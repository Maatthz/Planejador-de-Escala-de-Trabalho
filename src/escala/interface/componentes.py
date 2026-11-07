"""Design System e componentes reutilizáveis da interface gráfica.

Centraliza tokens visuais (cores, fontes, espaçamentos) e widgets padronizados
para garantir consistência e usabilidade acessível a pessoas leigas.
"""

from collections.abc import Callable
from contextlib import contextmanager
import ctypes
from datetime import date
import sys
import tkinter as tk
import customtkinter as ctk

from src.escala.textos_ajuda import obter_ajuda

# Fixa o modo de aparência como escuro (Dark Mode) para conforto visual e menor cansaço ocular
ctk.set_appearance_mode("dark")

# Tokens Visuais — Paleta Semântica (Modo Escuro Grafite / Charcoal)
COR_FUNDO: str = "#121214"
COR_CARTAO: str = "#1E1E22"
COR_BORDA: str = "#2E2E34"

COR_PRIMARIA: str = "#3B82F6"
COR_PRIMARIA_HOVER: str = "#2563EB"

COR_SUCESSO: str = "#16A34A"
COR_SUCESSO_HOVER: str = "#15803D"

COR_SECUNDARIA: str = "#2A2A30"
COR_SECUNDARIA_TEXTO: str = "#F4F4F5"
COR_SECUNDARIA_HOVER: str = "#3A3A42"

COR_PERIGO: str = "#DC2626"
COR_PERIGO_HOVER: str = "#B91C1C"

COR_AVISO_FUNDO: str = "#3D2406"
COR_AVISO_TEXTO: str = "#FDE68A"

COR_SUCESSO_FUNDO: str = "#064E3B"
COR_SUCESSO_TEXTO: str = "#A7F3D0"

COR_ESTRELA: str = "#FACC15"
COR_ESTRELA_HOVER: str = "#EAB308"

COR_TEXTO: str = "#F4F4F5"
COR_TEXTO_SUAVE: str = "#A1A1AA"

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

    def __init__(self, master, chave_ajuda: str, widget_controle=None, **kwargs) -> None:
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

        if callable(widget_controle):
            self.widget = widget_controle(self)
            self.widget.pack(fill="x", pady=(0, 6))
        elif widget_controle is not None:
            self.widget = widget_controle
            self.widget.pack(fill="x", pady=(0, 6))
        else:
            self.widget = None

        lbl_explicacao = ctk.CTkLabel(
            self,
            text=ajuda.explicacao,
            font=FONTE_AJUDA,
            text_color=COR_TEXTO_SUAVE,
            justify="left",
            wraplength=600,
            anchor="w",
        )
        lbl_explicacao.pack(fill="x", pady=(0, 2))

        lbl_exemplo = ctk.CTkLabel(
            self,
            text=f"Exemplo: {ajuda.exemplo}",
            font=FONTE_AJUDA,
            text_color=COR_TEXTO_SUAVE,
            justify="left",
            wraplength=600,
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


def perguntar_sim_nao(
    pai,
    titulo: str,
    texto: str | None = None,
    variante_confirmar: str = "perigo",
) -> bool:
    """Abre um diálogo modal de confirmação retornando True (Sim) ou False (Não)."""
    if texto is None:
        texto = titulo
        titulo = "Confirmação"
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

    btn_sim = BotaoGrande(
        botoes_frame,
        "Sim, continuar",
        _ao_confirmar,
        variante=variante_confirmar,
        height=38,
    )
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


def configurar_rolagem_suave(scroll: ctk.CTkScrollableFrame) -> None:
    """Otimiza a taxa de rolagem do CTkScrollableFrame para evitar micro-redesenhos lentos."""
    try:
        if hasattr(scroll, "_parent_canvas"):
            scroll._parent_canvas.configure(yscrollincrement=24)
    except Exception:
        pass


@contextmanager
def congelar_redesenho(widget):
    """Congela temporariamente a pintura Win32 (WM_SETREDRAW) para evitar efeito cascata."""
    hwnd = 0
    user32 = None
    if sys.platform == "win32":
        try:
            user32 = ctypes.windll.user32
            hwnd = widget.winfo_id()
            if hwnd:
                user32.SendMessageW(hwnd, 0x000B, 0, 0)
        except Exception:
            hwnd = 0
    try:
        yield
    finally:
        if hwnd and user32 is not None:
            try:
                widget.update_idletasks()
                user32.SendMessageW(hwnd, 0x000B, 1, 0)
                # RDW_INVALIDATE | RDW_ERASE | RDW_ALLCHILDREN | RDW_UPDATENOW | RDW_FRAME
                user32.RedrawWindow(hwnd, None, None, 0x0585)
            except Exception:
                pass


class RotuloSimples(tk.Label):
    """Rótulo de texto nativo leve (1 único HWND sem Canvas) compatível com CTkLabel."""

    def __init__(
        self,
        master,
        text: str = "",
        font: tuple = FONTE_CORPO,
        text_color: str = COR_TEXTO,
        fg_color: str | None = None,
        width: int = 0,
        anchor: str = "center",
        justify: str = "left",
        **kwargs,
    ) -> None:
        cor_fundo = fg_color
        if not cor_fundo or cor_fundo == "transparent":
            cor_fundo = master.cget("fg_color") if hasattr(master, "cget") else COR_CARTAO
            if isinstance(cor_fundo, (tuple, list)):
                cor_fundo = cor_fundo[1]
            if not cor_fundo or cor_fundo == "transparent":
                cor_fundo = COR_CARTAO
        fonte_escalada = (
            master._apply_font_scaling(font)
            if hasattr(master, "_apply_font_scaling")
            else font
        )
        self._cor_texto = text_color
        super().__init__(
            master,
            text=text,
            font=fonte_escalada,
            fg=text_color,
            bg=cor_fundo,
            bd=0,
            highlightthickness=0,
            anchor=anchor,
            justify=justify,
            width=width,
            **kwargs,
        )

    def configure(self, **kwargs) -> None:
        """Atualiza propriedades aceitando os mesmos nomes do CustomTkinter."""
        if "text_color" in kwargs:
            cor = kwargs.pop("text_color")
            self._cor_texto = cor
            kwargs["fg"] = cor
        if "fg_color" in kwargs:
            kwargs["bg"] = kwargs.pop("fg_color")
        if "font" in kwargs:
            fonte = kwargs.pop("font")
            kwargs["font"] = (
                self.master._apply_font_scaling(fonte)
                if hasattr(self.master, "_apply_font_scaling")
                else fonte
            )
        super().configure(**kwargs)

    config = configure

    def cget(self, key: str):
        """Retorna propriedades compatíveis com CTkLabel."""
        if key == "text_color":
            return self._cor_texto
        return super().cget(key)


class AbasRapidas(ctk.CTkTabview):
    """Tabview otimizado que mantém abas mapeadas na mesma célula e alterna via tkraise()."""

    def __init__(self, master, **kwargs) -> None:
        self._abas_mapeadas: set[str] = set()
        super().__init__(master, **kwargs)

    def insert(self, index: int, name: str) -> ctk.CTkFrame:
        """Cria a aba isolando a propagação de geometria (pack/grid_propagate=False)."""
        aba = super().insert(index, name)
        aba.configure(fg_color=COR_FUNDO)
        aba.pack_propagate(False)
        aba.grid_propagate(False)
        if self._current_name == name:
            self._abas_mapeadas.add(name)
        return aba

    def _garantir_aba_mapeada(self, name: str) -> None:
        """Mapeia a aba na grade na primeira visita e nunca mais usa grid_forget()."""
        if name not in self._abas_mapeadas:
            nome_anterior = self._current_name
            self._current_name = name
            self._set_grid_current_tab()
            self._current_name = nome_anterior
            self._abas_mapeadas.add(name)

    def _segmented_button_callback(self, selected_name: str) -> None:
        """Troca de aba via tkraise() sem desmapeamento (grid_forget)."""
        if selected_name == self._current_name:
            return
        self._current_name = selected_name
        if self._command is not None:
            self._command()
        self._garantir_aba_mapeada(selected_name)
        self._tab_dict[selected_name].tkraise()

    def set(self, name: str) -> None:
        """Seleciona uma aba programaticamente via tkraise() sem grid_forget()."""
        if name not in self._tab_dict:
            raise ValueError(f"AbasRapidas não possui a aba '{name}'")
        if name == self._current_name:
            self._segmented_button.set(name)
            return
        self._current_name = name
        self._segmented_button.set(name)
        if self._command is not None:
            self._command()
        self._garantir_aba_mapeada(name)
        self._tab_dict[name].tkraise()


class CalendarioMensal(ctk.CTkFrame):
    """Componente de calendário em grade 7x6 com botões reutilizados (in-place update)."""

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

        # Lista de 42 botões reutilizados in-place (sem destroy() ao navegar)
        self._botoes_dias: list[ctk.CTkButton] = []
        self._estado_botoes: list[tuple | None] = [None] * 42

        self._construir_estrutura()
        self._construir_grade_botoes()
        self._atualizar_dias()

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

        # Cabeçalho dos dias da semana (Seg a Dom) com Sáb e Dom destacados
        self.dias_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dias_frame.pack(fill="x", padx=12, pady=(0, 4))
        self._rotulos_cabecalho: list[ctk.CTkLabel] = []
        for col, dia_abrev in enumerate(DIAS_SEMANA_ABREV):
            self.dias_frame.grid_columnconfigure(col, weight=1)
            eh_fim_de_semana = dia_abrev in ("Sáb", "Dom")
            lbl_dia = ctk.CTkLabel(
                self.dias_frame,
                text=dia_abrev,
                font=("Segoe UI", 12, "bold") if eh_fim_de_semana else FONTE_AJUDA,
                text_color=COR_PRIMARIA if eh_fim_de_semana else COR_TEXTO_SUAVE,
            )
            lbl_dia.grid(row=0, column=col, sticky="ew")
            self._rotulos_cabecalho.append(lbl_dia)

        # Grade dos dias (7 colunas x 6 semanas)
        self.grade_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grade_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for col in range(7):
            self.grade_frame.grid_columnconfigure(col, weight=1)

    def _construir_grade_botoes(self) -> None:
        """Instancia os 42 botões uma única vez na inicialização para reuso in-place."""
        for idx in range(42):
            r = idx // 7
            c = idx % 7
            btn = ctk.CTkButton(
                self.grade_frame,
                text="",
                font=FONTE_CORPO,
                height=36,
                width=36,
                fg_color="transparent",
                hover_color=COR_SECUNDARIA_HOVER,
                text_color=COR_TEXTO,
                corner_radius=8,
            )
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            self._botoes_dias.append(btn)

    def _mes_anterior(self) -> None:
        """Avança para o mês anterior sem recriar os botões."""
        if self.mes_atual == 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        else:
            self.mes_atual -= 1
        self._atualizar_dias()

    def _mes_proximo(self) -> None:
        """Avança para o próximo mês sem recriar os botões."""
        if self.mes_atual == 12:
            self.mes_atual = 1
            self.ano_atual += 1
        else:
            self.mes_atual += 1
        self._atualizar_dias()

    def _atualizar_dias(self) -> None:
        """Atualiza o texto, cores e estados dos 42 botões existentes (in-place)."""
        import calendar

        nome_mes = MESES_PT[self.mes_atual]
        self.lbl_mes_ano.configure(text=f"{nome_mes} de {self.ano_atual}")
        hoje = date.today()

        semanas = calendar.monthcalendar(self.ano_atual, self.mes_atual)
        slots: list[int] = []
        for sem in semanas:
            slots.extend(sem)
        while len(slots) < 42:
            slots.append(0)

        for idx, num_dia in enumerate(slots[:42]):
            btn = self._botoes_dias[idx]
            if num_dia == 0:
                novo_estado = (0, False, False)
                if self._estado_botoes[idx] == novo_estado:
                    continue
                self._estado_botoes[idx] = novo_estado
                btn.configure(
                    text="",
                    fg_color="transparent",
                    hover_color=COR_CARTAO,
                    border_width=0,
                    state="disabled",
                    command=None,
                )
            else:
                data_dia = date(self.ano_atual, self.mes_atual, num_dia)
                marcado = data_dia in self.datas_marcadas
                eh_hoje = (data_dia == hoje)
                novo_estado = (data_dia, marcado, eh_hoje)
                if self._estado_botoes[idx] == novo_estado:
                    continue
                self._estado_botoes[idx] = novo_estado

                if marcado:
                    fg = COR_PERIGO
                    hover = COR_PERIGO_HOVER
                    cor_txt = "#FFFFFF"
                    borda_w = 0
                    borda_c = COR_BORDA
                elif eh_hoje:
                    fg = "transparent"
                    hover = COR_SECUNDARIA_HOVER
                    cor_txt = COR_PRIMARIA
                    borda_w = 2
                    borda_c = COR_PRIMARIA
                else:
                    fg = "transparent"
                    hover = COR_SECUNDARIA_HOVER
                    cor_txt = COR_TEXTO
                    borda_w = 0
                    borda_c = COR_BORDA

                btn.configure(
                    text=str(num_dia),
                    fg_color=fg,
                    hover_color=hover,
                    text_color=cor_txt,
                    border_width=borda_w,
                    border_color=borda_c,
                    state="normal",
                    command=lambda d=data_dia: self._ao_clicar_dia(d),
                )

    def _ao_clicar_dia(self, dia: date) -> None:
        """Dispara o callback de clique no dia."""
        if self.ao_clicar:
            self.ao_clicar(dia)

    def atualizar_datas_marcadas(self, datas: set[date]) -> None:
        """Atualiza a lista de datas marcadas in-place sem recriar widgets."""
        self.datas_marcadas = datas
        self._atualizar_dias()
