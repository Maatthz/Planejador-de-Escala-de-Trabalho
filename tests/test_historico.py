"""Testes para o módulo de histórico e contadores de justiça."""

from datetime import date, datetime
import pytest

from src.escala.historico import (
    calcular_contadores,
    esta_presente,
    quadro_de_justica,
)
from src.escala.modelos import (
    Configuracao,
    DadosDoPrograma,
    Dupla,
    Escala,
    Plantao,
)


def test_rascunho_nao_conta_nos_contadores(dados_padrao: DadosDoPrograma) -> None:
    """Escalas que são apenas rascunho (confirmada=False) não alteram os contadores."""
    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    dados_padrao.rascunho = Escala(
        plantoes=[plantao], gerada_em=datetime.now(), confirmada=False
    )

    contadores = calcular_contadores(dados_padrao)
    assert contadores.carga[1] == 0
    assert contadores.carga[2] == 0


def test_editar_escala_confirmada_muda_contadores(dados_padrao: DadosDoPrograma) -> None:
    """Editar diretamente as duplas de uma escala confirmada recalcula os contadores dinamicamente."""
    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    escala = Escala(plantoes=[plantao], gerada_em=datetime.now(), confirmada=True)
    dados_padrao.escalas.append(escala)

    contadores1 = calcular_contadores(dados_padrao)
    assert contadores1.carga[1] >= 1
    assert contadores1.carga[2] >= 1
    assert contadores1.carga[3] == 0

    # Troca a pessoa 2 pela pessoa 3
    plantao.duplas[0] = Dupla(1, 3)
    contadores2 = calcular_contadores(dados_padrao)
    assert contadores2.carga[2] == 0
    assert contadores2.carga[3] >= 1


def test_pessoa_nova_entra_com_a_menor_carga(dados_padrao: DadosDoPrograma) -> None:
    """Uma pessoa cadastrada após várias semanas entra com a menor carga entre os presentes."""
    # Semana 1: sábado 07/11 (pessoas 1 e 2 trabalham)
    p1 = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    dados_padrao.escalas.append(
        Escala(plantoes=[p1], gerada_em=datetime.now(), confirmada=True)
    )

    # Nova pessoa entra com data de entrada em 15/11/2026 (semana seguinte)
    nova = dados_padrao.adicionar_pessoa("Novata")
    nova.data_entrada = date(2026, 11, 15)

    contadores = calcular_contadores(dados_padrao)
    # A menor carga entre os presentes na semana do dia 07/11 foi 0 (as outras 26 pessoas não trabalharam)
    # Vamos criar uma situação onde TODOS os presentes trabalharam:
    dados_padrao.pessoas = [
        dados_padrao.buscar_pessoa(1),
        dados_padrao.buscar_pessoa(2),
        nova,
    ]
    # Agora apenas 1 e 2 estavam presentes na semana de 07/11 e ambos trabalharam (carga 1).
    # A menor carga entre os presentes foi 1.
    contadores_reduzidos = calcular_contadores(dados_padrao)
    assert contadores_reduzidos.carga[nova.id] == 1


def test_volta_de_ferias_entra_empatada_com_menor_carga(dados_padrao: DadosDoPrograma) -> None:
    """Quem esteve indisponível na semana inteira (férias) recebe o piso da menor carga entre presentes."""
    p1 = dados_padrao.buscar_pessoa(1)
    p2 = dados_padrao.buscar_pessoa(2)
    p3 = dados_padrao.buscar_pessoa(3)
    dados_padrao.pessoas = [p1, p2, p3]

    # p3 tira férias no sábado 07/11
    p3.indisponibilidades.add(date(2026, 11, 7))

    # Plantão com p1 e p2
    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    dados_padrao.escalas.append(
        Escala(plantoes=[plantao], gerada_em=datetime.now(), confirmada=True)
    )

    contadores = calcular_contadores(dados_padrao)
    # Como p1 e p2 trabalharam (carga 1 cada), a menor carga entre presentes foi 1.
    # Por padrão (não compensar ausências), p3 recebe o piso 1!
    assert contadores.carga[p3.id] == 1


def test_compensar_ausencias_mantem_carga_baixa(dados_padrao: DadosDoPrograma) -> None:
    """Com compensar_ausencias=True, a pessoa de férias não sobe para o piso (fica 'devendo')."""
    dados_padrao.configuracao.compensar_ausencias = True

    p1 = dados_padrao.buscar_pessoa(1)
    p2 = dados_padrao.buscar_pessoa(2)
    p3 = dados_padrao.buscar_pessoa(3)
    dados_padrao.pessoas = [p1, p2, p3]

    p3.indisponibilidades.add(date(2026, 11, 7))

    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    dados_padrao.escalas.append(
        Escala(plantoes=[plantao], gerada_em=datetime.now(), confirmada=True)
    )

    contadores = calcular_contadores(dados_padrao)
    # Com compensar_ausencias=True, p3 mantém carga 0 (deve o plantão)
    assert contadores.carga[p3.id] == 0


def test_quadro_de_justica_ordena_e_distingue_reais_de_justica(dados_padrao: DadosDoPrograma) -> None:
    """quadro_de_justica lista os que trabalharam menos primeiro e distingue plantoes_reais de carga_justica."""
    p1 = dados_padrao.buscar_pessoa(1)
    p2 = dados_padrao.buscar_pessoa(2)
    p3 = dados_padrao.buscar_pessoa(3)
    dados_padrao.pessoas = [p1, p2, p3]

    p3.indisponibilidades.add(date(2026, 11, 7))

    # p1 e p2 trabalham
    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    dados_padrao.escalas.append(
        Escala(plantoes=[plantao], gerada_em=datetime.now(), confirmada=True)
    )

    quadro = quadro_de_justica(dados_padrao)
    assert len(quadro) == 3

    # Para p3: não trabalhou nenhum plantão real, mas tem carga_justica 1 por causa do piso
    resumo_p3 = next(r for r in quadro if r.pessoa.id == 3)
    assert resumo_p3.plantoes_reais == 0
    assert resumo_p3.carga_justica == 1
    assert resumo_p3.ultimo_plantao is None


def test_ajustar_contadores_pessoa_manual_e_soma_automatica(
    dados_padrao: DadosDoPrograma, pasta_temporaria
) -> None:
    """Preencher o Quadro de Justiça manualmente ordena a fila e soma novas escalas confirmadas."""
    from src.escala.armazenamento import carregar, salvar
    from src.escala.historico import ajustar_contadores_pessoa

    dados_padrao.pessoas = dados_padrao.pessoas[:3]
    p1, p2, p3 = dados_padrao.pessoas

    # Define valores iniciais diferentes para cada pessoa (escala já em andamento)
    ajustar_contadores_pessoa(dados_padrao, p1.id, 5, 2, date(2026, 10, 31))
    ajustar_contadores_pessoa(dados_padrao, p2.id, 3, 1, date(2026, 10, 24))
    ajustar_contadores_pessoa(dados_padrao, p3.id, 4, 0, None)

    salvar(dados_padrao, pasta_temporaria)
    recarregado, _ = carregar(pasta_temporaria)

    quadro = quadro_de_justica(recarregado)
    # Ordem de prioridade: p2 (3) -> p3 (4) -> p1 (5)
    assert [r.pessoa.id for r in quadro] == [p2.id, p3.id, p1.id]
    assert quadro[0].plantoes_reais == 3
    assert quadro[0].feriados_trabalhados == 1
    assert quadro[0].ultimo_plantao == date(2026, 10, 24)

    # Quando uma nova escala é confirmada com p2 e p3 trabalhando em feriado:
    plantao_novo = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        eh_feriado=True,
        duplas=[Dupla(p2.id, p3.id)],
    )
    recarregado.escalas.append(
        Escala(plantoes=[plantao_novo], gerada_em=datetime.now(), confirmada=True)
    )

    quadro_pos = quadro_de_justica(recarregado)
    res_p2 = next(r for r in quadro_pos if r.pessoa.id == p2.id)
    assert res_p2.plantoes_reais == 4
    assert res_p2.carga_justica == 4
    assert res_p2.feriados_trabalhados == 2
    assert res_p2.ultimo_plantao == date(2026, 11, 7)
