"""Utilitários visuais, selos (badges), cartões de ajuda e diálogos da interface Flet.

Usa cores adaptáveis do Material 3 (`ft.Colors`) para funcionar tanto no
Modo Claro quanto no Modo Escuro sem precisar recriar controles.
"""

from collections.abc import Callable
import flet as ft

from src.escala.textos_ajuda import obter_ajuda

COR_PRIMARIA = "#2563EB"
COR_SUCESSO = "#16A34A"
COR_PERIGO = "#DC2626"
COR_AVISO = "#D97706"
COR_ESTRELA = "#F59E0B"


def iniciais_nome(nome: str) -> str:
    """Extrai até duas iniciais maiúsculas de um nome (ex.: 'Ana Souza' -> 'AS')."""
    partes = [p for p in nome.strip().split() if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return f"{partes[0][0]}{partes[-1][0]}".upper()


def criar_selo(
    texto: str,
    icone: ft.IconData | None = None,
    cor_fundo: str = ft.Colors.SECONDARY_CONTAINER,
    cor_texto: str = ft.Colors.ON_SECONDARY_CONTAINER,
) -> ft.Container:
    """Cria uma etiqueta arredondada (chip/badge) compacta com ícone opcional."""
    itens: list[ft.Control] = []
    if icone is not None:
        itens.append(ft.Icon(icone, size=15, color=cor_texto))
    itens.append(ft.Text(texto, size=12, weight=ft.FontWeight.W_600, color=cor_texto))

    return ft.Container(
        content=ft.Row(itens, spacing=5, tight=True),
        bgcolor=cor_fundo,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=20,
    )


def criar_bloco_ajuda(chave_ajuda: str, controle: ft.Control) -> ft.Container:
    """Empacota um controle com Título, Explicação e Exemplo vindos de textos_ajuda.py."""
    ajuda = obter_ajuda(chave_ajuda)
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(ajuda.titulo, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(
                    ajuda.explicacao,
                    size=13,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                controle,
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.LIGHTBULB_OUTLINE_ROUNDED,
                            size=15,
                            color=COR_ESTRELA,
                        ),
                        ft.Text(
                            f"Exemplo: {ajuda.exemplo}",
                            size=12,
                            italic=True,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            expand=True,
                        ),
                    ],
                    spacing=6,
                ),
            ],
            spacing=8,
        ),
        padding=ft.Padding.all(14),
        border_radius=10,
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
    )


def mostrar_notificacao(
    page: ft.Page,
    texto: str,
    icone: ft.IconData = ft.Icons.CHECK_CIRCLE_ROUNDED,
    cor_fundo: str = COR_SUCESSO,
) -> None:
    """Exibe uma barra flutuante (SnackBar) no rodapé com feedback imediato."""
    snack = ft.SnackBar(
        content=ft.Row(
            [
                ft.Icon(icone, color=ft.Colors.WHITE, size=20),
                ft.Text(texto, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_500),
            ],
            spacing=10,
        ),
        bgcolor=cor_fundo,
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=2800,
    )
    page.show_dialog(snack)


def mostrar_erro_modal(page: ft.Page, mensagem: str) -> None:
    """Abre um diálogo modal amigável para erros de regra de negócio (ErroEscala)."""
    dialogo = ft.AlertDialog(
        modal=True,
        icon=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=COR_AVISO, size=40),
        title=ft.Text("Atenção", weight=ft.FontWeight.BOLD, size=20),
        content=ft.Container(
            content=ft.Text(mensagem, size=15),
            width=420,
        ),
        actions=[
            ft.FilledButton("Entendi", on_click=lambda _: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dialogo)


def mostrar_info_modal(page: ft.Page, titulo: str, mensagem: str) -> None:
    """Abre um diálogo modal informativo para avisos ao usuário."""
    dialogo = ft.AlertDialog(
        modal=True,
        icon=ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=COR_PRIMARIA, size=40),
        title=ft.Text(titulo, weight=ft.FontWeight.BOLD, size=20),
        content=ft.Container(
            content=ft.Text(mensagem, size=15),
            width=440,
        ),
        actions=[
            ft.FilledButton("OK", on_click=lambda _: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dialogo)


def confirmar_acao(
    page: ft.Page,
    titulo: str,
    mensagem: str,
    ao_confirmar: Callable[[], None],
    texto_confirmar: str = "Sim, continuar",
    perigoso: bool = False,
) -> None:
    """Abre um diálogo de confirmação antes de executar ações destrutivas."""
    def _executar(_):
        page.pop_dialog()
        ao_confirmar()

    cor_botao = COR_PERIGO if perigoso else COR_PRIMARIA
    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, weight=ft.FontWeight.BOLD, size=19),
        content=ft.Container(content=ft.Text(mensagem, size=15), width=420),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
            ft.FilledButton(
                texto_confirmar,
                bgcolor=cor_botao,
                color=ft.Colors.WHITE,
                on_click=_executar,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dialogo)
