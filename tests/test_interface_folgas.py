"""Testes de interface para a aba Folgas e o componente CalendarioMensal."""

from datetime import date, timedelta
from pathlib import Path
import pytest

from src.escala.armazenamento import carregar
from src.escala.gerador import gerar_escala
from src.escala.interface.componentes import CalendarioMensal
from src.escala.interface.janela_principal import JanelaPrincipal
from src.escala.modelos import DadosDoPrograma


@pytest.fixture
def app_janela_folgas(app_janela_compartilhada: JanelaPrincipal) -> JanelaPrincipal:
    """Usa a janela compartilhada da sessão para evitar recriação de Tcl."""
    return app_janela_compartilhada


def test_tela_folgas_inicializacao_estado_vazio(
    app_janela_folgas: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """Tela de folgas deve iniciar com lista de integrantes e estado vazio no detalhe à direita."""
    app_janela_folgas.dados = dados_padrao
    app_janela_folgas.tela_folgas.dados = dados_padrao
    app_janela_folgas.tela_folgas.pessoa_selecionada = None
    app_janela_folgas.tela_folgas.atualizar_tela()
    app_janela_folgas.update_idletasks()

    assert app_janela_folgas.tela_folgas is not None
    assert app_janela_folgas.tela_folgas.pessoa_selecionada is None


def test_selecionar_pessoa_exibe_calendario(
    app_janela_folgas: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """Selecionar uma pessoa deve carregar seus dados no painel direito com CalendarioMensal."""
    app_janela_folgas.dados = dados_padrao
    app_janela_folgas.tela_folgas.dados = dados_padrao

    pessoa1 = dados_padrao.buscar_pessoa(1)
    app_janela_folgas.tela_folgas._selecionar_pessoa(pessoa1)
    app_janela_folgas.update_idletasks()

    assert app_janela_folgas.tela_folgas.pessoa_selecionada == pessoa1
    assert app_janela_folgas.tela_folgas.calendario is not None


def test_marcar_e_desmarcar_folga_calendario(
    app_janela_folgas: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """Clicar em uma data no calendário deve marcar folga; clicar novamente deve desmarcar."""
    app_janela_folgas.dados = dados_padrao
    app_janela_folgas.tela_folgas.dados = dados_padrao

    pessoa1 = dados_padrao.buscar_pessoa(1)
    app_janela_folgas.tela_folgas._selecionar_pessoa(pessoa1)
    dia_teste = date(2026, 11, 7)

    # 1. Marca folga
    app_janela_folgas.tela_folgas._alternar_dia_folga(dia_teste)
    assert dia_teste in pessoa1.indisponibilidades

    carregados, _ = carregar(pasta_temporaria)
    assert dia_teste in carregados.buscar_pessoa(1).indisponibilidades

    # 2. Desmarca folga
    app_janela_folgas.tela_folgas._alternar_dia_folga(dia_teste)
    assert dia_teste not in pessoa1.indisponibilidades

    carregados2, _ = carregar(pasta_temporaria)
    assert dia_teste not in carregados2.buscar_pessoa(1).indisponibilidades


def test_remover_folga_pela_lista(
    app_janela_folgas: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """Remover folga diretamente da lista de folgas cadastradas deve persistir no disco."""
    app_janela_folgas.dados = dados_padrao
    app_janela_folgas.tela_folgas.dados = dados_padrao

    pessoa1 = dados_padrao.buscar_pessoa(1)
    dia_folga = date(2026, 11, 14)
    pessoa1.indisponibilidades.add(dia_folga)
    app_janela_folgas.tela_folgas._selecionar_pessoa(pessoa1)

    app_janela_folgas.tela_folgas._remover_dia(dia_folga)
    assert dia_folga not in pessoa1.indisponibilidades

    carregados, _ = carregar(pasta_temporaria)
    assert dia_folga not in carregados.buscar_pessoa(1).indisponibilidades


def test_folgas_marcadas_sao_respeitadas_na_geracao(
    app_janela_folgas: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """Folgas marcadas na tela devem impedir que a pessoa seja escalada no gerador."""
    app_janela_folgas.dados = dados_padrao
    app_janela_folgas.tela_folgas.dados = dados_padrao

    pessoa1 = dados_padrao.buscar_pessoa(1)
    # Marca todo o fim de semana para a pessoa 1
    sabado = date(2026, 11, 7)
    domingo = date(2026, 11, 8)
    pessoa1.indisponibilidades.add(sabado)
    pessoa1.indisponibilidades.add(domingo)
    app_janela_folgas.ao_mudar()

    # Gera a escala para a semana do plantão
    inicio = date(2026, 11, 2)
    escala = gerar_escala(dados_padrao, inicio=inicio, qtd_semanas=1, semente=42)

    todos_escalados = set()
    for plantao in escala.plantoes:
        todos_escalados.update(plantao.pessoas())

    assert 1 not in todos_escalados


def test_calendario_navegacao_meses(app_janela_folgas: JanelaPrincipal) -> None:
    """Navegação de meses no CalendarioMensal deve avançar e retroceder ano/mês corretamente."""
    cal = CalendarioMensal(app_janela_folgas)
    cal.ano_atual = 2026
    cal.mes_atual = 12

    # Avança para janeiro de 2027
    cal._mes_proximo()
    assert cal.mes_atual == 1
    assert cal.ano_atual == 2027

    # Volta para dezembro de 2026
    cal._mes_anterior()
    assert cal.mes_atual == 12
    assert cal.ano_atual == 2026
