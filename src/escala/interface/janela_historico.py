"""Diálogo modal com o histórico de escalas confirmadas.

Permite consultar escalas passadas, copiá-las para o WhatsApp,
carregá-las para visualização/edição e excluir registros antigos.
"""

from collections.abc import Callable
import customtkinter as ctk

from src.escala.datas import formatar_data
from src.escala.edicao import excluir_escala
from src.escala.exportar import gerar_texto_whatsapp
from src.escala.interface.componentes import (
    COR_BORDA,
    COR_CARTAO,
    COR_FUNDO,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_AJUDA,
    FONTE_CORPO,
    FONTE_SUBTITULO,
    FONTE_TITULO,
    BotaoGrande,
    CartaoFrame,
    configurar_janela_modal,
    perguntar_sim_nao,
)
from src.escala.modelos import DadosDoPrograma, Escala


class JanelaHistorico(ctk.CTkToplevel):
    """Visualização e gerenciamento das escalas confirmadas do histórico."""

    def __init__(
        self,
        pai,
        dados: DadosDoPrograma,
        ao_mudar: Callable[[], None],
        ao_selecionar_para_ver: Callable[[Escala], None] | None = None,
    ) -> None:
        super().__init__(pai)
        self.dados = dados
        self.ao_mudar = ao_mudar
        self.ao_selecionar_para_ver = ao_selecionar_para_ver

        configurar_janela_modal(self, pai, "📜 Escalas Anteriores Confirmadas", 780, 560)
        self._construir_interface()

    def _construir_interface(self) -> None:
        """Monta o cabeçalho e a lista de escalas gravadas no histórico."""
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=24, pady=(20, 10))

        lbl_tit = ctk.CTkLabel(
            topo,
            text="📜 Histórico de Escalas Confirmadas",
            font=FONTE_TITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_tit.pack(fill="x")

        lbl_desc = ctk.CTkLabel(
            topo,
            text="Estas são as escalas oficiais salvas. Excluir uma escala recalcula a justiça automaticamente.",
            font=FONTE_CORPO,
            text_color=COR_TEXTO_SUAVE,
            anchor="w",
        )
        lbl_desc.pack(fill="x", pady=(2, 0))

        self.scroll_escalas = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_escalas.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._atualizar_lista()

    def _atualizar_lista(self) -> None:
        """Renderiza os cartões de cada escala confirmada."""
        for filho in self.scroll_escalas.winfo_children():
            filho.destroy()

        if not self.dados.escalas:
            cartao_vazio = CartaoFrame(self.scroll_escalas)
            cartao_vazio.pack(fill="x", pady=30, ipady=30)
            lbl = ctk.CTkLabel(
                cartao_vazio,
                text="Nenhuma escala foi confirmada ainda.\nQuando você gerar e confirmar uma escala, ela aparecerá aqui.",
                font=FONTE_SUBTITULO,
                text_color=COR_TEXTO_SUAVE,
                justify="center",
            )
            lbl.pack(expand=True)
            return

        # Lista as escalas mais recentes primeiro
        for idx in reversed(range(len(self.dados.escalas))):
            escala = self.dados.escalas[idx]
            self._criar_cartao_escala(escala, idx)

    def _criar_cartao_escala(self, escala: Escala, indice: int) -> None:
        """Cria um cartão com informações e ações da escala confirmada."""
        cartao = CartaoFrame(self.scroll_escalas)
        cartao.pack(fill="x", pady=6)

        info_frame = ctk.CTkFrame(cartao, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=16, pady=12)

        try:
            periodo_txt = f"{formatar_data(escala.primeiro_dia())} a {formatar_data(escala.ultimo_dia())}"
        except Exception:
            periodo_txt = "Período indefinido"

        lbl_periodo = ctk.CTkLabel(
            info_frame,
            text=f"📅 Período: {periodo_txt}",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_periodo.pack(fill="x")

        data_gerada = escala.gerada_em.strftime("%d/%m/%Y às %H:%M")
        lbl_sub = ctk.CTkLabel(
            info_frame,
            text=f"Gerada em {data_gerada} • {len(escala.plantoes)} plantão(ões)",
            font=FONTE_AJUDA,
            text_color=COR_TEXTO_SUAVE,
            anchor="w",
        )
        lbl_sub.pack(fill="x", pady=(2, 0))

        # Ações
        acoes = ctk.CTkFrame(cartao, fg_color="transparent")
        acoes.pack(side="right", padx=16, pady=12)

        if self.ao_selecionar_para_ver:
            btn_ver = BotaoGrande(
                acoes,
                "Visualizar",
                comando=lambda esc=escala: self._visualizar(esc),
                variante="secundaria",
                height=34,
            )
            btn_ver.pack(side="left", padx=(0, 6))

        btn_copiar = BotaoGrande(
            acoes,
            "📋 Copiar",
            comando=lambda esc=escala, b=None: None,
            variante="secundaria",
            height=34,
        )
        btn_copiar.configure(command=lambda esc=escala, b=btn_copiar: self._copiar_whatsapp(esc, b))
        btn_copiar.pack(side="left", padx=(0, 6))

        btn_excluir = BotaoGrande(
            acoes,
            "Excluir",
            comando=lambda i=indice: self._excluir(i),
            variante="perigo",
            height=34,
        )
        btn_excluir.pack(side="left")

    def _visualizar(self, escala: Escala) -> None:
        """Carrega a escala na tela principal de escala e fecha o modal."""
        if self.ao_selecionar_para_ver:
            self.ao_selecionar_para_ver(escala)
            self.destroy()

    def _copiar_whatsapp(self, escala: Escala, botao: BotaoGrande) -> None:
        """Gera o texto e envia para a área de transferência do Windows."""
        texto = gerar_texto_whatsapp(escala, self.dados)
        self.clipboard_clear()
        self.clipboard_append(texto)

        texto_original = botao.cget("text")
        botao.configure(text="✅ Copiado!")
        self.after(2000, lambda: botao.configure(text=texto_original))

    def _excluir(self, indice: int) -> None:
        """Pede confirmação e remove a escala do histórico."""
        confirmado = perguntar_sim_nao(
            self,
            "Excluir escala",
            "Tem certeza que deseja excluir esta escala confirmada?\n\n"
            "Todos os contadores de justiça serão recalculados automaticamente sem os dados desta escala.",
        )
        if confirmado:
            excluir_escala(self.dados, indice)
            self.ao_mudar()
            self._atualizar_lista()
