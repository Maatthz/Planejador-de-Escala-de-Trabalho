"""Janela principal da aplicação.

Coordena o ciclo de vida da interface gráfica, abas de navegação,
cabeçalho, rodapé e persistência unidirecional através de armazenamento.py.
"""

import customtkinter as ctk

from src.escala.armazenamento import carregar, salvar
from src.escala.interface.componentes import (
    COR_BORDA,
    COR_CARTAO,
    COR_FUNDO,
    COR_PRIMARIA,
    COR_PRIMARIA_HOVER,
    COR_SECUNDARIA,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_AJUDA,
    FONTE_CORPO,
    FONTE_SUBTITULO,
    FONTE_TITULO,
    BotaoGrande,
    CartaoFrame,
    mostrar_info,
)
from src.escala.interface.janela_configuracoes import JanelaConfiguracoes
from src.escala.interface.tela_equipe import TelaEquipe
from src.escala.interface.tela_escala import TelaEscala
from src.escala.interface.tela_folgas import TelaFolgas
from src.escala.modelos import DadosDoPrograma
from src.escala.versao import VERSAO


class JanelaPrincipal(ctk.CTk):
    """Janela principal que encapsula o estado e a navegação entre abas."""

    def __init__(self, dados: DadosDoPrograma | None = None, aviso_inicial: str | None = None) -> None:
        super().__init__()
        self.title("Planejador de Escala de Plantão")
        self.geometry("1080x720")
        self.minsize(960, 640)
        self.configure(fg_color=COR_FUNDO)

        # 1. Carrega o estado único da aplicação se não for fornecido
        if dados is not None:
            self.dados = dados
            self.aviso_inicial = aviso_inicial
        else:
            self.dados, self.aviso_inicial = carregar()

        # Rastreia abas que precisam atualizar sua visualização (Lazy Rendering)
        self._abas_desatualizadas: set[str] = set()

        self._construir_interface()

        # Se houve recuperação de backup, alerta o usuário de forma amigável
        if self.aviso_inicial:
            self.after(200, lambda: mostrar_info(self, self.aviso_inicial))

    def _construir_interface(self) -> None:
        """Monta o cabeçalho, sistema de abas e rodapé."""
        # Cabeçalho
        cabecalho = ctk.CTkFrame(self, fg_color=COR_CARTAO, height=65, corner_radius=0)
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)

        lbl_logo = ctk.CTkLabel(
            cabecalho,
            text="📋 Planejador de Escala",
            font=FONTE_TITULO,
            text_color=COR_TEXTO,
        )
        lbl_logo.pack(side="left", padx=24)

        btn_config = BotaoGrande(
            cabecalho,
            "⚙️ Configurações",
            comando=self._abrir_configuracoes,
            variante="secundaria",
            height=36,
        )
        btn_config.pack(side="right", padx=24)

        # Rodapé
        rodape = ctk.CTkFrame(self, fg_color=COR_CARTAO, height=35, corner_radius=0)
        rodape.pack(fill="x", side="bottom")
        rodape.pack_propagate(False)

        lbl_versao = ctk.CTkLabel(
            rodape,
            text=f"Versão {VERSAO} • Windows Desktop",
            font=FONTE_AJUDA,
            text_color=COR_TEXTO_SUAVE,
        )
        lbl_versao.pack(side="left", padx=24)

        # Sistema de Abas Navegáveis (com botões grandes e destacados)
        self.tabview = ctk.CTkTabview(
            self,
            fg_color="transparent",
            command=self._ao_trocar_aba,
            segmented_button_selected_color=COR_PRIMARIA,
            segmented_button_selected_hover_color=COR_PRIMARIA_HOVER,
            segmented_button_unselected_color=COR_SECUNDARIA,
            segmented_button_unselected_hover_color=COR_BORDA,
            text_color=COR_TEXTO,
        )
        self.tabview._segmented_button.configure(
            font=("Segoe UI", 16, "bold"),
            height=46,
            corner_radius=8,
        )
        self.tabview.pack(fill="both", expand=True, padx=16, pady=10)

        self.tab_equipe = self.tabview.add("👥 Equipe")
        self.tab_folgas = self.tabview.add("📅 Folgas")
        self.tab_escala = self.tabview.add("📋 Escala")

        # Aba Equipe (implementada na Fase 4)
        self.tela_equipe = TelaEquipe(
            master=self.tab_equipe,
            dados=self.dados,
            ao_mudar=self.ao_mudar,
        )
        self.tela_equipe.pack(fill="both", expand=True)

        # Aba Folgas (implementada na Fase 5)
        self.tela_folgas = TelaFolgas(
            master=self.tab_folgas,
            dados=self.dados,
            ao_mudar=self.ao_mudar,
        )
        self.tela_folgas.pack(fill="both", expand=True)

        # Aba Escala (implementada na Fase 6)
        self.tela_escala = TelaEscala(
            master=self.tab_escala,
            dados=self.dados,
            ao_mudar=self.ao_mudar,
        )
        self.tela_escala.pack(fill="both", expand=True)

    def _construir_placeholder_aba(self, tab, titulo: str, subtitulo: str) -> None:
        """Exibe mensagem orientativa nas abas das fases futuras."""
        frame = CartaoFrame(tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_t = ctk.CTkLabel(frame, text=titulo, font=FONTE_SUBTITULO, text_color=COR_TEXTO)
        lbl_t.pack(pady=(60, 10))

        lbl_s = ctk.CTkLabel(frame, text=subtitulo, font=FONTE_CORPO, text_color=COR_TEXTO_SUAVE)
        lbl_s.pack(pady=(0, 60))

    def _abrir_configuracoes(self) -> None:
        """Abre a janela modal de configurações completas com textos de ajuda."""
        JanelaConfiguracoes(pai=self, dados=self.dados, ao_mudar=self.ao_mudar)

    def _ao_trocar_aba(self) -> None:
        """Renderiza a aba recém-selecionada apenas se houver alterações pendentes (Lazy Rendering)."""
        aba_ativa = self.tabview.get()
        if aba_ativa == "👥 Equipe" and "equipe" in self._abas_desatualizadas:
            self.tela_equipe.atualizar_tela()
            self._abas_desatualizadas.discard("equipe")
        elif aba_ativa == "📅 Folgas" and hasattr(self, "tela_folgas") and "folgas" in self._abas_desatualizadas:
            self.tela_folgas.atualizar_tela()
            self._abas_desatualizadas.discard("folgas")
        elif aba_ativa == "📋 Escala" and hasattr(self, "tela_escala") and "escala" in self._abas_desatualizadas:
            self.tela_escala.atualizar_tela()
            self._abas_desatualizadas.discard("escala")

    def ao_mudar(self) -> None:
        """Salva o estado e atualiza imediatamente a aba ativa (demais sob demanda)."""
        salvar(self.dados)
        self._abas_desatualizadas = {"equipe", "folgas", "escala"}
        aba_ativa = self.tabview.get()

        if aba_ativa == "👥 Equipe":
            self.tela_equipe.atualizar_tela()
            self._abas_desatualizadas.discard("equipe")
        elif aba_ativa == "📅 Folgas" and hasattr(self, "tela_folgas"):
            self.tela_folgas.atualizar_tela()
            self._abas_desatualizadas.discard("folgas")
        elif aba_ativa == "📋 Escala" and hasattr(self, "tela_escala"):
            self.tela_escala.atualizar_tela()
            self._abas_desatualizadas.discard("escala")
        else:
            self.tela_equipe.atualizar_tela()
