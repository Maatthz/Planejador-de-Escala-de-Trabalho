"""Diálogo modal com o Quadro de Justiça da equipe.

Apresenta a fila ordenada de prioridade dos integrantes, distinguindo
plantões reais realizados de compensações pelo piso de ausências.
"""

import customtkinter as ctk

from src.escala.datas import formatar_data
from src.escala.historico import quadro_de_justica
from src.escala.interface.componentes import (
    COR_AVISO_FUNDO,
    COR_AVISO_TEXTO,
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
    configurar_rolagem_suave,
)
from src.escala.modelos import DadosDoPrograma


class JanelaJustica(ctk.CTkToplevel):
    """Visualização da fila de prioridade e contadores de justiça."""

    def __init__(self, pai, dados: DadosDoPrograma) -> None:
        super().__init__(pai)
        self.dados = dados

        configurar_janela_modal(self, pai, "📊 Quadro de Justiça", 760, 560)
        self._construir_interface()

    def _construir_interface(self) -> None:
        """Monta o cabeçalho explicativo e a tabela rolável de justiça."""
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=24, pady=(20, 10))

        lbl_tit = ctk.CTkLabel(
            topo,
            text="📊 Quadro de Justiça e Prioridade",
            font=FONTE_TITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_tit.pack(fill="x")

        lbl_desc = ctk.CTkLabel(
            topo,
            text="As pessoas no topo da lista têm prioridade para entrar na próxima escala (contando apenas escalas já confirmadas).",
            font=FONTE_CORPO,
            text_color=COR_TEXTO_SUAVE,
            anchor="w",
            wraplength=700,
            justify="left",
        )
        lbl_desc.pack(fill="x", pady=(4, 0))

        # Tabela com Cabeçalho e Conteúdo
        tabela_frame = CartaoFrame(self)
        tabela_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Cabeçalho da tabela
        cab_tab = ctk.CTkFrame(tabela_frame, fg_color=COR_BORDA, height=36, corner_radius=6)
        cab_tab.pack(fill="x", padx=10, pady=(10, 4))
        cab_tab.pack_propagate(False)

        colunas = [
            ("Fila", 55),
            ("Nome", 180),
            ("Plantões Feitos", 110),
            ("Em Feriados", 95),
            ("Último Plantão", 115),
            ("Observação", 145),
        ]

        for nome, larg in colunas:
            lbl = ctk.CTkLabel(
                cab_tab,
                text=nome,
                font=FONTE_AJUDA,
                text_color=COR_TEXTO,
                width=larg,
                anchor="w",
            )
            lbl.pack(side="left", padx=4)

        # Linhas roláveis
        scroll_linhas = ctk.CTkScrollableFrame(tabela_frame, fg_color="transparent")
        scroll_linhas.pack(fill="both", expand=True, padx=6, pady=(0, 10))
        configurar_rolagem_suave(scroll_linhas)

        linhas = quadro_de_justica(self.dados)
        if not linhas:
            lbl_vazio = ctk.CTkLabel(
                scroll_linhas,
                text="Nenhuma pessoa ativa na equipe.",
                font=FONTE_CORPO,
                text_color=COR_TEXTO_SUAVE,
            )
            lbl_vazio.pack(pady=40)
            return

        for idx, item in enumerate(linhas):
            cor_linha = COR_FUNDO if idx % 2 == 0 else "transparent"
            linha = ctk.CTkFrame(scroll_linhas, fg_color=cor_linha, height=34, corner_radius=6)
            linha.pack(fill="x", pady=2)

            # 1. Posição na fila
            lbl_pos = ctk.CTkLabel(
                linha,
                text=f"{item.posicao}º",
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
                width=55,
                anchor="w",
            )
            lbl_pos.pack(side="left", padx=4)

            # 2. Nome (com estrela se experiente)
            estrela = " ⭐" if item.pessoa.experiente else ""
            lbl_nome = ctk.CTkLabel(
                linha,
                text=f"{item.pessoa.nome}{estrela}",
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
                width=180,
                anchor="w",
            )
            lbl_nome.pack(side="left", padx=4)

            # 3. Plantões reais
            lbl_plantoes = ctk.CTkLabel(
                linha,
                text=str(item.plantoes_reais),
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
                width=110,
                anchor="w",
            )
            lbl_plantoes.pack(side="left", padx=4)

            # 4. Feriados reais
            lbl_feriados = ctk.CTkLabel(
                linha,
                text=str(item.feriados_trabalhados),
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
                width=95,
                anchor="w",
            )
            lbl_feriados.pack(side="left", padx=4)

            # 5. Último plantão
            ult_texto = formatar_data(item.ultimo_plantao) if item.ultimo_plantao else "Nunca"
            lbl_ult = ctk.CTkLabel(
                linha,
                text=ult_texto,
                font=FONTE_CORPO,
                text_color=COR_TEXTO_SUAVE if not item.ultimo_plantao else COR_TEXTO,
                width=115,
                anchor="w",
            )
            lbl_ult.pack(side="left", padx=4)

            # 6. Observação (se recebeu piso)
            obs_texto = "Entrou/voltou empatado" if item.carga_justica > item.plantoes_reais else ""
            lbl_obs = ctk.CTkLabel(
                linha,
                text=obs_texto,
                font=FONTE_AJUDA,
                text_color=COR_AVISO_TEXTO if obs_texto else COR_TEXTO_SUAVE,
                width=145,
                anchor="w",
            )
            lbl_obs.pack(side="left", padx=4)

        btn_fechar = BotaoGrande(
            self,
            "Fechar",
            comando=self.destroy,
            variante="secundaria",
            height=36,
        )
        btn_fechar.pack(pady=(0, 16))
