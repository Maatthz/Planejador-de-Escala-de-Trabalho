"""Edição manual, validação e confirmação de escalas.

Permite realizar trocas de pessoas em plantões, validar quebras de regras,
listar sugestões de substitutos e gerenciar o histórico de escalas confirmadas.
"""

from collections import defaultdict

from src.escala.datas import formatar_data, formatar_dia_completo
from src.escala.gerador import descrever_plantao
from src.escala.modelos import DadosDoPrograma, ErroEscala, Escala, Pessoa


def trocar_pessoa(
    escala: Escala,
    indice_plantao: int,
    id_sai: int,
    id_entra: int,
    dados: DadosDoPrograma,
) -> list[str]:
    """Troca uma pessoa num plantão. Levanta ErroEscala se quebrar a regra 2 (mesmo dia).

    Retorna avisos (ex.: 'Ana marcou folga neste dia') sem bloquear — o usuário decide.
    """
    if indice_plantao < 0 or indice_plantao >= len(escala.plantoes):
        raise ErroEscala("Índice de plantão inválido.")

    plantao = escala.plantoes[indice_plantao]
    dupla_alvo = None
    for dupla in plantao.duplas:
        if dupla.contem(id_sai):
            dupla_alvo = dupla
            break

    if dupla_alvo is None:
        raise ErroEscala(f"Pessoa com ID {id_sai} não encontrada no plantão informado.")

    # Regra 2: ninguém pode trabalhar em dois plantões no mesmo dia
    escalados_no_dia = escala.pessoas_no_dia(plantao.data)
    if id_entra in escalados_no_dia:
        p_entra = dados.buscar_pessoa(id_entra)
        nome = p_entra.nome if p_entra else f"ID {id_entra}"
        raise ErroEscala(
            f"{nome} já está escalado(a) em outro plantão no dia {formatar_data(plantao.data)}."
        )

    # Realiza a substituição
    if dupla_alvo.pessoa_a == id_sai:
        dupla_alvo.pessoa_a = id_entra
    else:
        dupla_alvo.pessoa_b = id_entra

    # Coleta eventuais avisos não impeditivos
    avisos: list[str] = []
    p_entra = dados.buscar_pessoa(id_entra)
    if p_entra:
        if not p_entra.ativo:
            avisos.append(f"{p_entra.nome} está marcado(a) como inativo(a).")
        if plantao.data in p_entra.indisponibilidades:
            avisos.append(
                f"{p_entra.nome} marcou folga neste dia ({formatar_data(plantao.data)})."
            )

    return avisos


def validar_escala(escala: Escala, dados: DadosDoPrograma) -> list[str]:
    """Lista em português todas as regras quebradas na escala (vazia = tudo certo)."""
    avisos: list[str] = []

    # 1. Quantidade de duplas por plantão
    for plantao in escala.plantoes:
        if len(plantao.duplas) != plantao.qtd_duplas:
            desc = descrever_plantao(plantao)
            avisos.append(
                f"O plantão {desc} tem {len(plantao.duplas)} duplas, mas deveria ter {plantao.qtd_duplas}."
            )

    # 2. Mesma pessoa em mais de um plantão no mesmo dia
    por_dia: dict = defaultdict(list)
    for plantao in escala.plantoes:
        por_dia[plantao.data].extend(plantao.pessoas())

    for dia, ids in por_dia.items():
        vistos: set[int] = set()
        for id_pessoa in ids:
            if id_pessoa in vistos:
                pessoa = dados.buscar_pessoa(id_pessoa)
                nome = pessoa.nome if pessoa else f"ID {id_pessoa}"
                avisos.append(
                    f"{nome} está escalado(a) em mais de um plantão no dia {formatar_data(dia)}."
                )
            vistos.add(id_pessoa)

    # 3. Indisponibilidades, inativos e duplas proibidas
    for plantao in escala.plantoes:
        for dupla in plantao.duplas:
            par = frozenset([dupla.pessoa_a, dupla.pessoa_b])
            for proibido in dados.configuracao.nunca_juntos:
                if frozenset(proibido) == par:
                    p1 = dados.buscar_pessoa(dupla.pessoa_a)
                    p2 = dados.buscar_pessoa(dupla.pessoa_b)
                    n1 = p1.nome if p1 else str(dupla.pessoa_a)
                    n2 = p2.nome if p2 else str(dupla.pessoa_b)
                    desc = descrever_plantao(plantao)
                    avisos.append(
                        f"A dupla {n1} e {n2} no {desc} quebra a restrição de 'Nunca juntos'."
                    )

        for id_pessoa in plantao.pessoas():
            p = dados.buscar_pessoa(id_pessoa)
            if p:
                if not p.ativo:
                    desc = descrever_plantao(plantao)
                    avisos.append(
                        f"{p.nome} está inativo(a) mas está escalado(a) no {desc}."
                    )
                if plantao.data in p.indisponibilidades:
                    desc = descrever_plantao(plantao)
                    avisos.append(
                        f"{p.nome} está escalado(a) em dia de folga no {desc}."
                    )

    return avisos


def pessoas_para_troca(
    escala: Escala, indice_plantao: int, dados: DadosDoPrograma
) -> list[tuple[Pessoa, str]]:
    """Opções para o menu de troca: (pessoa, observação), ex.: (Bruno, 'já trabalha domingo')."""
    if indice_plantao < 0 or indice_plantao >= len(escala.plantoes):
        raise ErroEscala("Índice de plantão inválido.")

    plantao = escala.plantoes[indice_plantao]
    pessoas_do_plantao = plantao.pessoas()
    escalados_no_dia = escala.pessoas_no_dia(plantao.data)

    opcoes: list[tuple[Pessoa, str]] = []
    for pessoa in dados.pessoas_ativas():
        if pessoa.id in pessoas_do_plantao:
            continue

        observacao = ""
        if pessoa.id in escalados_no_dia:
            observacao = f"já trabalha no dia {formatar_data(plantao.data)}"
        elif plantao.data in pessoa.indisponibilidades:
            observacao = "marcou folga neste dia"
        else:
            outros_dias = [
                formatar_dia_completo(pl.data)
                for pl in escala.plantoes
                if pessoa.id in pl.pessoas() and pl.data != plantao.data
            ]
            if outros_dias:
                observacao = f"já trabalha em {', '.join(outros_dias)}"

        opcoes.append((pessoa, observacao))

    return opcoes


def escalas_sobrepostas(dados: DadosDoPrograma, escala: Escala) -> list[int]:
    """Índices das escalas confirmadas com datas em comum com `escala`."""
    datas_escala = {p.data for p in escala.plantoes}
    sobrepostas: list[int] = []

    for i, conf in enumerate(dados.escalas):
        datas_conf = {p.data for p in conf.plantoes}
        if datas_escala.intersection(datas_conf):
            sobrepostas.append(i)

    return sobrepostas


def confirmar_rascunho(dados: DadosDoPrograma) -> None:
    """Move o rascunho para o histórico (substituindo sobrepostas — a interface pergunta antes)."""
    if dados.rascunho is None:
        raise ErroEscala("Não há nenhum rascunho de escala para confirmar.")

    sobrepostas = escalas_sobrepostas(dados, dados.rascunho)
    for idx in sorted(sobrepostas, reverse=True):
        dados.escalas.pop(idx)

    dados.rascunho.confirmada = True
    dados.escalas.append(dados.rascunho)
    dados.rascunho = None


def excluir_escala(dados: DadosDoPrograma, indice: int) -> None:
    """Remove uma escala confirmada do histórico (a interface pede confirmação antes)."""
    if indice < 0 or indice >= len(dados.escalas):
        raise ErroEscala("Escala não encontrada no histórico.")
    dados.escalas.pop(indice)
