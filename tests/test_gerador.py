"""Testes para o algoritmo do gerador de escalas."""

from collections import Counter
from datetime import date
import pytest

from src.escala.gerador import gerar_escala, montar_plantoes_vazios
from src.escala.modelos import DadosDoPrograma, ErroEscala, Feriado


def test_gerador_quantidade_de_duplas_correta(dados_padrao: DadosDoPrograma) -> None:
    """Cada plantão gerado deve ter exatamente o número de duplas configurado."""
    inicio = date(2026, 11, 2)
    escala = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=1, semente=42)

    assert len(escala.plantoes) == 2
    for plantao in escala.plantoes:
        assert len(plantao.duplas) == 4
        assert len(plantao.pessoas()) == 8


def test_gerador_ninguem_duas_vezes_no_mesmo_dia(dados_padrao: DadosDoPrograma) -> None:
    """Nenhuma pessoa pode ser escalada em dois plantões na mesma data."""
    # Adiciona mais um turno no sábado à tarde
    from src.escala.modelos import ModeloDeTurno
    dados_padrao.configuracao.turnos.append(ModeloDeTurno(5, "tarde", 2))

    inicio = date(2026, 11, 2)
    escala = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=1, semente=42)

    sabado = date(2026, 11, 7)
    escalados_sabado = []
    for plantao in escala.plantoes:
        if plantao.data == sabado:
            for pid in plantao.pessoas():
                escalados_sabado.append(pid)

    assert len(escalados_sabado) == len(set(escalados_sabado))


def test_gerador_indisponiveis_e_inativos_nunca_escalados(dados_padrao: DadosDoPrograma) -> None:
    """Pessoas inativas ou com folga na data do plantão nunca são escaladas."""
    p1 = dados_padrao.buscar_pessoa(1)
    p2 = dados_padrao.buscar_pessoa(2)

    p1.ativo = False
    p2.indisponibilidades.add(date(2026, 11, 7))
    p2.indisponibilidades.add(date(2026, 11, 8))

    inicio = date(2026, 11, 2)
    escala = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=1, semente=42)

    todos_escalados = set()
    for plantao in escala.plantoes:
        todos_escalados.update(plantao.pessoas())

    assert 1 not in todos_escalados
    assert 2 not in todos_escalados


def test_gerador_sete_semanas_no_padrao_distribui_quatro_plantoes(dados_padrao: DadosDoPrograma) -> None:
    """Em 7 semanas no padrão (112 vagas / 28 pessoas), todos devem ter exatamente 4 plantões."""
    inicio = date(2026, 11, 2)
    escala = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=7, semente=42)

    contagem = Counter()
    for plantao in escala.plantoes:
        for pid in plantao.pessoas():
            contagem[pid] += 1

    assert len(contagem) == 28
    for pid in range(1, 29):
        assert contagem[pid] == 4, f"Pessoa {pid} trabalhou {contagem[pid]} vezes (esperado 4)"


def test_gerador_semana_com_feriado_ninguem_repete_semana(dados_padrao: DadosDoPrograma) -> None:
    """Em semana com 24 vagas (16 fim de semana + 8 feriado <= 28), ninguém deve trabalhar 2 vezes."""
    dados_padrao.feriados.append(
        Feriado(data=date(2026, 11, 6), nome="Feriado Sexta", periodos={"manhã": 4})
    )
    inicio = date(2026, 11, 2)
    escala = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=1, semente=42)

    contagem = Counter()
    for plantao in escala.plantoes:
        for pid in plantao.pessoas():
            contagem[pid] += 1

    for pid, qtd in contagem.items():
        assert qtd == 1, f"Pessoa {pid} trabalhou {qtd} vezes na mesma semana"


def test_gerador_feriado_no_sabado_substitui_turnos_do_sabado(dados_padrao: DadosDoPrograma) -> None:
    """Feriado que cai no sábado substitui os turnos habituais do sábado."""
    sabado = date(2026, 11, 7)
    dados_padrao.feriados.append(
        Feriado(data=sabado, nome="Feriado Sabadão", periodos={"tarde": 2})
    )

    plantoes = montar_plantoes_vazios(
        inicio=date(2026, 11, 2),
        qtd_semanas=1,
        config=dados_padrao.configuracao,
        feriados=dados_padrao.feriados,
    )

    plantoes_sabado = [p for p in plantoes if p.data == sabado]
    assert len(plantoes_sabado) == 1
    assert plantoes_sabado[0].periodo == "tarde"
    assert plantoes_sabado[0].qtd_duplas == 2
    assert plantoes_sabado[0].eh_feriado is True


def test_gerador_preferencia_experiencia_distribui_experiente_por_dupla(
    dados_padrao: DadosDoPrograma,
) -> None:
    """Com modo 'preferencia' e experientes suficientes entre os escolhidos, toda dupla tem ao menos 1 experiente."""
    from src.escala.gerador import formar_duplas
    from src.escala.historico import calcular_contadores
    from src.escala.modelos import Pessoa

    # 4 experientes e 4 não experientes escolhidos para um plantão de 4 duplas
    escolhidas = [
        Pessoa(id=1, nome="Exp 1", experiente=True),
        Pessoa(id=2, nome="Exp 2", experiente=True),
        Pessoa(id=3, nome="Exp 3", experiente=True),
        Pessoa(id=4, nome="Exp 4", experiente=True),
        Pessoa(id=5, nome="Nov 1", experiente=False),
        Pessoa(id=6, nome="Nov 2", experiente=False),
        Pessoa(id=7, nome="Nov 3", experiente=False),
        Pessoa(id=8, nome="Nov 4", experiente=False),
    ]
    contadores = calcular_contadores(dados_padrao)
    duplas = formar_duplas(escolhidas, contadores, dados_padrao.configuracao)

    assert len(duplas) == 4
    pessoas_map = {p.id: p for p in escolhidas}
    for dupla in duplas:
        p_a = pessoas_map[dupla.pessoa_a]
        p_b = pessoas_map[dupla.pessoa_b]
        assert (p_a.experiente or p_b.experiente) is True


def test_gerador_modo_obrigatoria_garante_ou_falha(dados_padrao: DadosDoPrograma) -> None:
    """Modo 'obrigatoria' garante 1 experiente por dupla; se impossível, levanta ErroEscala."""
    dados_padrao.configuracao.modo_experiencia = "obrigatoria"
    # Mantém apenas 2 experientes ativos no total, mas precisa de 4 duplas no sábado
    for p in dados_padrao.pessoas[2:]:
        p.experiente = False

    inicio = date(2026, 11, 2)
    with pytest.raises(ErroEscala, match="regra obrigatória"):
        gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=1, semente=42)


def test_gerador_respeita_nunca_juntos(dados_padrao: DadosDoPrograma) -> None:
    """Pessoas na restrição 'nunca_juntos' nunca são colocadas na mesma dupla."""
    dados_padrao.configuracao.nunca_juntos = [(1, 2)]

    inicio = date(2026, 11, 2)
    escala = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=3, semente=10)

    for plantao in escala.plantoes:
        for dupla in plantao.duplas:
            par = frozenset([dupla.pessoa_a, dupla.pessoa_b])
            assert par != frozenset([1, 2])


def test_gerador_duplas_fixas_ficam_juntas_quando_disponiveis(
    dados_padrao: DadosDoPrograma,
) -> None:
    """Pessoas em duplas fixas (sempre_juntos) trabalham juntas quando ambas disponíveis."""
    dados_padrao.configuracao.sempre_juntos = [(1, 2)]

    inicio = date(2026, 11, 2)
    escala = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=1, semente=42)

    encontrou_dupla = False
    for plantao in escala.plantoes:
        for dupla in plantao.duplas:
            if frozenset([dupla.pessoa_a, dupla.pessoa_b]) == frozenset([1, 2]):
                encontrou_dupla = True
                break

    assert encontrou_dupla is True


def test_gerador_falta_de_gente_mensagem_exata(dados_padrao: DadosDoPrograma) -> None:
    """Falta de pessoas disponíveis deve levantar mensagem amigável no formato exato."""
    # Deixa apenas 6 pessoas disponíveis no sábado 07/11 (precisa de 8 = 4 duplas)
    sabado = date(2026, 11, 7)
    for p in dados_padrao.pessoas[6:]:
        p.indisponibilidades.add(sabado)

    inicio = date(2026, 11, 2)
    with pytest.raises(
        ErroEscala,
        match="Não há pessoas suficientes no sábado 07/11 \\(manhã\\): precisa de 8, há 6\\.",
    ):
        gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=1, semente=42)


def test_gerador_mesma_semente_mesma_escala(dados_padrao: DadosDoPrograma) -> None:
    """O algoritmo deve ser determinístico: mesma semente produz exatamente a mesma escala."""
    inicio = date(2026, 11, 2)
    escala1 = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=2, semente=123)
    escala2 = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=2, semente=123)

    for p1, p2 in zip(escala1.plantoes, escala2.plantoes):
        assert p1.data == p2.data
        assert p1.periodo == p2.periodo
        for d1, d2 in zip(p1.duplas, p2.duplas):
            assert d1.ids() == d2.ids()
