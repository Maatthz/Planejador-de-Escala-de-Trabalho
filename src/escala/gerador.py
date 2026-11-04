"""Algoritmo de geração da escala de plantão.

Implementa o algoritmo guloso com critérios ponderados de justiça,
duplas fixas, restrições rígidas e formação de duplas equilibradas.
"""

from collections import defaultdict
import copy
from datetime import date, datetime, timedelta
import random

from src.escala.datas import (
    DIAS_DA_SEMANA,
    chave_da_semana,
    dias_do_periodo,
    formatar_data,
    inicio_da_semana,
)
from src.escala.historico import (
    Contadores,
    aplicar_piso_semanal,
    calcular_contadores,
    registrar_plantao,
)
from src.escala.modelos import (
    Configuracao,
    DadosDoPrograma,
    Dupla,
    ErroEscala,
    Escala,
    Feriado,
    Pessoa,
    Plantao,
)


def descrever_plantao(plantao: Plantao) -> str:
    """Texto para mensagens. Ex.: 'sábado 07/11 (manhã)'."""
    dia_nome = DIAS_DA_SEMANA[plantao.data.weekday()].lower()
    return f"{dia_nome} {formatar_data(plantao.data)} ({plantao.periodo})"


def montar_plantoes_vazios(
    inicio: date,
    qtd_semanas: int,
    config: Configuracao,
    feriados: list[Feriado],
) -> list[Plantao]:
    """Cria os plantões (sem duplas) do período, já com feriados aplicados e em ordem."""
    dias = dias_do_periodo(inicio, qtd_semanas)
    feriados_por_data = {
        f.data: f for f in feriados
    } if config.feriados_ativos else {}
    ordem_periodo = {nome: i for i, nome in enumerate(config.periodos)}

    plantoes: list[Plantao] = []
    for dia in dias:
        if dia in feriados_por_data:
            feriado = feriados_por_data[dia]
            for periodo, qtd_duplas in feriado.periodos.items():
                plantoes.append(
                    Plantao(
                        data=dia,
                        periodo=periodo,
                        qtd_duplas=qtd_duplas,
                        eh_feriado=True,
                        nome_feriado=feriado.nome,
                    )
                )
        else:
            for turno in config.turnos:
                if turno.dia_da_semana == dia.weekday():
                    plantoes.append(
                        Plantao(
                            data=dia,
                            periodo=turno.periodo,
                            qtd_duplas=turno.qtd_duplas,
                            eh_feriado=False,
                            nome_feriado="",
                        )
                    )

    plantoes.sort(key=lambda p: (p.data, ordem_periodo.get(p.periodo, 999)))
    return plantoes


def listar_candidatos(
    plantao: Plantao, pessoas: list[Pessoa], escalados_no_dia: set[int]
) -> list[Pessoa]:
    """Pessoas ativas, disponíveis na data e ainda não escaladas nesse dia."""
    return [
        p
        for p in pessoas
        if p.ativo
        and plantao.data not in p.indisponibilidades
        and p.id not in escalados_no_dia
    ]


def chave_de_prioridade(
    pessoa: Pessoa,
    plantao: Plantao,
    contadores: Contadores,
    config: Configuracao,
    sorteio: random.Random,
) -> tuple:
    """Tupla de ordenação da seção 8.4 (menor = escolhido primeiro)."""
    semana_iso = chave_da_semana(plantao.data)
    ja_trabalha = 1 if semana_iso in contadores.semanas_trabalhadas.get(pessoa.id, set()) else 0
    carga = contadores.carga.get(pessoa.id, 0)
    feriados = contadores.feriados.get(pessoa.id, 0) if plantao.eh_feriado else 0

    if config.evitar_semanas_seguidas:
        segunda_anterior = inicio_da_semana(plantao.data) - timedelta(days=7)
        semana_anterior = chave_da_semana(segunda_anterior)
        trabalhou_anterior = 1 if semana_anterior in contadores.semanas_trabalhadas.get(pessoa.id, set()) else 0

        ult = contadores.ultimo_plantao.get(pessoa.id)
        dias_desde = 9999 if ult is None else (plantao.data - ult).days
        neg_dias = -dias_desde
    else:
        trabalhou_anterior = 0
        neg_dias = 0

    turno_chave = (pessoa.id, plantao.data.weekday(), plantao.periodo)
    vezes_turno = contadores.vezes_no_turno.get(turno_chave, 0)

    return (
        ja_trabalha,
        carga,
        feriados,
        trabalhou_anterior,
        neg_dias,
        vezes_turno,
        sorteio.random(),
    )


def custo_do_par(
    a: Pessoa, b: Pessoa, contadores: Contadores, config: Configuracao
) -> float:
    """Quanto pior a dupla, maior o custo. 'Nunca juntos' = infinito."""
    par = frozenset([a.id, b.id])
    for proibido in config.nunca_juntos:
        if frozenset(proibido) == par:
            return float("inf")

    custo = 0.0
    if config.modo_experiencia != "ignorar":
        if not a.experiente and not b.experiente:
            custo += 10.0

    custo += float(contadores.vezes_juntos.get(par, 0))
    return custo


def escolher_pessoas(
    candidatos: list[Pessoa],
    plantao: Plantao,
    contadores: Contadores,
    config: Configuracao,
    sorteio: random.Random,
) -> list[Pessoa]:
    """Escolhe 2 × qtd_duplas pessoas (prioridade, duplas fixas, modo de experiência)."""
    precisa = 2 * plantao.qtd_duplas
    if len(candidatos) < precisa:
        desc = descrever_plantao(plantao)
        raise ErroEscala(
            f"Não há pessoas suficientes no {desc}: precisa de {precisa}, há {len(candidatos)}."
        )

    ordenados = sorted(
        candidatos,
        key=lambda p: chave_de_prioridade(p, plantao, contadores, config, sorteio),
    )
    candidatos_por_id = {p.id: p for p in candidatos}

    par_fixo = {}
    for a, b in config.sempre_juntos:
        par_fixo[a] = b
        par_fixo[b] = a

    escolhidas: list[Pessoa] = []
    escolhidas_ids: set[int] = set()

    for cand in ordenados:
        if cand.id in escolhidas_ids:
            continue
        vagas = precisa - len(escolhidas)
        if vagas <= 0:
            break

        outro_id = par_fixo.get(cand.id)
        if outro_id is not None and outro_id in candidatos_por_id and outro_id not in escolhidas_ids:
            if vagas >= 2:
                escolhidas.append(cand)
                escolhidas_ids.add(cand.id)
                parceiro = candidatos_por_id[outro_id]
                escolhidas.append(parceiro)
                escolhidas_ids.add(parceiro.id)
            else:
                continue
        else:
            escolhidas.append(cand)
            escolhidas_ids.add(cand.id)

    if len(escolhidas) < precisa:
        for cand in ordenados:
            if cand.id not in escolhidas_ids:
                escolhidas.append(cand)
                escolhidas_ids.add(cand.id)
                if len(escolhidas) == precisa:
                    break

    if config.modo_experiencia == "obrigatoria":
        _garantir_experiencia_obrigatoria(
            escolhidas, ordenados, plantao, precisa
        )

    return escolhidas


def _garantir_experiencia_obrigatoria(
    escolhidas: list[Pessoa],
    ordenados: list[Pessoa],
    plantao: Plantao,
    precisa: int,
) -> None:
    """Garante que haja no mínimo qtd_duplas experientes substituindo os de menor prioridade."""
    qtd_exp = sum(1 for p in escolhidas if p.experiente)
    if qtd_exp < plantao.qtd_duplas:
        escolhidas_ids = {p.id for p in escolhidas}
        exp_sobrando = [
            p for p in ordenados if p.experiente and p.id not in escolhidas_ids
        ]
        falta = plantao.qtd_duplas - qtd_exp
        if len(exp_sobrando) < falta:
            desc = descrever_plantao(plantao)
            total_disp = qtd_exp + len(exp_sobrando)
            raise ErroEscala(
                f"Não há pessoas experientes suficientes no {desc} para cumprir a regra obrigatória "
                f"(precisa de {plantao.qtd_duplas}, há {total_disp}). "
                f"Considere alterar a opção de experiência para 'Preferência' em Configurações."
            )

        nao_exp_escolhidas = [
            p for p in reversed(ordenados) if p.id in escolhidas_ids and not p.experiente
        ]
        for i in range(falta):
            sai = nao_exp_escolhidas[i]
            entra = exp_sobrando[i]
            idx = escolhidas.index(sai)
            escolhidas[idx] = entra
            escolhidas_ids.remove(sai.id)
            escolhidas_ids.add(entra.id)


def formar_duplas(
    escolhidas: list[Pessoa], contadores: Contadores, config: Configuracao
) -> list[Dupla]:
    """Forma as duplas minimizando o custo (seção 8.4, passo 6)."""
    disponiveis = list(escolhidas)
    duplas: list[Dupla] = []

    # 1. Duplas fixas primeiro
    for a, b in config.sempre_juntos:
        p_a = next((p for p in disponiveis if p.id == a), None)
        p_b = next((p for p in disponiveis if p.id == b), None)
        if p_a and p_b:
            duplas.append(Dupla(p_a.id, p_b.id))
            disponiveis.remove(p_a)
            disponiveis.remove(p_b)

    # 2. Experiente com não experiente (se modo != "ignorar")
    if config.modo_experiencia != "ignorar":
        experientes = [p for p in disponiveis if p.experiente]
        nao_exp = [p for p in disponiveis if not p.experiente]
        while experientes and nao_exp:
            exp = experientes.pop(0)
            melhor_nao_exp = min(
                nao_exp,
                key=lambda n: custo_do_par(exp, n, contadores, config),
            )
            if custo_do_par(exp, melhor_nao_exp, contadores, config) == float("inf"):
                experientes.insert(0, exp)
                break
            duplas.append(Dupla(exp.id, melhor_nao_exp.id))
            disponiveis.remove(exp)
            disponiveis.remove(melhor_nao_exp)
            nao_exp.remove(melhor_nao_exp)

    # 3. Restantes
    while len(disponiveis) >= 2:
        melhor_custo = float("inf")
        melhor_par = None
        for i in range(len(disponiveis)):
            for j in range(i + 1, len(disponiveis)):
                c = custo_do_par(disponiveis[i], disponiveis[j], contadores, config)
                if c < melhor_custo:
                    melhor_custo = c
                    melhor_par = (disponiveis[i], disponiveis[j])

        if melhor_par is None or melhor_custo == float("inf"):
            raise ErroEscala(
                "Não foi possível formar as duplas respeitando a restrição de 'Nunca juntos'. "
                "Verifique os pares proibidos em Configurações."
            )

        p1, p2 = melhor_par
        duplas.append(Dupla(p1.id, p2.id))
        disponiveis.remove(p1)
        disponiveis.remove(p2)

    return duplas


def gerar_escala(
    dados: DadosDoPrograma,
    inicio: date,
    qtd_semanas: int,
    semente: int | None = None,
) -> Escala:
    """Gera um rascunho de escala para o período. Levanta ErroEscala com mensagem amigável."""
    plantoes = montar_plantoes_vazios(
        inicio, qtd_semanas, dados.configuracao, dados.feriados
    )
    if not plantoes:
        raise ErroEscala("Não há plantões configurados para as datas selecionadas.")

    contadores = copy.deepcopy(calcular_contadores(dados))
    sorteio = random.Random(semente)

    escalados_no_dia: dict[date, set[int]] = defaultdict(set)
    semana_atual = None
    dias_semana_atual: list[date] = []

    for plantao in plantoes:
        segunda = inicio_da_semana(plantao.data)
        if semana_atual is not None and segunda != semana_atual:
            aplicar_piso_semanal(contadores, dias_semana_atual, dados)
            dias_semana_atual = []
        semana_atual = segunda
        dias_semana_atual.append(plantao.data)

        candidatos = listar_candidatos(
            plantao, dados.pessoas, escalados_no_dia[plantao.data]
        )
        escolhidas = escolher_pessoas(
            candidatos, plantao, contadores, dados.configuracao, sorteio
        )
        duplas = formar_duplas(escolhidas, contadores, dados.configuracao)

        plantao.duplas = duplas
        escalados_no_dia[plantao.data].update(plantao.pessoas())
        registrar_plantao(contadores, plantao)

    if dias_semana_atual:
        aplicar_piso_semanal(contadores, dias_semana_atual, dados)

    escala = Escala(
        plantoes=plantoes,
        gerada_em=datetime.now(),
        confirmada=False,
    )
    dados.rascunho = escala
    return escala
