"""Testes para o módulo de datas."""

from datetime import date
import pytest

from src.escala.datas import (
    chave_da_semana,
    dias_do_periodo,
    formatar_data,
    formatar_dia_completo,
    inicio_da_semana,
    ler_data,
)
from src.escala.modelos import ErroEscala


def test_inicio_da_semana() -> None:
    """inicio_da_semana deve retornar sempre a segunda-feira da mesma semana."""
    # 07/11/2026 é sábado; a segunda foi 02/11/2026
    sabado = date(2026, 11, 7)
    assert inicio_da_semana(sabado) == date(2026, 11, 2)

    # 02/11/2026 é segunda; o início é a própria data
    segunda = date(2026, 11, 2)
    assert inicio_da_semana(segunda) == date(2026, 11, 2)

    # 08/11/2026 é domingo; a segunda foi 02/11/2026
    domingo = date(2026, 11, 8)
    assert inicio_da_semana(domingo) == date(2026, 11, 2)


def test_chave_da_semana() -> None:
    """chave_da_semana deve retornar (ano, numero_da_semana) segundo o padrão ISO."""
    # 07/11/2026 está na semana 45 de 2026
    sabado = date(2026, 11, 7)
    assert chave_da_semana(sabado) == (2026, 45)


def test_dias_do_periodo() -> None:
    """dias_do_periodo deve gerar todos os dias corridos de N semanas a partir da segunda-feira."""
    quarta = date(2026, 11, 4)
    dias = dias_do_periodo(quarta, qtd_semanas=2)

    assert len(dias) == 14
    assert dias[0] == date(2026, 11, 2)  # segunda-feira
    assert dias[-1] == date(2026, 11, 15)  # domingo da 2ª semana


def test_formatar_data() -> None:
    """formatar_data deve retornar 'DD/MM'."""
    assert formatar_data(date(2026, 11, 7)) == "07/11"
    assert formatar_data(date(2026, 1, 5)) == "05/01"


def test_formatar_dia_completo() -> None:
    """formatar_dia_completo deve retornar 'NomeDoDia, DD/MM'."""
    sabado = date(2026, 11, 7)
    assert formatar_dia_completo(sabado) == "Sábado, 07/11"

    domingo = date(2026, 11, 8)
    assert formatar_dia_completo(domingo) == "Domingo, 08/11"

    segunda = date(2026, 11, 2)
    assert formatar_dia_completo(segunda) == "Segunda, 02/11"


def test_ler_data_valida() -> None:
    """ler_data deve converter corretamente 'dd/mm/aaaa' em date."""
    assert ler_data("07/11/2026") == date(2026, 11, 7)
    assert ler_data(" 25/12/2026 ") == date(2026, 12, 25)


@pytest.mark.parametrize(
    "texto_invalido",
    [
        "",
        "texto",
        "07-11-2026",
        "07/11/26",
        "32/01/2026",
        "29/02/2026",  # 2026 não é bissexto
        "07/13/2026",
        "07/11/2026/01",
    ],
)
def test_ler_data_invalida_levanta_erro(texto_invalido: str) -> None:
    """ler_data deve levantar ErroEscala com mensagem amigável para qualquer formato inválido."""
    with pytest.raises(ErroEscala, match="Data inválida: use o formato 25/12/2026."):
        ler_data(texto_invalido)
