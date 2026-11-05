"""Aba de gerenciamento de folgas, indisponibilidades e férias.

Permite selecionar integrantes da equipe e marcar ou desmarcar folgas
pontuais diretamente no calendário ou registrar intervalos contínuos de férias.
"""

from collections.abc import Callable
from datetime import date, timedelta
import customtkinter as ctk

from src.escala.datas import formatar_data, formatar_dia_completo, ler_data
from src.escala.interface.componentes import (
    COR_AVISO_FUNDO,
    COR_AVISO_TEXTO,
    COR_BORDA,
    COR_CARTAO,
    COR_FUNDO,
    COR_PRIMARIA,
    COR_PRIMARIA_HOVER,
    COR_SECUNDARIA,
    COR_SECUNDARIA_HOVER,
    COR_SECUNDARIA_TEXTO,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_AJUDA,
    FONTE_CORPO,
    FONTE_SUBTITULO,
    FONTE_TITULO,
    BotaoGrande,
    CalendarioMensal,
    CartaoFrame,
    configurar_janela_modal,
    configurar_rolagem_suave,
    mostrar_erro,
)
from src.escala.modelos import DadosDoPrograma, ErroEscala, Pessoa


class TelaFolgas(ctk.CTkFrame):
    """Visualização e controle de folgas e ausências (Aba Folgas)."""

    def __init__(
        self,
        master,
        dados: DadosDoPrograma,
        ao_mudar: Callable[[], None],
        inicializar_agora: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(master=master, fg_color=COR_FUNDO, **kwargs)
        self.dados = dados
        self.ao_mudar = ao_mudar
        self.pessoa_selecionada: Pessoa | None = None
        self._id_botao_selecionado: int | None = None
        self._botoes_pessoas: dict[int, ctk.CTkButton] = {}
        self._datas_renderizadas: tuple[date, ...] | None = None

        self._construir_layout()
        if inicializar_agora:
            self.atualizar_tela()

    def _construir_layout(self) -> None:
        """Divide a tela em duas colunas: lista de integrantes à esquerda e detalhes à direita."""
        self.grid_columnconfigure(0, weight=0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Painel Esquerdo — Lista de Integrantes
        self.painel_esquerdo = CartaoFrame(self)
        self.painel_esquerdo.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        lbl_tit_esq = ctk.CTkLabel(
            self.painel_esquerdo,
            text="👥 Integrantes da Equipe",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_tit_esq.pack(fill="x", padx=16, pady=(16, 4))

        lbl_sub_esq = ctk.CTkLabel(
            self.painel_esquerdo,
            text="Selecione para ver e marcar folgas:",
            font=FONTE_AJUDA,
            text_color=COR_TEXTO_SUAVE,
            anchor="w",
        )
        lbl_sub_esq.pack(fill="x", padx=16, pady=(0, 10))

        self.scroll_pessoas = ctk.CTkScrollableFrame(self.painel_esquerdo, fg_color="transparent")
        self.scroll_pessoas.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        configurar_rolagem_suave(self.scroll_pessoas)

        # Painel Direito — Estrutura persistente (evita recriação ao trocar de pessoa)
        self.painel_direito = ctk.CTkFrame(self, fg_color=COR_FUNDO)
        self.painel_direito.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.painel_direito.grid_rowconfigure(0, weight=1)
        self.painel_direito.grid_columnconfigure(0, weight=1)
        self.painel_direito.grid_propagate(False)

        # 1. Estado vazio persistente à direita
        self.frame_vazio_direito = CartaoFrame(self.painel_direito)
        self.frame_vazio_direito.grid(row=0, column=0, sticky="nsew")
        lbl_vazio = ctk.CTkLabel(
            self.frame_vazio_direito,
            text="Nenhuma pessoa selecionada.\n\nSelecione um integrante na lista à esquerda para visualizar,\nmarcar folgas individuais ou registrar períodos de férias.",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO_SUAVE,
            justify="center",
        )
        lbl_vazio.pack(expand=True)

        # 2. Conteúdo de folgas persistente à direita
        self.frame_conteudo_direito = ctk.CTkFrame(self.painel_direito, fg_color=COR_FUNDO)
        self.frame_conteudo_direito.grid(row=0, column=0, sticky="nsew")
        self.frame_vazio_direito.tkraise()

        topo = ctk.CTkFrame(self.frame_conteudo_direito, fg_color="transparent")
        topo.pack(fill="x", pady=(0, 12))

        self.lbl_nome_pessoa = ctk.CTkLabel(
            topo,
            text="",
            font=FONTE_TITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        self.lbl_nome_pessoa.pack(side="left", fill="x", expand=True)

        btn_ferias = BotaoGrande(
            topo,
            "Marcar período (férias)",
            comando=self._abrir_dialogo_ferias,
            variante="primaria",
            height=38,
        )
        btn_ferias.pack(side="right")

        scroll_conteudo = ctk.CTkScrollableFrame(self.frame_conteudo_direito, fg_color="transparent")
        scroll_conteudo.pack(fill="both", expand=True)
        configurar_rolagem_suave(scroll_conteudo)

        lbl_dica = ctk.CTkLabel(
            scroll_conteudo,
            text="Clique diretamente no dia do calendário para marcar ou desmarcar folga (vermelho = folga marcada):",
            font=FONTE_AJUDA,
            text_color=COR_TEXTO_SUAVE,
            anchor="w",
        )
        lbl_dica.pack(fill="x", pady=(0, 8))

        # Calendário persistente reutilizado in-place
        self.calendario = CalendarioMensal(
            scroll_conteudo,
            datas_marcadas=set(),
            ao_clicar=self._alternar_dia_folga,
        )
        self.calendario.pack(fill="x", pady=(0, 16))

        # Cartão de lista das datas registradas
        self.cartao_lista_datas = CartaoFrame(scroll_conteudo)
        self.cartao_lista_datas.pack(fill="x", pady=(0, 16))

        lbl_tit_lista = ctk.CTkLabel(
            self.cartao_lista_datas,
            text="Todas as folgas cadastradas:",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_tit_lista.pack(fill="x", padx=16, pady=(12, 8))

        self.container_linhas_datas = ctk.CTkFrame(self.cartao_lista_datas, fg_color="transparent")
        self.container_linhas_datas.pack(fill="x", padx=16, pady=(0, 8))

    def atualizar_tela(self) -> None:
        """Atualiza a lista de pessoas à esquerda e o painel de folgas à direita."""
        if self.pessoa_selecionada is not None:
            pessoa_atual = self.dados.buscar_pessoa(self.pessoa_selecionada.id)
            if pessoa_atual is None or not pessoa_atual.ativo:
                self.pessoa_selecionada = None

        self._atualizar_lista_pessoas()
        self._atualizar_painel_direito()

    def _atualizar_lista_pessoas(self) -> None:
        """Reconstrói ou atualiza in-place a lista de pessoas ativas com 1 único CTkButton por item."""
        ativas = self.dados.pessoas_ativas()
        if not ativas:
            for filho in self.scroll_pessoas.winfo_children():
                filho.destroy()
            self._botoes_pessoas.clear()
            lbl_vazio = ctk.CTkLabel(
                self.scroll_pessoas,
                text="Nenhuma pessoa ativa cadastrada.",
                font=FONTE_CORPO,
                text_color=COR_TEXTO_SUAVE,
            )
            lbl_vazio.pack(pady=20)
            return

        hoje = date.today()
        ids_ativas = [p.id for p in ativas]

        # Se a lista de botões já corresponde aos mesmos IDs, apenas atualiza quem mudou
        if list(self._botoes_pessoas.keys()) == ids_ativas:
            id_sel = self.pessoa_selecionada.id if self.pessoa_selecionada is not None else None
            for pessoa in ativas:
                btn = self._botoes_pessoas[pessoa.id]
                selecionada = (pessoa.id == id_sel)
                folgas_futuras = sum(1 for d in pessoa.indisponibilidades if d >= hoje)
                txt = f"  {pessoa.nome}   •   {folgas_futuras} folga(s)" if folgas_futuras > 0 else f"  {pessoa.nome}"
                cor_fg = COR_PRIMARIA if selecionada else COR_FUNDO
                if btn.cget("text") != txt or btn.cget("fg_color") != cor_fg:
                    btn.configure(
                        text=txt,
                        fg_color=cor_fg,
                        hover_color=COR_PRIMARIA_HOVER if selecionada else COR_BORDA,
                        text_color="#FFFFFF" if selecionada else COR_TEXTO,
                    )
            self._id_botao_selecionado = id_sel
            return

        # Reconstrói a lista de botões se a equipe mudou
        for filho in self.scroll_pessoas.winfo_children():
            filho.destroy()
        self._botoes_pessoas.clear()

        for pessoa in ativas:
            selecionada = (
                self.pessoa_selecionada is not None
                and self.pessoa_selecionada.id == pessoa.id
            )
            folgas_futuras = sum(1 for d in pessoa.indisponibilidades if d >= hoje)
            txt = f"  {pessoa.nome}   •   {folgas_futuras} folga(s)" if folgas_futuras > 0 else f"  {pessoa.nome}"

            item_btn = ctk.CTkButton(
                self.scroll_pessoas,
                text=txt,
                fg_color=COR_PRIMARIA if selecionada else COR_FUNDO,
                hover_color=COR_PRIMARIA_HOVER if selecionada else COR_BORDA,
                text_color="#FFFFFF" if selecionada else COR_TEXTO,
                corner_radius=8,
                height=40,
                anchor="w",
                font=FONTE_CORPO,
                command=lambda p=pessoa: self._selecionar_pessoa(p),
            )
            item_btn.pack(fill="x", pady=2, padx=4)
            self._botoes_pessoas[pessoa.id] = item_btn

        self._id_botao_selecionado = (
            self.pessoa_selecionada.id if self.pessoa_selecionada is not None else None
        )

    def _selecionar_pessoa(self, pessoa: Pessoa) -> None:
        """Seleciona uma pessoa atualizando apenas os 2 botões envolvidos e o painel direito."""
        id_anterior = self._id_botao_selecionado
        self.pessoa_selecionada = pessoa

        if not self._botoes_pessoas:
            self._atualizar_lista_pessoas()
        else:
            if id_anterior is not None and id_anterior != pessoa.id and id_anterior in self._botoes_pessoas:
                self._botoes_pessoas[id_anterior].configure(
                    fg_color=COR_FUNDO,
                    hover_color=COR_BORDA,
                    text_color=COR_TEXTO,
                )
            if pessoa.id in self._botoes_pessoas and id_anterior != pessoa.id:
                self._botoes_pessoas[pessoa.id].configure(
                    fg_color=COR_PRIMARIA,
                    hover_color=COR_PRIMARIA_HOVER,
                    text_color="#FFFFFF",
                )
            self._id_botao_selecionado = pessoa.id

        self._atualizar_painel_direito()

    def _atualizar_painel_direito(self) -> None:
        """Alterna entre estado vazio e conteúdo de folgas via tkraise, reaproveitando o calendário."""
        if self.pessoa_selecionada is None:
            self.frame_vazio_direito.tkraise()
            return

        self.lbl_nome_pessoa.configure(text=f"📅 Folgas de {self.pessoa_selecionada.nome}")
        self.calendario.atualizar_datas_marcadas(self.pessoa_selecionada.indisponibilidades)
        self._construir_lista_datas_registradas()
        self.frame_conteudo_direito.tkraise()

    def _construir_lista_datas_registradas(self) -> None:
        """Exibe os dias marcados organizados em ordem cronológica com botão de remoção."""
        datas_ordenadas = (
            tuple(sorted(self.pessoa_selecionada.indisponibilidades))
            if self.pessoa_selecionada
            else ()
        )
        if self._datas_renderizadas == datas_ordenadas:
            return
        self._datas_renderizadas = datas_ordenadas

        for filho in self.container_linhas_datas.winfo_children():
            filho.destroy()

        if not datas_ordenadas:
            lbl_nenhuma = ctk.CTkLabel(
                self.container_linhas_datas,
                text="Nenhuma folga cadastrada no momento.",
                font=FONTE_CORPO,
                text_color=COR_TEXTO_SUAVE,
                anchor="w",
            )
            lbl_nenhuma.pack(fill="x", pady=4)
            return
        for d in datas_ordenadas:
            linha = ctk.CTkFrame(self.container_linhas_datas, fg_color="transparent")
            linha.pack(fill="x", pady=2)

            lbl_data = ctk.CTkLabel(
                linha,
                text=f"• {formatar_dia_completo(d)}",
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
                anchor="w",
            )
            lbl_data.pack(side="left")

            btn_remover = BotaoGrande(
                linha,
                "Remover",
                comando=lambda dia=d: self._remover_dia(dia),
                variante="secundaria",
                height=26,
            )
            btn_remover.pack(side="right")

    def _alternar_dia_folga(self, dia: date) -> None:
        """Marca ou desmarca a data clicada no calendário para a pessoa atual."""
        if self.pessoa_selecionada is None:
            return

        if dia in self.pessoa_selecionada.indisponibilidades:
            self.pessoa_selecionada.indisponibilidades.remove(dia)
        else:
            self.pessoa_selecionada.indisponibilidades.add(dia)

        self.ao_mudar()

    def _remover_dia(self, dia: date) -> None:
        """Remove a folga selecionada."""
        if self.pessoa_selecionada and dia in self.pessoa_selecionada.indisponibilidades:
            self.pessoa_selecionada.indisponibilidades.remove(dia)
            self.ao_mudar()

    def _abrir_dialogo_ferias(self) -> None:
        """Abre janela modal para marcar intervalo de datas de ausência contínua."""
        if not self.pessoa_selecionada:
            return

        janela = ctk.CTkToplevel(self)
        configurar_janela_modal(
            janela,
            self.winfo_toplevel(),
            f"Marcar férias — {self.pessoa_selecionada.nome}",
            440,
            330,
        )

        lbl_desc = ctk.CTkLabel(
            janela,
            text="Informe o primeiro e o último dia do período de ausência:",
            font=FONTE_CORPO,
            text_color=COR_TEXTO,
        )
        lbl_desc.pack(padx=24, pady=(20, 14), anchor="w")

        lbl_inicio = ctk.CTkLabel(janela, text="Data inicial (dd/mm/aaaa):", font=FONTE_AJUDA)
        lbl_inicio.pack(padx=24, anchor="w")
        campo_inicio = ctk.CTkEntry(janela, placeholder_text="Ex.: 01/12/2026", height=36)
        campo_inicio.pack(fill="x", padx=24, pady=(2, 12))

        lbl_fim = ctk.CTkLabel(janela, text="Data final (dd/mm/aaaa):", font=FONTE_AJUDA)
        lbl_fim.pack(padx=24, anchor="w")
        campo_fim = ctk.CTkEntry(janela, placeholder_text="Ex.: 15/12/2026", height=36)
        campo_fim.pack(fill="x", padx=24, pady=(2, 20))

        def _confirmar():
            try:
                data_inicio = ler_data(campo_inicio.get())
                data_fim = ler_data(campo_fim.get())
                if data_fim < data_inicio:
                    mostrar_erro(
                        janela, "A data final deve ser igual ou posterior à data inicial."
                    )
                    return

                total_dias = (data_fim - data_inicio).days + 1
                for i in range(total_dias):
                    dia_folga = data_inicio + timedelta(days=i)
                    self.pessoa_selecionada.indisponibilidades.add(dia_folga)

                janela.destroy()
                self.ao_mudar()
            except ErroEscala as erro:
                mostrar_erro(janela, str(erro))

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack(fill="x", padx=24, pady=(0, 16))

        btn_cancelar = BotaoGrande(
            botoes,
            "Cancelar",
            janela.destroy,
            variante="secundaria",
            height=38,
        )
        btn_cancelar.pack(side="left", expand=True, padx=(0, 6))

        btn_salvar = BotaoGrande(
            botoes,
            "Marcar ausências",
            _confirmar,
            variante="primaria",
            height=38,
        )
        btn_salvar.pack(side="right", expand=True, padx=(6, 0))
