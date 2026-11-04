"""Contadores de justiça e histórico do Planejador de Escala.

Recalcula contadores a partir de escalas confirmadas (fonte única da verdade),
aplicando a regra do piso para novas entradas e retornos de ausências.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from src.escala.datas import chave_da_semana, inicio_da_semana
from src.escala.modelos import Configuracao, DadosDoPrograma, Pessoa, Plantao


@dataclass
class Contadores:
    """Números usados para decidir quem trabalha. Sempre derivados das escalas confirmadas."""

    carga: dict[int, int]
    feriados: dict[int, int]
    ultimo_plantao: dict[int, date]
    vezes_juntos: dict[frozenset[int], int]
    vezes_no_turno: dict[tuple[int, int, str], int]  # (id, dia_da_semana, periodo)
    semanas_trabalhadas: dict[int, set[tuple[int, int]]]  # id -> chaves de semana


@dataclass
class ResumoJustica:
    """Linha do quadro de justiça para mostrar ao usuário."""

    posicao: int  # 1 = primeiro da fila (maior prioridade)
    pessoa: Pessoa
    plantoes_reais: int  # quantos plantões realmente fez nas escalas confirmadas
    carga_justica: int  # contador usado pelo algoritmo (inclui o piso de entrada/férias)
    feriados_trabalhados: int  # quantos feriados realmente trabalhou
    ultimo_plantao: date | None  # data do último plantão confirmado (ou None)


def registrar_plantao(contadores: Contadores, plantao: Plantao) -> None:
    """Soma um plantão aos contadores (usado no histórico e durante a geração)."""
    for dupla in plantao.duplas:
        par = frozenset([dupla.pessoa_a, dupla.pessoa_b])
        contadores.vezes_juntos[par] = contadores.vezes_juntos.get(par, 0) + 1

    semana_iso = chave_da_semana(plantao.data)
    for id_pessoa in plantao.pessoas():
        contadores.carga[id_pessoa] = contadores.carga.get(id_pessoa, 0) + 1
        if plantao.eh_feriado:
            contadores.feriados[id_pessoa] = contadores.feriados.get(id_pessoa, 0) + 1

        contadores.ultimo_plantao[id_pessoa] = plantao.data

        chave_turno = (id_pessoa, plantao.data.weekday(), plantao.periodo)
        contadores.vezes_no_turno[chave_turno] = (
            contadores.vezes_no_turno.get(chave_turno, 0) + 1
        )

        if id_pessoa not in contadores.semanas_trabalhadas:
            contadores.semanas_trabalhadas[id_pessoa] = set()
        contadores.semanas_trabalhadas[id_pessoa].add(semana_iso)


def esta_presente(
    pessoa: Pessoa, dias_com_plantao: list[date], config: Configuracao
) -> bool:
    """Diz se a pessoa conta como presente na semana (regra da seção 8.1/8.3)."""
    if not dias_com_plantao:
        return True

    segunda = inicio_da_semana(dias_com_plantao[0])
    domingo = segunda + timedelta(days=6)

    # Pessoa que entrou depois da semana sempre é ausente (não herda dívida)
    if pessoa.data_entrada > domingo:
        return False

    # Com compensação ligada, indisponibilidade não a torna ausente (ela deve o plantão)
    if config.compensar_ausencias:
        return True

    # Padrão: presente se estiver disponível em pelo menos um plantão da semana
    return any(dia not in pessoa.indisponibilidades for dia in dias_com_plantao)


def aplicar_piso_semanal(
    contadores: Contadores, dias_com_plantao: list[date], dados: DadosDoPrograma
) -> None:
    """Aplica o piso de ausência ao fim de uma semana com plantões."""
    if not dias_com_plantao:
        return

    presentes = [
        p
        for p in dados.pessoas
        if esta_presente(p, dias_com_plantao, dados.configuracao)
    ]

    if presentes:
        menor_carga = min(contadores.carga[p.id] for p in presentes)
        menor_feriados = min(contadores.feriados[p.id] for p in presentes)

        for p in dados.pessoas:
            if not esta_presente(p, dias_com_plantao, dados.configuracao):
                contadores.carga[p.id] = max(contadores.carga[p.id], menor_carga)
                contadores.feriados[p.id] = max(
                    contadores.feriados[p.id], menor_feriados
                )


def calcular_contadores(dados: DadosDoPrograma) -> Contadores:
    """Reprocessa as escalas confirmadas em ordem e aplica o piso de ausências (seção 8.3)."""
    contadores = Contadores(
        carga={p.id: 0 for p in dados.pessoas},
        feriados={p.id: 0 for p in dados.pessoas},
        ultimo_plantao={},
        vezes_juntos=defaultdict(int),
        vezes_no_turno=defaultdict(int),
        semanas_trabalhadas=defaultdict(set),
    )

    # Coleta todos os plantões de escalas confirmadas
    plantoes_confirmados: list[Plantao] = []
    for escala in dados.escalas:
        if escala.confirmada:
            plantoes_confirmados.extend(escala.plantoes)

    if not plantoes_confirmados:
        return contadores

    # Agrupa plantões por semana cronológica
    plantoes_por_semana: dict[date, list[Plantao]] = defaultdict(list)
    for plantao in plantoes_confirmados:
        segunda = inicio_da_semana(plantao.data)
        plantoes_por_semana[segunda].append(plantao)

    for segunda in sorted(plantoes_por_semana.keys()):
        plantoes_da_semana = plantoes_por_semana[segunda]
        dias_com_plantao = [p.data for p in plantoes_da_semana]

        # 1. Registra os plantões da semana
        for plantao in plantoes_da_semana:
            registrar_plantao(contadores, plantao)

        # 2. Aplica o piso de ausência ao fim da semana
        aplicar_piso_semanal(contadores, dias_com_plantao, dados)

    return contadores


def quadro_de_justica(dados: DadosDoPrograma) -> list[ResumoJustica]:
    """Retorna as pessoas ativas ordenadas por prioridade (quem está na frente da fila vem primeiro)."""
    contadores = calcular_contadores(dados)

    # Contagem real direta (sem a elevação de piso)
    plantoes_reais: dict[int, int] = {p.id: 0 for p in dados.pessoas}
    feriados_reais: dict[int, int] = {p.id: 0 for p in dados.pessoas}

    for escala in dados.escalas:
        if escala.confirmada:
            for plantao in escala.plantoes:
                for id_pessoa in plantao.pessoas():
                    plantoes_reais[id_pessoa] = plantoes_reais.get(id_pessoa, 0) + 1
                    if plantao.eh_feriado:
                        feriados_reais[id_pessoa] = (
                            feriados_reais.get(id_pessoa, 0) + 1
                        )

    ativas = dados.pessoas_ativas()

    # Ordenação da fila de prioridade:
    # 1. Menor carga de justiça
    # 2. Menor plantões em feriados
    # 3. Mais tempo sem trabalhar (nunca trabalhou vem primeiro)
    # 4. Nome alfabético
    def chave_fila(p: Pessoa) -> tuple:
        carga = contadores.carga.get(p.id, 0)
        feriados = contadores.feriados.get(p.id, 0)
        ult = contadores.ultimo_plantao.get(p.id, date.min)
        return (carga, feriados, ult, p.nome.lower())

    ordenadas = sorted(ativas, key=chave_fila)

    resumo: list[ResumoJustica] = []
    for posicao, pessoa in enumerate(ordenadas, start=1):
        resumo.append(
            ResumoJustica(
                posicao=posicao,
                pessoa=pessoa,
                plantoes_reais=plantoes_reais.get(pessoa.id, 0),
                carga_justica=contadores.carga.get(pessoa.id, 0),
                feriados_trabalhados=feriados_reais.get(pessoa.id, 0),
                ultimo_plantao=contadores.ultimo_plantao.get(pessoa.id),
            )
        )

    return resumo
