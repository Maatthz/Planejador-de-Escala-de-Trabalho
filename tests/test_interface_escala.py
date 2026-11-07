"""Testes de interface para a aba Escala, diálogos de feriado, justiça e histórico."""

from datetime import date, datetime
from pathlib import Path
import pytest

from src.escala.armazenamento import carregar
from src.escala.interface.janela_feriado import JanelaFeriado
from src.escala.interface.janela_historico import JanelaHistorico
from src.escala.interface.janela_justica import JanelaJustica
from src.escala.interface.janela_principal import JanelaPrincipal
from src.escala.modelos import DadosDoPrograma, Dupla, Escala, Feriado, Plantao


@pytest.fixture
def app_janela_escala(app_janela_compartilhada: JanelaPrincipal) -> JanelaPrincipal:
    """Usa a janela compartilhada da sessão para evitar recriação de Tcl."""
    return app_janela_compartilhada


def test_tela_escala_inicializacao_vazia(
    app_janela_escala: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """Tela de escala deve iniciar com estado vazio quando não há escalas geradas."""
    dados_padrao.rascunho = None
    dados_padrao.escalas.clear()
    app_janela_escala.dados = dados_padrao
    app_janela_escala.tela_escala.dados = dados_padrao
    app_janela_escala.tela_escala.escala_ativa = None
    app_janela_escala.tela_escala.atualizar_tela()
    app_janela_escala.update_idletasks()

    assert app_janela_escala.tela_escala.escala_ativa is None
    filhos = app_janela_escala.tela_escala.scroll_plantoes.winfo_children()
    assert len(filhos) == 1  # Cartão de estado vazio


def test_gerar_escala_interface(
    app_janela_escala: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """Executar a geração pela interface deve produzir um rascunho com faixa de status amarela."""
    app_janela_escala.dados = dados_padrao
    app_janela_escala.tela_escala.dados = dados_padrao
    app_janela_escala.tela_escala.data_inicio = date(2026, 11, 2)
    app_janela_escala.tela_escala.combo_semanas.set("1")

    app_janela_escala.tela_escala._executar_geracao()
    app_janela_escala.update_idletasks()

    # Verifica se gerou o rascunho
    assert app_janela_escala.dados.rascunho is not None
    assert app_janela_escala.dados.rascunho.confirmada is False
    assert len(app_janela_escala.tela_escala.escala_ativa.plantoes) == 2

    # Verifica persistência
    carregados, _ = carregar(pasta_temporaria)
    assert carregados.rascunho is not None


def test_confirmar_escala_interface(
    app_janela_escala: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """Confirmar escala deve mover o rascunho para o histórico e alterar a faixa para confirmada."""
    app_janela_escala.dados = dados_padrao
    app_janela_escala.tela_escala.dados = dados_padrao
    app_janela_escala.tela_escala.data_inicio = date(2026, 11, 2)
    app_janela_escala.tela_escala.combo_semanas.set("1")
    app_janela_escala.tela_escala._executar_geracao()

    # Confirmação
    app_janela_escala.tela_escala._confirmar_escala_atual()
    app_janela_escala.update_idletasks()

    assert app_janela_escala.dados.rascunho is None
    assert len(app_janela_escala.dados.escalas) == 1
    assert app_janela_escala.dados.escalas[0].confirmada is True

    # Persistência
    carregados, _ = carregar(pasta_temporaria)
    assert carregados.rascunho is None
    assert len(carregados.escalas) == 1


def test_copiar_whatsapp_interface(
    app_janela_escala: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """Copiar para WhatsApp deve preencher o clipboard e mudar o texto do botão temporariamente."""
    app_janela_escala.dados = dados_padrao
    app_janela_escala.tela_escala.dados = dados_padrao
    app_janela_escala.tela_escala.data_inicio = date(2026, 11, 2)
    app_janela_escala.tela_escala._executar_geracao()

    app_janela_escala.tela_escala._copiar_whatsapp()
    conteudo_clipboard = app_janela_escala.clipboard_get()

    assert "ESCALA DE PLANTÃO" in conteudo_clipboard
    assert "Sábado" in conteudo_clipboard
    assert app_janela_escala.tela_escala.btn_copiar.cget("text") == "✅ Copiado!"


def test_janela_feriado_adiciona_feriado(
    app_janela_escala: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """JanelaFeriado deve adicionar uma nova data com plantão aos feriados e persistir."""
    app_janela_escala.dados = dados_padrao
    janela_fer = JanelaFeriado(
        pai=app_janela_escala,
        dados=dados_padrao,
        ao_mudar=app_janela_escala.ao_mudar,
    )
    janela_fer.campo_data.insert(0, "20/11/2026")
    janela_fer.campo_nome.insert(0, "Consciência Negra")
    janela_fer.combo_periodo.set("manhã")
    janela_fer.combo_duplas.set("4")

    janela_fer._salvar_feriado()
    janela_fer.destroy()

    assert len(dados_padrao.feriados) == 1
    assert dados_padrao.feriados[0].data == date(2026, 11, 20)
    assert dados_padrao.feriados[0].nome == "Consciência Negra"

    carregados, _ = carregar(pasta_temporaria)
    assert len(carregados.feriados) == 1


def test_janela_justica_exibe_integrantes(
    app_janela_escala: JanelaPrincipal, dados_padrao: DadosDoPrograma, pasta_temporaria: Path
) -> None:
    """JanelaJustica deve abrir, exibir a fila e permitir edição manual dos contadores."""
    app_janela_escala.dados = dados_padrao
    janela_just = JanelaJustica(
        pai=app_janela_escala,
        dados=dados_padrao,
        ao_mudar=app_janela_escala.ao_mudar,
    )
    app_janela_escala.update_idletasks()

    filhos = [
        f for f in janela_just.winfo_children()
        if hasattr(f, "winfo_children")
    ]
    assert len(filhos) > 0

    # Ativa modo de edição manual e altera a pessoa de ID 1
    janela_just._ativar_modo_edicao()
    ent_p, ent_f, ent_u = janela_just._campos_edicao[1]
    ent_p.delete(0, "end")
    ent_p.insert(0, "6")
    ent_f.delete(0, "end")
    ent_f.insert(0, "2")
    ent_u.delete(0, "end")
    ent_u.insert(0, "31/10/2026")

    janela_just._salvar_edicao()
    assert janela_just._modo_edicao is False

    p1 = dados_padrao.buscar_pessoa(1)
    assert p1 is not None
    assert p1.ajuste_plantoes == 6
    assert p1.ajuste_feriados == 2
    assert p1.ultimo_plantao_manual == date(2026, 10, 31)

    janela_just.destroy()


def test_janela_historico_exibe_e_exclui(
    app_janela_escala: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma, monkeypatch
) -> None:
    """JanelaHistorico lista escalas confirmadas e permite exclusão com recálculo."""
    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    dados_padrao.escalas.append(Escala(plantoes=[plantao], gerada_em=datetime.now(), confirmada=True))

    app_janela_escala.dados = dados_padrao
    janela_hist = JanelaHistorico(
        pai=app_janela_escala,
        dados=dados_padrao,
        ao_mudar=app_janela_escala.ao_mudar,
    )
    janela_hist.update_idletasks()

    assert len(dados_padrao.escalas) == 1

    # Simula confirmação "Sim" no diálogo de exclusão
    monkeypatch.setattr("src.escala.interface.janela_historico.perguntar_sim_nao", lambda *args, **kwargs: True)

    janela_hist._excluir(0)
    janela_hist.destroy()

    assert len(dados_padrao.escalas) == 0
    carregados, _ = carregar(pasta_temporaria)
    assert len(carregados.escalas) == 0
