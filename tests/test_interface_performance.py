"""Testes de performance e polimento visual de interface (Fase 7.1).

Verifica o reuso de widgets (in-place updates) no CalendarioMensal e na TelaFolgas,
além da barra de período e eliminação de bordas aninhadas na TelaEscala.
"""

from datetime import date
import customtkinter as ctk
import pytest

from src.escala.interface.componentes import (
    COR_FUNDO,
    COR_PRIMARIA,
    COR_SECUNDARIA,
    CalendarioMensal,
)
from src.escala.interface.janela_principal import JanelaPrincipal
from src.escala.modelos import DadosDoPrograma


@pytest.fixture
def app_janela_perf(app_janela_compartilhada: JanelaPrincipal) -> JanelaPrincipal:
    """Usa a janela compartilhada da sessão para evitar recriação de Tcl."""
    return app_janela_compartilhada


def test_calendario_mensal_reutiliza_botoes_in_place(
    app_janela_perf: JanelaPrincipal,
) -> None:
    """Navegar meses e marcar datas deve reutilizar os 42 CTkButtons sem recriá-los (sem destroy)."""
    hoje = date.today()
    cal = CalendarioMensal(
        master=app_janela_perf,
        datas_marcadas={hoje},
    )
    app_janela_perf.update_idletasks()

    assert len(cal._botoes_dias) == 42
    ids_iniciais = [id(b) for b in cal._botoes_dias]

    # Cabeçalhos de Sábado e Domingo devem ter cor primária em destaque
    assert cal._rotulos_cabecalho[5].cget("text_color") == COR_PRIMARIA
    assert cal._rotulos_cabecalho[6].cget("text_color") == COR_PRIMARIA

    # 1. Navega para próximo mês
    cal._mes_proximo()
    app_janela_perf.update_idletasks()
    assert [id(b) for b in cal._botoes_dias] == ids_iniciais

    # 2. Navega para mês anterior
    cal._mes_anterior()
    app_janela_perf.update_idletasks()
    assert [id(b) for b in cal._botoes_dias] == ids_iniciais

    # 3. Atualiza datas marcadas
    cal.atualizar_datas_marcadas({hoje})
    app_janela_perf.update_idletasks()
    assert [id(b) for b in cal._botoes_dias] == ids_iniciais

    cal.destroy()


def test_tela_folgas_preserva_botoes_e_calendario(
    app_janela_perf: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """Selecionar pessoas na TelaFolgas não deve recriar a lista da esquerda nem o CalendarioMensal."""
    app_janela_perf.dados = dados_padrao
    app_janela_perf.tela_folgas.dados = dados_padrao
    app_janela_perf.tela_folgas.pessoa_selecionada = None
    app_janela_perf.tela_folgas.atualizar_tela()
    app_janela_perf.update_idletasks()

    # Dicionário de botões da lista da esquerda
    botoes_iniciais = {id_p: id(btn) for id_p, btn in app_janela_perf.tela_folgas._botoes_pessoas.items()}
    assert len(botoes_iniciais) == len(dados_padrao.pessoas_ativas())

    p1 = dados_padrao.buscar_pessoa(1)
    p2 = dados_padrao.buscar_pessoa(2)
    assert p1 is not None and p2 is not None

    # Seleciona pessoa 1
    app_janela_perf.tela_folgas._selecionar_pessoa(p1)
    app_janela_perf.update_idletasks()

    cal_instancia_id = id(app_janela_perf.tela_folgas.calendario)

    # Seleciona pessoa 2
    app_janela_perf.tela_folgas._selecionar_pessoa(p2)
    app_janela_perf.update_idletasks()

    # O calendário é o mesmo objeto na memória (in-place update)
    assert id(app_janela_perf.tela_folgas.calendario) == cal_instancia_id

    # Os botões de pessoas continuam os mesmos objetos (nenhum destroy em massa)
    botoes_finais = {id_p: id(btn) for id_p, btn in app_janela_perf.tela_folgas._botoes_pessoas.items()}
    assert botoes_finais == botoes_iniciais


def test_tela_escala_destaque_botoes_periodo_e_duplas_planas(
    app_janela_perf: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """Verifica destaque visual dos botões de período e duplas planas sem bordas aninhadas."""
    app_janela_perf.tabview.set("📋 Escala")
    app_janela_perf.dados = dados_padrao
    app_janela_perf.tela_escala.dados = dados_padrao
    app_janela_perf.tela_escala.data_inicio = date(2026, 11, 2)
    app_janela_perf.tela_escala.combo_semanas.set("1")
    app_janela_perf.tela_escala.atualizar_tela()
    app_janela_perf.update_idletasks()

    # 1. Seleciona "Esta semana"
    app_janela_perf.tela_escala._selecionar_esta_semana()
    assert app_janela_perf.tela_escala.btn_esta_semana.cget("fg_color") == COR_PRIMARIA
    assert app_janela_perf.tela_escala.btn_prox_semana.cget("fg_color") == COR_SECUNDARIA
    assert "📅" in app_janela_perf.tela_escala.lbl_periodo_datas.cget("text")

    # 2. Seleciona "Próxima semana"
    app_janela_perf.tela_escala._selecionar_proxima_semana()
    assert app_janela_perf.tela_escala.btn_esta_semana.cget("fg_color") == COR_SECUNDARIA
    assert app_janela_perf.tela_escala.btn_prox_semana.cget("fg_color") == COR_PRIMARIA
    assert "📅" in app_janela_perf.tela_escala.lbl_periodo_datas.cget("text")

    # 3. Gera escala e verifica duplas planas (border_width == 0 e botões diretos)
    app_janela_perf.tela_escala.data_inicio = date(2026, 11, 2)
    app_janela_perf.tela_escala._executar_geracao()
    app_janela_perf.tela_escala.atualizar_tela()
    app_janela_perf.update_idletasks()

    cartoes_plantao = app_janela_perf.tela_escala.scroll_plantoes.winfo_children()
    assert len(cartoes_plantao) >= 1

    # Localiza frames de duplas dentro do cartão
    encontrou_dupla_plana = False
    for cartao in cartoes_plantao:
        for filho in cartao.winfo_children():
            # frame_grid
            for frame_dupla in filho.winfo_children():
                if isinstance(frame_dupla, ctk.CTkFrame):
                    # Cada dupla deve ser plana: border_width == 0
                    assert frame_dupla.cget("border_width") == 0
                    assert frame_dupla.cget("fg_color") == COR_FUNDO

                    # Filhos da linha da dupla: número, botão A, &, botão B
                    filhos_dupla = frame_dupla.winfo_children()
                    botoes_pessoas = [w for w in filhos_dupla if isinstance(w, ctk.CTkButton)]
                    assert len(botoes_pessoas) == 2
                    assert botoes_pessoas[0].cget("anchor") == "w"
                    assert botoes_pessoas[1].cget("anchor") == "w"
                    encontrou_dupla_plana = True

    assert encontrou_dupla_plana, "Deve encontrar pelo menos um frame de dupla plano na grade"
