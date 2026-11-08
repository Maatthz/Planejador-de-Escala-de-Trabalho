"""Testes automatizados para a interface oficial em Flet (`src.escala.interface_flet`)."""

from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
import flet as ft

from src.escala.edicao import confirmar_rascunho
from src.escala.gerador import gerar_escala
from src.escala.interface_flet.app_flet import construir_pagina
from src.escala.interface_flet.dialogos import (
    abrir_dialogo_feriados,
    abrir_dialogo_historico,
    abrir_dialogo_justica,
    abrir_dialogo_troca,
)
from src.escala.interface_flet.janela_configuracoes import abrir_dialogo_configuracoes
from src.escala.interface_flet.visao_equipe_folgas import agrupar_datas_continuas
from src.escala.modelos import DadosDoPrograma


class PaginaFalsa:
    """Simula `ft.Page` sem abrir janela gráfica para testes rápidos e determinísticos."""

    def __init__(self) -> None:
        self.title: str = ""
        self.window = SimpleNamespace(width=0, height=0, min_width=0, min_height=0)
        self.padding: int = 0
        self.theme_mode = ft.ThemeMode.DARK
        self.theme = None
        self.dark_theme = None
        self.controls: list[ft.Control] = []
        self.dialogos: list[ft.Control] = []

    def add(self, *controles: ft.Control) -> None:
        self.controls.extend(controles)

    def update(self) -> None:
        pass

    def show_dialog(self, dialogo: ft.Control) -> None:
        self.dialogos.append(dialogo)

    def pop_dialog(self) -> None:
        if self.dialogos:
            self.dialogos.pop()


def test_agrupar_datas_continuas_une_intervalos_consecutivos() -> None:
    """Datas seguidas devem virar um único intervalo (inicio, fim)."""
    datas = {
        date(2026, 12, 1),
        date(2026, 12, 2),
        date(2026, 12, 3),
        date(2026, 12, 10),
    }
    grupos = agrupar_datas_continuas(datas)
    assert grupos == [
        (date(2026, 12, 1), date(2026, 12, 3)),
        (date(2026, 12, 10), date(2026, 12, 10)),
    ]


def test_construir_pagina_flet_e_navegacao_entre_abas(
    dados_padrao: DadosDoPrograma,
    pasta_temporaria: Path,
) -> None:
    """A página Flet deve construir as 3 visões e alternar entre elas sem erros."""
    page = PaginaFalsa()
    ctx = construir_pagina(page, dados_iniciais=dados_padrao, aviso_inicial="Backup restaurado.")
    assert len(page.controls) == 1
    assert len(page.dialogos) == 1  # modal do aviso inicial
    page.pop_dialog()

    barra = ctx["barra_lateral"]
    for idx in (1, 2, 0):
        barra.selected_index = idx
        barra.on_change(SimpleNamespace(control=barra))


def test_visao_escala_visualizar_historico_com_rascunho_aberto(
    dados_padrao: DadosDoPrograma,
    pasta_temporaria: Path,
) -> None:
    """Deve ser possível visualizar uma escala confirmada mesmo com rascunho ativo."""
    page = PaginaFalsa()
    gerar_escala(dados_padrao, date(2026, 11, 2), 1, semente=10)
    confirmar_rascunho(dados_padrao)
    gerar_escala(dados_padrao, date(2026, 11, 9), 1, semente=20)

    ctx = construir_pagina(page, dados_iniciais=dados_padrao)
    visao_escala = ctx["visao_escala"]

    # Por padrão exibe o rascunho
    exibida = visao_escala.obter_escala_exibida()
    assert exibida is not None and not exibida.confirmada

    # Seleciona a escala 0 do histórico e confirma que ela permanece visível após atualizar()
    visao_escala._selecionar_escala_historico(0)
    exibida_hist = visao_escala.obter_escala_exibida()
    assert exibida_hist is not None and exibida_hist.confirmada

    # Volta ao rascunho
    visao_escala._voltar_ao_rascunho(None)
    assert not visao_escala.obter_escala_exibida().confirmada


def test_dialogos_flet_justica_historico_feriados_configuracoes(
    dados_padrao: DadosDoPrograma,
    pasta_temporaria: Path,
) -> None:
    """Todos os diálogos modais devem abrir e construir seus controles sem exceções."""
    page = PaginaFalsa()
    escala = gerar_escala(dados_padrao, date(2026, 11, 2), 1, semente=7)
    id_pessoa = escala.plantoes[0].duplas[0].pessoa_a

    abrir_dialogo_troca(page, escala, 0, id_pessoa, dados_padrao, lambda: None)
    assert len(page.dialogos) == 1
    page.pop_dialog()

    abrir_dialogo_justica(page, dados_padrao, lambda: None)
    assert len(page.dialogos) == 1
    page.pop_dialog()

    abrir_dialogo_historico(page, dados_padrao, lambda _: None, lambda _: None, lambda: None)
    assert len(page.dialogos) == 1
    page.pop_dialog()

    abrir_dialogo_feriados(page, dados_padrao, date(2026, 11, 2), lambda: None)
    assert len(page.dialogos) == 1
    page.pop_dialog()

    abrir_dialogo_configuracoes(page, dados_padrao, lambda: None)
    assert len(page.dialogos) == 1
    page.pop_dialog()
