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


MESES_PT: list[str] = [
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

DIAS_SEMANA_ABREV: list[str] = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


class CalendarioMensal(ctk.CTkFrame):
    """Componente de calendário em grade 7x6 para marcação de folgas e feriados."""

    def __init__(
        self,
        master,
        datas_marcadas: set[date] | None = None,
        ao_clicar: Callable[[date], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master=master,
            fg_color=COR_CARTAO,
            border_color=COR_BORDA,
            border_width=1,
            corner_radius=10,
            **kwargs,
        )
        self.datas_marcadas: set[date] = datas_marcadas if datas_marcadas is not None else set()
        self.ao_clicar: Callable[[date], None] | None = ao_clicar

        hoje = date.today()
        self.ano_atual: int = hoje.year
        self.mes_atual: int = hoje.month

        self._construir_estrutura()
        self._redesenhar_grade()

    def _construir_estrutura(self) -> None:
        """Cria o cabeçalho com botões de navegação e os títulos dos dias da semana."""
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=12, pady=(12, 8))

        btn_ant = ctk.CTkButton(
            topo,
            text="◀",
            width=36,
            height=32,
            font=FONTE_SUBTITULO,
            fg_color=COR_SECUNDARIA,
            hover_color=COR_SECUNDARIA_HOVER,
            text_color=COR_SECUNDARIA_TEXTO,
            command=self._mes_anterior,
        )
        btn_ant.pack(side="left")

        self.lbl_mes_ano = ctk.CTkLabel(
            topo,
            text="",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
        )
        self.lbl_mes_ano.pack(side="left", expand=True)

        btn_prox = ctk.CTkButton(
            topo,
            text="▶",
            width=36,
            height=32,
            font=FONTE_SUBTITULO,
            fg_color=COR_SECUNDARIA,
            hover_color=COR_SECUNDARIA_HOVER,
            text_color=COR_SECUNDARIA_TEXTO,
            command=self._mes_proximo,
        )
        btn_prox.pack(side="right")

        # Cabeçalho dos dias da semana (Seg a Dom)
        dias_frame = ctk.CTkFrame(self, fg_color="transparent")
        dias_frame.pack(fill="x", padx=12, pady=(0, 4))
        for col, dia_abrev in enumerate(DIAS_SEMANA_ABREV):
            dias_frame.grid_columnconfigure(col, weight=1)
            lbl_dia = ctk.CTkLabel(
                dias_frame,
                text=dia_abrev,
                font=FONTE_AJUDA,
                text_color=COR_TEXTO_SUAVE,
            )
            lbl_dia.grid(row=0, column=col, sticky="ew")

        # Grade dos dias (7 colunas x 6 semanas)
        self.grade_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grade_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for col in range(7):
            self.grade_frame.grid_columnconfigure(col, weight=1)

    def _mes_anterior(self) -> None:
        """Avança para o mês anterior."""
        if self.mes_atual == 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        else:
            self.mes_atual -= 1
        self._redesenhar_grade()

    def _mes_proximo(self) -> None:
        """Avança para o próximo mês."""
        if self.mes_atual == 12:
            self.mes_atual = 1
            self.ano_atual += 1
        else:
            self.mes_atual += 1
        self._redesenhar_grade()

    def _redesenhar_grade(self) -> None:
        """Limpa e reconstrói os botões da grade do mês atual."""
        import calendar

        for filho in self.grade_frame.winfo_children():
            filho.destroy()

        nome_mes = MESES_PT[self.mes_atual]
        self.lbl_mes_ano.configure(text=f"{nome_mes} de {self.ano_atual}")

        semanas = calendar.monthcalendar(self.ano_atual, self.mes_atual)
        for lin, semana in enumerate(semanas):
            for col, num_dia in enumerate(semana):
                if num_dia == 0:
                    lbl_vazio = ctk.CTkLabel(self.grade_frame, text="", height=36)
                    lbl_vazio.grid(row=lin, column=col, padx=2, pady=2, sticky="nsew")
                else:
                    data_dia = date(self.ano_atual, self.mes_atual, num_dia)
                    marcado = data_dia in self.datas_marcadas

                    fg = COR_PERIGO if marcado else "transparent"
                    hover = COR_PERIGO_HOVER if marcado else COR_SECUNDARIA_HOVER
                    cor_texto = "#FFFFFF" if marcado else COR_TEXTO

                    btn_dia = ctk.CTkButton(
                        self.grade_frame,
                        text=str(num_dia),
                        font=FONTE_CORPO,
                        height=36,
                        width=36,
                        fg_color=fg,
                        hover_color=hover,
                        text_color=cor_texto,
                        corner_radius=8,
                        command=lambda d=data_dia: self._ao_clicar_dia(d),
                    )
                    btn_dia.grid(row=lin, column=col, padx=2, pady=2, sticky="nsew")

    def _ao_clicar_dia(self, dia: date) -> None:
        """Dispara o callback de clique no dia."""
        if self.ao_clicar:
            self.ao_clicar(dia)

    def atualizar_datas_marcadas(self, datas: set[date]) -> None:
        """Atualiza a lista de datas marcadas e redesenha a grade."""
        self.datas_marcadas = datas
        self._redesenhar_grade()
