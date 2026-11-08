"""Janela principal oficial em Flet para o Planejador de Escala de Plantão.

Conecta a interface Material Design 3 à camada de armazenamento real (%APPDATA%),
ao atualizador automático em segundo plano e às janelas de configuração.
"""

from pathlib import Path
import tempfile
import flet as ft

from src.escala.armazenamento import carregar, salvar
from src.escala.atualizador import (
    ErroAtualizacao,
    InfoAtualizacao,
    baixar_e_verificar,
    instalar_e_reiniciar,
    programa_esta_empacotado,
    verificar_em_segundo_plano,
)
from src.escala.interface_flet.janela_configuracoes import abrir_dialogo_configuracoes
from src.escala.interface_flet.tema import (
    COR_PRIMARIA,
    confirmar_acao,
    mostrar_erro_modal,
    mostrar_info_modal,
)
from src.escala.interface_flet.visao_equipe_folgas import VisaoEquipe, VisaoFolgas
from src.escala.interface_flet.visao_escala import VisaoEscala
from src.escala.modelos import DadosDoPrograma
from src.escala.versao import VERSAO


def construir_pagina(
    page: ft.Page,
    dados_iniciais: DadosDoPrograma | None = None,
    aviso_inicial: str | None = None,
) -> dict[str, object]:
    """Configura a página Flet, barra de navegação lateral, temas e persistência."""
    page.title = f"Planejador de Escala de Plantão (v{VERSAO})"
    page.window.width = 1180
    page.window.height = 760
    page.window.min_width = 960
    page.window.min_height = 640
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=COR_PRIMARIA)
    page.dark_theme = ft.Theme(color_scheme_seed=COR_PRIMARIA)

    clipboard = ft.Clipboard()
    if dados_iniciais is not None:
        dados = dados_iniciais
        aviso = aviso_inicial
    else:
        dados, aviso = carregar()

    visoes: dict[str, object] = {}

    def _ao_mudar_estado() -> None:
        salvar(dados)
        if "escala" in visoes:
            visoes["escala"].atualizar()  # type: ignore[attr-defined]
        if "equipe" in visoes:
            visoes["equipe"].atualizar()  # type: ignore[attr-defined]
        if "folgas" in visoes:
            visoes["folgas"].atualizar()  # type: ignore[attr-defined]
        page.update()

    visao_escala = VisaoEscala(page, dados, clipboard, _ao_mudar_estado)
    visao_equipe = VisaoEquipe(page, dados, _ao_mudar_estado)
    visao_folgas = VisaoFolgas(page, dados, _ao_mudar_estado)
    visoes["escala"] = visao_escala
    visoes["equipe"] = visao_equipe
    visoes["folgas"] = visao_folgas

    area_conteudo = ft.Container(
        content=visao_escala.container_principal,
        expand=True,
        padding=ft.Padding.all(20),
    )

    def _trocar_aba(e: ft.ControlEvent) -> None:
        idx = e.control.selected_index
        if idx == 0:
            visao_escala.atualizar()
            area_conteudo.content = visao_escala.container_principal
        elif idx == 1:
            visao_equipe.atualizar()
            area_conteudo.content = visao_equipe.container_principal
        elif idx == 2:
            visao_folgas.atualizar()
            area_conteudo.content = visao_folgas.container_principal
        page.update()

    btn_tema = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE_ROUNDED,
        tooltip="Alternar Modo Claro / Escuro",
    )

    def _alternar_tema(_) -> None:
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            btn_tema.icon = ft.Icons.DARK_MODE_ROUNDED
        else:
            page.theme_mode = ft.ThemeMode.DARK
            btn_tema.icon = ft.Icons.LIGHT_MODE_ROUNDED
        page.update()

    btn_tema.on_click = _alternar_tema

    barra_lateral = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=96,
        group_alignment=-0.85,
        on_change=_trocar_aba,
        leading=ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.EVENT_AVAILABLE_ROUNDED,
                            color=ft.Colors.WHITE,
                            size=24,
                        ),
                        width=44,
                        height=44,
                        border_radius=12,
                        bgcolor=COR_PRIMARIA,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text("Plantão", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(f"v{VERSAO}", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=ft.Padding.only(top=14, bottom=10),
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_VIEW_WEEK_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_VIEW_WEEK_ROUNDED,
                label="Escala",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.GROUPS_OUTLINED,
                selected_icon=ft.Icons.GROUPS_ROUNDED,
                label="Equipe",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BEACH_ACCESS_OUTLINED,
                selected_icon=ft.Icons.BEACH_ACCESS_ROUNDED,
                label="Folgas",
            ),
        ],
        trailing=ft.Container(
            content=ft.Column(
                [
                    ft.Divider(height=16),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS_ROUNDED,
                        tooltip="Configurações do programa",
                        on_click=lambda _: abrir_dialogo_configuracoes(
                            page, dados, _ao_mudar_estado
                        ),
                    ),
                    btn_tema,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            padding=ft.Padding.only(top=20),
        ),
    )

    page.add(
        ft.Row(
            [
                barra_lateral,
                ft.VerticalDivider(width=1),
                area_conteudo,
            ],
            expand=True,
            spacing=0,
        )
    )

    if aviso:
        mostrar_info_modal(page, "Recuperação automática de backup", aviso)

    if programa_esta_empacotado():
        def _oferecer_atualizacao(info: InfoAtualizacao) -> None:
            def _aplicar() -> None:
                pasta_temp = Path(tempfile.mkdtemp(prefix="atualizacao_escala_"))
                try:
                    novo_exe = baixar_e_verificar(info, pasta_temp)
                    instalar_e_reiniciar(novo_exe)
                except ErroAtualizacao as erro:
                    if "Mova o programa" in str(erro):
                        mostrar_erro_modal(page, str(erro))

            confirmar_acao(
                page,
                "Atualização disponível",
                f"Nova versão {info.versao} disponível! Deseja baixar e atualizar agora?",
                _aplicar,
                texto_confirmar="Atualizar agora",
            )

        verificar_em_segundo_plano(_oferecer_atualizacao)

    return {
        "dados": dados,
        "visao_escala": visao_escala,
        "visao_equipe": visao_equipe,
        "visao_folgas": visao_folgas,
        "barra_lateral": barra_lateral,
        "ao_mudar": _ao_mudar_estado,
    }


def iniciar_app_flet(
    dados: DadosDoPrograma | None = None,
    aviso_inicial: str | None = None,
) -> None:
    """Inicia a janela desktop oficial em Flet."""
    ft.run(lambda page: construir_pagina(page, dados_iniciais=dados, aviso_inicial=aviso_inicial))
