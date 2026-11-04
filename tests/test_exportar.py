"""Testes para o módulo de exportação para WhatsApp."""

from datetime import date, datetime
import pytest

from src.escala.exportar import gerar_texto_whatsapp
from src.escala.modelos import (
    DadosDoPrograma,
    Dupla,
    Escala,
    Plantao,
)


def test_gerar_texto_whatsapp_formato_padrao(dados_padrao: DadosDoPrograma) -> None:
    """O texto gerado deve corresponder exatamente ao formato especificado na seção 10.6."""
    p1 = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=4,
        duplas=[
            Dupla(1, 2),  # Ana e Bruno
            Dupla(3, 4),  # Carla e Diego
            Dupla(5, 6),  # Elisa e Fábio
            Dupla(7, 8),  # Gabi e Hugo
        ],
    )
    escala = Escala(plantoes=[p1], gerada_em=datetime.now(), confirmada=True)

    texto = gerar_texto_whatsapp(escala, dados_padrao)

    esperado = (
        "📋 *ESCALA DE PLANTÃO*\n\n"
        "📅 *Sábado, 07/11 — Manhã*\n"
        "1. Ana e Bruno\n"
        "2. Carla e Diego\n"
        "3. Elisa e Fábio\n"
        "4. Gabi e Hugo"
    )

    assert texto == esperado


def test_gerar_texto_whatsapp_com_feriado_e_texto_final(
    dados_padrao: DadosDoPrograma,
) -> None:
    """Verifica a inclusão da tag de feriado no cabeçalho e do texto final configurado."""
    dados_padrao.configuracao.texto_final_mensagem = "Trocas: falar com a coordenação."

    p_normal = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    p_feriado = Plantao(
        data=date(2026, 11, 20),
        periodo="manhã",
        qtd_duplas=1,
        eh_feriado=True,
        nome_feriado="Consciência Negra",
        duplas=[Dupla(3, 4)],
    )
    escala = Escala(
        plantoes=[p_normal, p_feriado],
        gerada_em=datetime.now(),
        confirmada=True,
    )

    texto = gerar_texto_whatsapp(escala, dados_padrao)

    esperado = (
        "📋 *ESCALA DE PLANTÃO*\n\n"
        "📅 *Sábado, 07/11 — Manhã*\n"
        "1. Ana e Bruno\n\n"
        "📅 *Sexta, 20/11 — Manhã (Feriado: Consciência Negra)*\n"
        "1. Carla e Diego\n\n"
        "Trocas: falar com a coordenação."
    )

    assert texto == esperado
