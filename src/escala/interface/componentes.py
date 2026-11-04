"""Design System e componentes reutilizáveis da interface gráfica.

Centraliza tokens visuais (cores, fontes, espaçamentos) e widgets padronizados
para garantir consistência e usabilidade acessível a pessoas leigas.
"""

from collections.abc import Callable
from datetime import date
import customtkinter as ctk

from src.escala.textos_ajuda import obter_ajuda

# Fixa o modo de aparência como claro para máxima legibilidade e contraste
ctk.set_appearance_mode("light")

# Tokens Visuais — Paleta Semântica
COR_FUNDO: str = "#F8FAFC"
COR_CARTAO: str = "#FFFFFF"
COR_BORDA: str = "#E2E8F0"

COR_PRIMARIA: str = "#1D4ED8"
COR_PRIMARIA_HOVER: str = "#1E40AF"

COR_SUCESSO: str = "#15803D"
COR_SUCESSO_HOVER: str = "#166534"

COR_SECUNDARIA: str = "#E2E8F0"
COR_SECUNDARIA_TEXTO: str = "#1E293B"
COR_SECUNDARIA_HOVER: str = "#CBD5E1"

COR_PERIGO: str = "#B91C1C"
COR_PERIGO_HOVER: str = "#991B1B"

COR_AVISO_FUNDO: str = "#FEF3C7"
COR_AVISO_TEXTO: str = "#92400E"

COR_TEXTO: str = "#0F172A"
COR_TEXTO_SUAVE: str = "#475569"

# Tokens Visuais — Tipografia Segoe UI
FONTE_TITULO: tuple[str, int, str] = ("Segoe UI", 20, "bold")
FONTE_SUBTITULO: tuple[str, int, str] = ("Segoe UI", 16, "bold")
FONTE_CORPO: tuple[str, int] = ("Segoe UI", 15)
FONTE_BOTAO: tuple[str, int, str] = ("Segoe UI", 16, "bold")
FONTE_AJUDA: tuple[str, int] = ("Segoe UI", 13)


class BotaoGrande(ctk.CTkButton):
    """Botão com variantes semânticas e altura generosa para facilidade de clique."""

    def __init__(
        self,
        master,
        texto: str,
        comando: Callable[[], None] | None = None,
        variante: str = "primaria",
        **kwargs,
    ) -> None:
        cfg = self._obter_estilo_variante(variante)
        altura = kwargs.pop("height", cfg["height"])
        fonte = kwargs.pop("font", cfg["font"])

        super().__init__(
            master=master,
            text=texto,
            command=comando,
            height=altura,
            font=fonte,
            fg_color=cfg["fg_color"],
            hover_color=cfg["hover_color"],
            text_color=cfg["text_color"],
            corner_radius=8,
            **kwargs,
        )

    def _obter_estilo_variante(self, variante: str) -> dict:
        if variante == "primaria":
            return {
                "fg_color": COR_PRIMARIA,
                "hover_color": COR_PRIMARIA_HOVER,
                "text_color": "#FFFFFF",
                "font": FONTE_BOTAO,
                "height": 44,
            }
        elif variante == "sucesso":
            return {
                "fg_color": COR_SUCESSO,
                "hover_color": COR_SUCESSO_HOVER,
                "text_color": "#FFFFFF",
                "font": FONTE_BOTAO,
                "height": 44,
            }
        elif variante == "secundaria":
            return {
                "fg_color": COR_SECUNDARIA,
                "hover_color": COR_SECUNDARIA_HOVER,
                "text_color": COR_SECUNDARIA_TEXTO,
                "font": FONTE_CORPO,
                "height": 36,
            }
        elif variante == "perigo":
            return {
                "fg_color": COR_PERIGO,
                "hover_color": COR_PERIGO_HOVER,
                "text_color": "#FFFFFF",
                "font": FONTE_CORPO,
                "height": 36,
            }
        return {
            "fg_color": COR_SECUNDARIA,
            "hover_color": COR_SECUNDARIA_HOVER,
            "text_color": COR_SECUNDARIA_TEXTO,
            "font": FONTE_CORPO,
            "height": 36,
        }


class CartaoFrame(ctk.CTkFrame):
    """Container branco com cantos arredondados e borda sutil para agrupamento visual."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master=master,
            fg_color=COR_CARTAO,
            border_color=COR_BORDA,
            border_width=1,
            corner_radius=10,
            **kwargs,
        )


class CampoComAjuda(ctk.CTkFrame):
    """Combina um título, controle de entrada, explicação didática e exemplo prático."""

    def __init__(self, master, chave_ajuda: str, widget_controle, **kwargs) -> None:
        super().__init__(master=master, fg_color="transparent", **kwargs)
        ajuda = obter_ajuda(chave_ajuda)

        lbl_titulo = ctk.CTkLabel(
            self,
            text=ajuda.titulo,
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_titulo.pack(fill="x", pady=(0, 4))

        widget_controle.pack(fill="x", pady=(0, 6))

        lbl_explicacao = ctk.CTkLabel(
            self,
            text=ajuda.explicacao,
            font=FONTE_AJUDA,
            text_color=COR_TEXTO_SUAVE,
            justify="left",
            wraplength=520,
            anchor="w",
        )
        lbl_explicacao.pack(fill="x", pady=(0, 2))

        lbl_exemplo = ctk.CTkLabel(
            self,
            text=f"Exemplo: {ajuda.exemplo}",
            font=FONTE_AJUDA,
            text_color=COR_TEXTO_SUAVE,
            justify="left",
            wraplength=520,
            anchor="w",
        )
        lbl_exemplo.pack(fill="x")


def configurar_janela_modal(
    janela: ctk.CTkToplevel,
    pai: ctk.CTk | ctk.CTkToplevel,
    titulo: str,
    largura: int,
    altura: int,
) -> None:
    """Configura tamanho, centralização sobre a janela pai, foco modal e fechamento por Esc."""
    janela.title(titulo)
    janela.configure(fg_color=COR_FUNDO)
    janela.resizable(False, False)

    pai.update_idletasks()
    pos_x = pai.winfo_x() + (pai.winfo_width() // 2) - (largura // 2)
    pos_y = pai.winfo_y() + (pai.winfo_height() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{max(pos_x, 0)}+{max(pos_y, 0)}")

    janela.transient(pai)
    janela.grab_set()
    janela.focus_set()
    janela.bind("<Escape>", lambda _: janela.destroy())


def mostrar_erro(pai, texto: str) -> None:
    """Exibe um diálogo modal com mensagem de erro amigável para o usuário."""
    janela = ctk.CTkToplevel(pai)
    configurar_janela_modal(janela, pai, "Atenção", 460, 200)

    lbl_icone = ctk.CTkLabel(janela, text="⚠️", font=("Segoe UI", 32))
    lbl_icone.pack(pady=(16, 4))

    lbl_msg = ctk.CTkLabel(
        janela,
        text=texto,
        font=FONTE_CORPO,
        text_color=COR_TEXTO,
        wraplength=400,
        justify="center",
    )
    lbl_msg.pack(padx=20, pady=(0, 16), expand=True)

    btn_ok = BotaoGrande(janela, "Entendi", janela.destroy, variante="primaria", height=38)
    btn_ok.pack(pady=(0, 16))


def mostrar_info(pai, texto: str) -> None:
    """Exibe um diálogo modal com mensagem informativa de sucesso ou recuperação."""
    janela = ctk.CTkToplevel(pai)
    configurar_janela_modal(janela, pai, "Informação", 460, 200)

    lbl_icone = ctk.CTkLabel(janela, text="ℹ️", font=("Segoe UI", 32))
    lbl_icone.pack(pady=(16, 4))

    lbl_msg = ctk.CTkLabel(
        janela,
        text=texto,
        font=FONTE_CORPO,
        text_color=COR_TEXTO,
        wraplength=400,
        justify="center",
    )
    lbl_msg.pack(padx=20, pady=(0, 16), expand=True)

    btn_ok = BotaoGrande(janela, "OK", janela.destroy, variante="sucesso", height=38)
    btn_ok.pack(pady=(0, 16))


def perguntar_sim_nao(pai, titulo: str, texto: str) -> bool:
    """Abre um diálogo modal de confirmação retornando True (Sim) ou False (Não)."""
    resposta = {"confirmou": False}

    janela = ctk.CTkToplevel(pai)
    configurar_janela_modal(janela, pai, titulo, 460, 210)

    lbl_msg = ctk.CTkLabel(
        janela,
        text=texto,
        font=FONTE_CORPO,
        text_color=COR_TEXTO,
        wraplength=400,
        justify="center",
    )
    lbl_msg.pack(padx=20, pady=(24, 16), expand=True)

    botoes_frame = ctk.CTkFrame(janela, fg_color="transparent")
    botoes_frame.pack(fill="x", padx=30, pady=(0, 20))

    def _ao_confirmar():
        resposta["confirmou"] = True
        janela.destroy()

    def _ao_cancelar():
        resposta["confirmou"] = False
        janela.destroy()

    btn_nao = BotaoGrande(botoes_frame, "Cancelar", _ao_cancelar, variante="secundaria", height=38)
    btn_nao.pack(side="left", expand=True, padx=(0, 8))

    btn_sim = BotaoGrande(botoes_frame, "Sim, continuar", _ao_confirmar, variante="perigo", height=38)
    btn_sim.pack(side="right", expand=True, padx=(8, 0))

    janela.wait_window()
    return resposta["confirmou"]


class CalendarioMensal(ctk.CTkFrame):
    """Componente de calendário em grade 7x6 para marcação de folgas e feriados."""

    def __init__(
        self,
        master,
        datas_marcadas: set[date] | None = None,
        ao_clicar: Callable[[date], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(master=master, fg_color=COR_CARTAO, corner_radius=10, **kwargs)
        self.datas_marcadas = datas_marcadas if datas_marcadas is not None else set()
        self.ao_clicar = ao_clicar
        self.ano_atual = date.today().year
        self.mes_atual = date.today().month
