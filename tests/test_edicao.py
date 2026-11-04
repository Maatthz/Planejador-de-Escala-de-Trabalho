"""Testes para o módulo de edição, validação e confirmação de escalas."""

from datetime import date, datetime
import pytest

from src.escala.edicao import (
    confirmar_rascunho,
    escalas_sobrepostas,
    excluir_escala,
    pessoas_para_troca,
    trocar_pessoa,
    validar_escala,
)
from src.escala.modelos import (
    DadosDoPrograma,
    Dupla,
    ErroEscala,
    Escala,
    Plantao,
)


def test_trocar_pessoa_mesmo_dia_levanta_erro(dados_padrao: DadosDoPrograma) -> None:
    """Tentar trocar uma pessoa por alguém que já trabalha no mesmo dia levanta ErroEscala."""
    p1 = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    p2 = Plantao(
        data=date(2026, 11, 7),
        periodo="tarde",
        qtd_duplas=1,
        duplas=[Dupla(3, 4)],
    )
    escala = Escala(plantoes=[p1, p2], gerada_em=datetime.now())

    # Tenta colocar a pessoa 3 (que já trabalha à tarde) no plantão da manhã no lugar da 2
    with pytest.raises(ErroEscala, match="já está escalado\\(a\\) em outro plantão"):
        trocar_pessoa(escala, indice_plantao=0, id_sai=2, id_entra=3, dados=dados_padrao)


def test_trocar_pessoa_de_folga_retorna_aviso_sem_bloquear(
    dados_padrao: DadosDoPrograma,
) -> None:
    """Trocar por alguém de folga é permitido (o usuário decide), mas retorna um aviso."""
    p1 = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    escala = Escala(plantoes=[p1], gerada_em=datetime.now())

    # Pessoa 5 marcou folga no sábado
    pessoa5 = dados_padrao.buscar_pessoa(5)
    pessoa5.indisponibilidades.add(date(2026, 11, 7))

    avisos = trocar_pessoa(
        escala, indice_plantao=0, id_sai=2, id_entra=5, dados=dados_padrao
    )

    # A troca foi efetuada
    assert p1.duplas[0].ids() == (1, 5)
    # E retornou aviso sobre a folga
    assert len(avisos) == 1
    assert "marcou folga" in avisos[0]


def test_confirmar_rascunho_substitui_sobrepostas(
    dados_padrao: DadosDoPrograma,
) -> None:
    """confirmar_rascunho move o rascunho para escalas e substitui escalas anteriores com datas em comum."""
    sabado = date(2026, 11, 7)
    p_antigo = Plantao(
        data=sabado, periodo="manhã", qtd_duplas=1, duplas=[Dupla(1, 2)]
    )
    escala_antiga = Escala(
        plantoes=[p_antigo], gerada_em=datetime(2026, 11, 1), confirmada=True
    )
    dados_padrao.escalas.append(escala_antiga)

    # Novo rascunho com a mesma data (sabado)
    p_novo = Plantao(
        data=sabado, periodo="manhã", qtd_duplas=1, duplas=[Dupla(3, 4)]
    )
    rascunho = Escala(
        plantoes=[p_novo], gerada_em=datetime(2026, 11, 4), confirmada=False
    )
    dados_padrao.rascunho = rascunho

    confirmar_rascunho(dados_padrao)

    assert dados_padrao.rascunho is None
    assert len(dados_padrao.escalas) == 1
    assert dados_padrao.escalas[0].confirmada is True
    assert dados_padrao.escalas[0].plantoes[0].duplas[0].ids() == (3, 4)


def test_excluir_escala(dados_padrao: DadosDoPrograma) -> None:
    """excluir_escala remove a escala correspondente do histórico."""
    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    dados_padrao.escalas.append(
        Escala(plantoes=[plantao], gerada_em=datetime.now(), confirmada=True)
    )

    assert len(dados_padrao.escalas) == 1
    excluir_escala(dados_padrao, indice=0)
    assert len(dados_padrao.escalas) == 0


def test_validar_escala_detecta_irregularidades(dados_padrao: DadosDoPrograma) -> None:
    """validar_escala deve apontar todas as quebras de regras da escala."""
    # Monta uma escala com várias irregularidades:
    # 1. Menos duplas que o necessário
    # 2. Pessoa inativa
    # 3. Pessoa de folga
    # 4. Dupla proibida
    sabado = date(2026, 11, 7)
    dados_padrao.configuracao.nunca_juntos = [(1, 2)]

    p_inativa = dados_padrao.buscar_pessoa(1)
    p_inativa.ativo = False

    p_folga = dados_padrao.buscar_pessoa(2)
    p_folga.indisponibilidades.add(sabado)

    plantao = Plantao(
        data=sabado,
        periodo="manhã",
        qtd_duplas=2,  # espera 2 duplas, tem só 1
        duplas=[Dupla(1, 2)],
    )
    escala = Escala(plantoes=[plantao], gerada_em=datetime.now())

    erros = validar_escala(escala, dados_padrao)
    assert any("deveria ter 2" in e for e in erros)
    assert any("está inativo" in e for e in erros)
    assert any("em dia de folga" in e for e in erros)
    assert any("Nunca juntos" in e for e in erros)
