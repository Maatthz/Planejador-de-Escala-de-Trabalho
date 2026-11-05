"""Aba principal de geração, edição e confirmação de Escalas de Plantão.

Permite selecionar o período, adicionar feriados, gerar a escala de plantão,
trocar integrantes manualmente, validar regras, confirmar e copiar para o WhatsApp.
"""

from collections.abc import Callable
from datetime import date, timedelta
import tkinter as tk
import customtkinter as ctk

from src.escala.datas import (
    formatar_data,
    formatar_dia_completo,
    inicio_da_semana,
    ler_data,
)
from src.escala.edicao import (
    confirmar_rascunho,
    escalas_sobrepostas,
    pessoas_para_troca,
    trocar_pessoa,
    validar_escala,
)
from src.escala.exportar import gerar_texto_whatsapp
from src.escala.gerador import descrever_plantao, gerar_escala
from src.escala.interface.componentes import (
    COR_AVISO_FUNDO,
    COR_AVISO_TEXTO,
    COR_BORDA,
    COR_CARTAO,
    COR_ESTRELA,
    COR_FUNDO,
    COR_PERIGO,
    COR_PRIMARIA,
    COR_PRIMARIA_HOVER,
    COR_SECUNDARIA,
    COR_SECUNDARIA_HOVER,
    COR_SECUNDARIA_TEXTO,
    COR_SUCESSO,
    COR_SUCESSO_FUNDO,
    COR_SUCESSO_HOVER,
    COR_SUCESSO_TEXTO,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_AJUDA,
    FONTE_BOTAO,
    FONTE_CORPO,
    FONTE_SUBTITULO,
    FONTE_TITULO,
    BotaoGrande,
    CartaoFrame,
    RotuloSimples,
    configurar_janela_modal,
    configurar_rolagem_suave,
    congelar_redesenho,
    mostrar_erro,
    mostrar_info,
    perguntar_sim_nao,
)
from src.escala.interface.janela_feriado import JanelaFeriado
from src.escala.interface.janela_historico import JanelaHistorico
from src.escala.interface.janela_justica import JanelaJustica
from src.escala.modelos import DadosDoPrograma, ErroEscala, Escala, Plantao


class TelaEscala(ctk.CTkFrame):
    """Visualização e controle da Escala de Plantão (Aba Escala)."""

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

        # Data de início padrão: segunda-feira desta semana
        self.data_inicio: date = inicio_da_semana(date.today())
        self._modo_periodo: str = "esta"
        # Escala ativa sendo exibida (pode ser o rascunho ou uma do histórico)
        self.escala_ativa: Escala | None = self.dados.rascunho

        # Cache de estrutura e estado para reuso de widgets in-place (sem destroy repetido)
        self._estado_faixa_status: tuple | None = ("__inicial__",)
        self._estrutura_plantoes: tuple[int, ...] | str | None = None
        self._cartoes_plantoes: list[dict] = []

        self._construir_interface()
        if inicializar_agora:
            self.atualizar_tela()

    def _construir_interface(self) -> None:
        """Monta a barra superior de controles, área rolável e rodapé com botões de ação."""
        self._construir_barra_controle()

        # Faixa de status e avisos
        self.faixa_status = ctk.CTkFrame(self, fg_color="transparent")
        self.faixa_status.pack(fill="x", padx=20, pady=(0, 6))

        # Área central rolável para os cartões de plantão
        self.scroll_plantoes = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_plantoes.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        configurar_rolagem_suave(self.scroll_plantoes)

        # Rodapé com ações
        self._construir_rodape()
        self._atualizar_destaque_botoes_periodo("esta")

    def _construir_barra_controle(self) -> None:
        """Barra com botões de período, seletor de semanas, feriados e botão Gerar."""
        barra = CartaoFrame(self)
        barra.pack(fill="x", padx=20, pady=(16, 10))

        linha = ctk.CTkFrame(barra, fg_color="transparent")
        linha.pack(fill="x", padx=16, pady=12)

        # Botões de escolha do período
        lbl_per = ctk.CTkLabel(linha, text="Período:", font=FONTE_SUBTITULO, text_color=COR_TEXTO)
        lbl_per.pack(side="left", padx=(0, 8))

        self.btn_esta_semana = BotaoGrande(
            linha,
            "Esta semana",
            comando=self._selecionar_esta_semana,
            variante="secundaria",
            height=36,
        )
        self.btn_esta_semana.pack(side="left", padx=(0, 6))

        self.btn_prox_semana = BotaoGrande(
            linha,
            "Próxima semana",
            comando=self._selecionar_proxima_semana,
            variante="secundaria",
            height=36,
        )
        self.btn_prox_semana.pack(side="left", padx=(0, 6))

        self.btn_outra_data = BotaoGrande(
            linha,
            "Escolher data…",
            comando=self._abrir_dialogo_escolher_data,
            variante="secundaria",
            height=36,
        )
        self.btn_outra_data.pack(side="left", padx=(0, 10))

        # Rótulo de intervalo de datas visível e claro
        self.lbl_periodo_datas = ctk.CTkLabel(
            linha,
            text="",
            font=("Segoe UI", 14, "bold"),
            text_color=COR_PRIMARIA,
        )
        self.lbl_periodo_datas.pack(side="left", padx=(0, 14))

        # Quantidade de semanas
        lbl_sem = ctk.CTkLabel(linha, text="Semanas:", font=FONTE_CORPO, text_color=COR_TEXTO)
        lbl_sem.pack(side="left", padx=(0, 4))

        self.combo_semanas = ctk.CTkOptionMenu(
            linha,
            values=["1", "2", "3", "4"],
            width=65,
            height=36,
            font=FONTE_CORPO,
            command=lambda _: self._atualizar_rotulo_periodo(),
        )
        self.combo_semanas.set(str(self.dados.configuracao.semanas_por_geracao))
        self.combo_semanas.pack(side="left", padx=(0, 14))

        # Feriados
        btn_feriado = BotaoGrande(
            linha,
            "+ Feriado",
            comando=self._abrir_janela_feriados,
            variante="secundaria",
            height=36,
        )
        btn_feriado.pack(side="left", padx=(0, 14))

        # Botão principal Gerar Escala
        self.btn_gerar = BotaoGrande(
            linha,
            "Gerar escala",
            comando=self._executar_geracao,
            variante="primaria",
            height=40,
        )
        self.btn_gerar.pack(side="right")

    def _construir_rodape(self) -> None:
        """Rodapé com botões de quadro de justiça, histórico, confirmação e copiar WhatsApp."""
        rodape = CartaoFrame(self)
        rodape.pack(fill="x", padx=20, pady=(0, 16))

        linha = ctk.CTkFrame(rodape, fg_color="transparent")
        linha.pack(fill="x", padx=16, pady=10)

        # Lado esquerdo — consultas auxiliares
        btn_justica = BotaoGrande(
            linha,
            "📊 Quadro de justiça",
            comando=self._abrir_quadro_justica,
            variante="secundaria",
            height=36,
        )
        btn_justica.pack(side="left", padx=(0, 8))

        btn_hist = BotaoGrande(
            linha,
            "📜 Escalas anteriores",
            comando=self._abrir_historico,
            variante="secundaria",
            height=36,
        )
        btn_hist.pack(side="left")

        # Lado direito — ações finais
        self.btn_copiar = BotaoGrande(
            linha,
            "📋 Copiar para WhatsApp",
            comando=self._copiar_whatsapp,
            variante="sucesso",
            height=40,
        )
        self.btn_copiar.pack(side="right", padx=(8, 0))

        self.btn_confirmar = BotaoGrande(
            linha,
            "✅ Confirmar escala",
            comando=self._confirmar_escala_atual,
            variante="sucesso",
            height=40,
        )
        self.btn_confirmar.pack(side="right")

    def atualizar_tela(self) -> None:
        """Atualiza a exibição da escala ativa, faixas de status e avisos."""
        # Se houver rascunho e nenhuma outra escala selecionada, usa o rascunho
        if self.dados.rascunho is not None:
            self.escala_ativa = self.dados.rascunho
        elif self.escala_ativa is None and self.dados.escalas:
            self.escala_ativa = self.dados.escalas[-1]

        self._atualizar_faixa_status()
        self._atualizar_cartoes_plantoes()

    def _atualizar_faixa_status(self) -> None:
        """Renderiza a faixa de status (rascunho ou confirmada) e avisos de validação."""
        if self.escala_ativa is None:
            novo_estado = None
            avisos: tuple[str, ...] = ()
        else:
            avisos = tuple(validar_escala(self.escala_ativa, self.dados))
            novo_estado = (self.escala_ativa.confirmada, avisos)

        if self._estado_faixa_status == novo_estado:
            return
        self._estado_faixa_status = novo_estado

        for filho in self.faixa_status.winfo_children():
            filho.destroy()

        if self.escala_ativa is None:
            return

        # Faixa de Rascunho vs Confirmada
        if not self.escala_ativa.confirmada:
            faixa = ctk.CTkFrame(self.faixa_status, fg_color=COR_AVISO_FUNDO, corner_radius=8)
            faixa.pack(fill="x", pady=(0, 6))
            lbl = ctk.CTkLabel(
                faixa,
                text="⚠️ Rascunho — esta escala ainda não está valendo. Clique em 'Confirmar escala' para salvar no histórico.",
                font=FONTE_CORPO,
                text_color=COR_AVISO_TEXTO,
            )
            lbl.pack(padx=16, pady=8, anchor="w")
        else:
            faixa = ctk.CTkFrame(self.faixa_status, fg_color=COR_SUCESSO_FUNDO, corner_radius=8)
            faixa.pack(fill="x", pady=(0, 6))
            lbl = ctk.CTkLabel(
                faixa,
                text="✅ Escala confirmada e salva no histórico.",
                font=FONTE_CORPO,
                text_color=COR_SUCESSO_TEXTO,
            )
            lbl.pack(padx=16, pady=8, anchor="w")

        # Avisos de validação
        if avisos:
            caixa_aviso = ctk.CTkFrame(self.faixa_status, fg_color=COR_AVISO_FUNDO, corner_radius=8)
            caixa_aviso.pack(fill="x", pady=(0, 6))
            lbl_tit_aviso = ctk.CTkLabel(
                caixa_aviso,
                text="Atenção aos seguintes pontos nesta escala:",
                font=FONTE_SUBTITULO,
                text_color=COR_AVISO_TEXTO,
            )
            lbl_tit_aviso.pack(padx=16, pady=(6, 2), anchor="w")

            for av in avisos:
                lbl_item = ctk.CTkLabel(
                    caixa_aviso,
                    text=f"• {av}",
                    font=FONTE_AJUDA,
                    text_color=COR_AVISO_TEXTO,
                )
                lbl_item.pack(padx=24, pady=1, anchor="w")
            ctk.CTkLabel(caixa_aviso, text="", height=4).pack()

    def _atualizar_cartoes_plantoes(self) -> None:
        """Renderiza ou atualiza in-place os cartões dos plantões e das duplas."""
        if self.escala_ativa is None:
            if self._estrutura_plantoes != "vazio":
                for filho in self.scroll_plantoes.winfo_children():
                    filho.destroy()
                self._cartoes_plantoes.clear()
                self._mostrar_estado_vazio()
                self._estrutura_plantoes = "vazio"
            return

        estrutura_atual = tuple(len(p.duplas) for p in self.escala_ativa.plantoes)
        if self._estrutura_plantoes != estrutura_atual:
            with congelar_redesenho(self.scroll_plantoes):
                for filho in self.scroll_plantoes.winfo_children():
                    filho.destroy()
                self._cartoes_plantoes = [
                    self._criar_esqueleto_cartao_plantao(qtd_duplas)
                    for qtd_duplas in estrutura_atual
                ]
                self._estrutura_plantoes = estrutura_atual
                try:
                    self.scroll_plantoes._parent_canvas.yview_moveto(0.0)
                except Exception:
                    pass

        for idx_plantao, (cartao_info, plantao) in enumerate(
            zip(self._cartoes_plantoes, self.escala_ativa.plantoes)
        ):
            self._preencher_cartao_plantao(cartao_info, plantao, idx_plantao)

    def _mostrar_estado_vazio(self) -> None:
        """Orienta o usuário a gerar uma escala quando nenhuma está ativa."""
        cartao_vazio = CartaoFrame(self.scroll_plantoes)
        cartao_vazio.pack(fill="x", pady=40, ipady=40)

        lbl = ctk.CTkLabel(
            cartao_vazio,
            text="Nenhuma escala gerada no momento.\n\nEscolha o período na barra acima e clique em 'Gerar escala'.",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO_SUAVE,
            justify="center",
        )
        lbl.pack(expand=True)

    def _criar_esqueleto_cartao_plantao(self, qtd_duplas: int) -> dict:
        """Instancia os widgets estruturais de um plantão uma única vez para reuso in-place."""
        cartao = CartaoFrame(self.scroll_plantoes)
        cartao.pack(fill="x", pady=6)

        topo = ctk.CTkFrame(cartao, fg_color=COR_FUNDO, corner_radius=8)
        topo.pack(fill="x", padx=12, pady=(12, 8))

        lbl_tit = RotuloSimples(
            topo,
            text="",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            fg_color=COR_FUNDO,
            anchor="w",
        )
        lbl_tit.pack(side="left", padx=12, pady=8)

        lbl_resumo = RotuloSimples(
            topo,
            text="",
            font=("Segoe UI", 12),
            text_color=COR_TEXTO_SUAVE,
            fg_color=COR_FUNDO,
        )
        lbl_resumo.pack(side="right", padx=12, pady=8)

        frame_grid = tk.Frame(cartao, bg=COR_CARTAO, bd=0, highlightthickness=0)
        frame_grid.pack(fill="x", padx=12, pady=(2, 10))
        frame_grid.grid_columnconfigure(0, weight=1, uniform="col_dupla")
        frame_grid.grid_columnconfigure(1, weight=1, uniform="col_dupla")

        slots: list[dict] = []
        for num_dupla in range(1, qtd_duplas + 1):
            card_dupla = ctk.CTkFrame(
                frame_grid,
                fg_color=COR_FUNDO,
                border_width=0,
                corner_radius=8,
            )

            if qtd_duplas == 1:
                card_dupla.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=4, pady=4)
            else:
                linha_idx = (num_dupla - 1) // 2
                col_idx = (num_dupla - 1) % 2
                if num_dupla == qtd_duplas and col_idx == 0:
                    card_dupla.grid(row=linha_idx, column=0, columnspan=2, sticky="nsew", padx=4, pady=4)
                else:
                    card_dupla.grid(row=linha_idx, column=col_idx, sticky="nsew", padx=4, pady=4)

            lbl_num = RotuloSimples(
                card_dupla,
                text=f"{num_dupla}.",
                font=("Segoe UI", 13, "bold"),
                text_color=COR_TEXTO_SUAVE,
                fg_color=COR_FUNDO,
            )
            lbl_num.pack(side="left", padx=(8, 4), pady=6)

            btn_a = ctk.CTkButton(
                card_dupla,
                text="",
                fg_color=COR_CARTAO,
                hover_color=COR_SECUNDARIA_HOVER,
                text_color=COR_TEXTO,
                font=("Segoe UI", 14, "bold"),
                height=34,
                anchor="w",
            )
            btn_a.pack(side="left", fill="x", expand=True, padx=(2, 2), pady=4)

            lbl_est_a = RotuloSimples(
                card_dupla,
                text="",
                font=("Segoe UI", 15, "bold"),
                text_color=COR_ESTRELA,
                fg_color=COR_FUNDO,
            )
            lbl_est_a.pack(side="left", padx=(0, 4), pady=4)

            lbl_sep = RotuloSimples(
                card_dupla,
                text="&",
                font=FONTE_AJUDA,
                text_color=COR_TEXTO_SUAVE,
                fg_color=COR_FUNDO,
            )
            lbl_sep.pack(side="left", padx=4, pady=6)

            btn_b = ctk.CTkButton(
                card_dupla,
                text="",
                fg_color=COR_CARTAO,
                hover_color=COR_SECUNDARIA_HOVER,
                text_color=COR_TEXTO,
                font=("Segoe UI", 14, "bold"),
                height=34,
                anchor="w",
            )
            btn_b.pack(side="left", fill="x", expand=True, padx=(2, 2), pady=4)

            lbl_est_b = RotuloSimples(
                card_dupla,
                text="",
                font=("Segoe UI", 15, "bold"),
                text_color=COR_ESTRELA,
                fg_color=COR_FUNDO,
            )
            lbl_est_b.pack(side="left", padx=(0, 6), pady=4)

            slots.append(
                {
                    "btn_a": btn_a,
                    "lbl_est_a": lbl_est_a,
                    "estado_a": None,
                    "btn_b": btn_b,
                    "lbl_est_b": lbl_est_b,
                    "estado_b": None,
                }
            )

        return {
            "cartao": cartao,
            "topo": topo,
            "lbl_tit": lbl_tit,
            "lbl_resumo": lbl_resumo,
            "estado_cabecalho": None,
            "slots": slots,
        }

    def _preencher_cartao_plantao(self, cartao_info: dict, plantao: Plantao, idx_plantao: int) -> None:
        """Atualiza in-place apenas os textos e comandos que mudaram no cartão do plantão."""
        cor_topo = COR_AVISO_FUNDO if plantao.eh_feriado else COR_FUNDO
        dia_txt = formatar_dia_completo(plantao.data)
        per_txt = plantao.periodo.capitalize()
        fer_txt = f" (Feriado: {plantao.nome_feriado})" if plantao.eh_feriado and plantao.nome_feriado else ""
        texto_tit = f"📅 {dia_txt} — {per_txt}{fer_txt}"

        qtd_duplas = len(plantao.duplas)
        resumo_duplas = (
            f"{qtd_duplas} duplas • Clique em um nome para trocar"
            if qtd_duplas != 1
            else "1 dupla • Clique em um nome para trocar"
        )
        estado_cabecalho = (cor_topo, texto_tit, resumo_duplas)
        if cartao_info["estado_cabecalho"] != estado_cabecalho:
            cartao_info["topo"].configure(fg_color=cor_topo)
            cartao_info["lbl_tit"].configure(text=texto_tit, fg_color=cor_topo)
            cartao_info["lbl_resumo"].configure(text=resumo_duplas, fg_color=cor_topo)
            cartao_info["estado_cabecalho"] = estado_cabecalho

        for slot, dupla in zip(cartao_info["slots"], plantao.duplas):
            p_a = self.dados.buscar_pessoa(dupla.pessoa_a)
            p_b = self.dados.buscar_pessoa(dupla.pessoa_b)
            nome_a = p_a.nome if p_a else f"ID {dupla.pessoa_a}"
            exp_a = bool(p_a and p_a.experiente)
            nome_b = p_b.nome if p_b else f"ID {dupla.pessoa_b}"
            exp_b = bool(p_b and p_b.experiente)

            estado_a = (idx_plantao, dupla.pessoa_a, nome_a, exp_a)
            if slot["estado_a"] != estado_a:
                slot["btn_a"].configure(
                    text=nome_a,
                    command=lambda ip=idx_plantao, sa=dupla.pessoa_a: self._abrir_dialogo_troca(ip, sa),
                )
                slot["lbl_est_a"].configure(text="★" if exp_a else "")
                slot["lbl_est_a"].bind(
                    "<Button-1>",
                    lambda _, ip=idx_plantao, sa=dupla.pessoa_a: self._abrir_dialogo_troca(ip, sa),
                )
                slot["estado_a"] = estado_a

            estado_b = (idx_plantao, dupla.pessoa_b, nome_b, exp_b)
            if slot["estado_b"] != estado_b:
                slot["btn_b"].configure(
                    text=nome_b,
                    command=lambda ip=idx_plantao, sb=dupla.pessoa_b: self._abrir_dialogo_troca(ip, sb),
                )
                slot["lbl_est_b"].configure(text="★" if exp_b else "")
                slot["lbl_est_b"].bind(
                    "<Button-1>",
                    lambda _, ip=idx_plantao, sb=dupla.pessoa_b: self._abrir_dialogo_troca(ip, sb),
                )
                slot["estado_b"] = estado_b

    def _abrir_dialogo_troca(self, indice_plantao: int, id_sai: int) -> None:
        """Abre modal com lista de opções para substituir uma pessoa no plantão."""
        if self.escala_ativa is None:
            return

        pessoa_sai = self.dados.buscar_pessoa(id_sai)
        nome_sai = pessoa_sai.nome if pessoa_sai else f"ID {id_sai}"

        janela = ctk.CTkToplevel(self)
        configurar_janela_modal(janela, self.winfo_toplevel(), f"Substituir {nome_sai}", 540, 480)

        lbl_tit = ctk.CTkLabel(
            janela,
            text=f"Escolha quem entrará no lugar de {nome_sai}:",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
        )
        lbl_tit.pack(padx=24, pady=(20, 10), anchor="w")

        scroll = ctk.CTkScrollableFrame(janela, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        configurar_rolagem_suave(scroll)

        opcoes = pessoas_para_troca(self.escala_ativa, indice_plantao, self.dados)
        for pessoa_entra, obs in opcoes:
            cartao_opcao = CartaoFrame(scroll)
            cartao_opcao.pack(fill="x", pady=3)

            lbl_nome = ctk.CTkLabel(
                cartao_opcao,
                text=pessoa_entra.nome,
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
            )
            lbl_nome.pack(side="left", padx=12, pady=8)

            if obs:
                lbl_obs = ctk.CTkLabel(
                    cartao_opcao,
                    text=f"({obs})",
                    font=FONTE_AJUDA,
                    text_color=COR_AVISO_TEXTO,
                )
                lbl_obs.pack(side="left", padx=6)

            btn_escolher = BotaoGrande(
                cartao_opcao,
                "Escolher",
                comando=lambda pe=pessoa_entra: self._efetivar_troca(janela, indice_plantao, id_sai, pe.id),
                variante="secundaria",
                height=30,
            )
            btn_escolher.pack(side="right", padx=12)

    def _efetivar_troca(self, janela: ctk.CTkToplevel, indice_plantao: int, id_sai: int, id_entra: int) -> None:
        """Executa trocar_pessoa, trata erros e avisos, e atualiza tela."""
        if self.escala_ativa is None:
            return

        try:
            avisos = trocar_pessoa(self.escala_ativa, indice_plantao, id_sai, id_entra, self.dados)
            janela.destroy()
            self.ao_mudar()

            if avisos:
                mostrar_info(self, "\n".join(avisos))
        except ErroEscala as erro:
            mostrar_erro(janela, str(erro))

    def _executar_geracao(self) -> None:
        """Gera nova proposta de escala a partir dos parâmetros selecionados."""
        try:
            qtd_sem = int(self.combo_semanas.get())
        except ValueError:
            qtd_sem = 1

        try:
            nova_escala = gerar_escala(
                dados=self.dados,
                inicio=self.data_inicio,
                qtd_semanas=qtd_sem,
            )
            self.escala_ativa = nova_escala
            self.ao_mudar()
        except ErroEscala as erro:
            mostrar_erro(self, str(erro))

    def _confirmar_escala_atual(self) -> None:
        """Confirma o rascunho ativo e o salva definitivamente no histórico."""
        if self.dados.rascunho is None:
            mostrar_info(self, "Não há nenhum rascunho de escala para confirmar.")
            return

        sobrepostas = escalas_sobrepostas(self.dados, self.dados.rascunho)
        if sobrepostas:
            confirmado = perguntar_sim_nao(
                self,
                "Substituir escala existente",
                "Já existem escalas confirmadas no histórico com datas em comum com este rascunho.\n\n"
                "Confirmar agora irá substituir as escalas anteriores nessas datas. Deseja continuar?",
            )
            if not confirmado:
                return

        confirmar_rascunho(self.dados)
        self.escala_ativa = self.dados.escalas[-1] if self.dados.escalas else None
        self.ao_mudar()

    def _copiar_whatsapp(self) -> None:
        """Gera o texto da escala atual e copia para a área de transferência."""
        if self.escala_ativa is None:
            mostrar_info(self, "Gere ou selecione uma escala antes de copiar.")
            return

        texto = gerar_texto_whatsapp(self.escala_ativa, self.dados)
        self.clipboard_clear()
        self.clipboard_append(texto)

        texto_original = self.btn_copiar.cget("text")
        self.btn_copiar.configure(text="✅ Copiado!")
        self.after(2000, lambda: self.btn_copiar.configure(text=texto_original))

    def _atualizar_destaque_botoes_periodo(self, modo: str = "esta") -> None:
        """Atualiza cores dos botões de período e texto descritivo do intervalo de datas."""
        self._modo_periodo = modo
        botoes = {
            "esta": self.btn_esta_semana,
            "proxima": self.btn_prox_semana,
            "outra": self.btn_outra_data,
        }
        for chave, btn in botoes.items():
            if chave == modo:
                btn.configure(
                    fg_color=COR_PRIMARIA,
                    text_color="#FFFFFF",
                    hover_color=COR_PRIMARIA_HOVER,
                )
            else:
                btn.configure(
                    fg_color=COR_SECUNDARIA,
                    text_color=COR_SECUNDARIA_TEXTO,
                    hover_color=COR_SECUNDARIA_HOVER,
                )
        self._atualizar_rotulo_periodo()

    def _atualizar_rotulo_periodo(self) -> None:
        """Atualiza o rótulo com as datas do período selecionado."""
        try:
            qtd_sem = int(self.combo_semanas.get())
        except (ValueError, AttributeError):
            qtd_sem = 1
        fim = self.data_inicio + timedelta(days=7 * qtd_sem - 1)
        if hasattr(self, "lbl_periodo_datas"):
            self.lbl_periodo_datas.configure(
                text=f"📅 {formatar_data(self.data_inicio)} a {formatar_data(fim)}"
            )

    def _selecionar_esta_semana(self) -> None:
        """Ajusta a data de início para a segunda-feira atual."""
        self.data_inicio = inicio_da_semana(date.today())
        self.btn_outra_data.configure(text="Escolher data…")
        self._atualizar_destaque_botoes_periodo("esta")

    def _selecionar_proxima_semana(self) -> None:
        """Ajusta a data de início para a segunda-feira da próxima semana."""
        self.data_inicio = inicio_da_semana(date.today()) + timedelta(days=7)
        self.btn_outra_data.configure(text="Escolher data…")
        self._atualizar_destaque_botoes_periodo("proxima")

    def _abrir_dialogo_escolher_data(self) -> None:
        """Abre modal para digitar data customizada de início."""
        janela = ctk.CTkToplevel(self)
        configurar_janela_modal(janela, self.winfo_toplevel(), "Escolher data de início", 380, 220)

        lbl = ctk.CTkLabel(janela, text="Data de início (dd/mm/aaaa):", font=FONTE_CORPO, text_color=COR_TEXTO)
        lbl.pack(padx=24, pady=(20, 6), anchor="w")

        campo = ctk.CTkEntry(janela, placeholder_text="Ex.: 07/11/2026", height=36)
        campo.insert(0, formatar_data(self.data_inicio) + f"/{self.data_inicio.year}")
        campo.pack(fill="x", padx=24, pady=(0, 20))

        def _salvar():
            try:
                data_lida = ler_data(campo.get())
                self.data_inicio = data_lida
                self.btn_outra_data.configure(text=formatar_data(data_lida))
                self._atualizar_destaque_botoes_periodo("outra")
                janela.destroy()
            except ErroEscala as err:
                mostrar_erro(janela, str(err))

        campo.bind("<Return>", lambda _: _salvar())

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack(fill="x", padx=24, pady=(0, 16))

        btn_canc = BotaoGrande(botoes, "Cancelar", janela.destroy, variante="secundaria", height=36)
        btn_canc.pack(side="left", expand=True, padx=(0, 6))

        btn_ok = BotaoGrande(botoes, "OK", _salvar, variante="primaria", height=36)
        btn_ok.pack(side="right", expand=True, padx=(6, 0))

    def _abrir_janela_feriados(self) -> None:
        """Abre o diálogo de feriados."""
        JanelaFeriado(
            pai=self.winfo_toplevel(),
            dados=self.dados,
            ao_mudar=self.ao_mudar,
            data_sugerida=self.data_inicio,
        )

    def _abrir_quadro_justica(self) -> None:
        """Abre o diálogo do Quadro de Justiça."""
        JanelaJustica(pai=self.winfo_toplevel(), dados=self.dados)

    def _abrir_historico(self) -> None:
        """Abre o diálogo do Histórico de escalas anteriores."""
        JanelaHistorico(
            pai=self.winfo_toplevel(),
            dados=self.dados,
            ao_mudar=self.ao_mudar,
            ao_selecionar_para_ver=self._visualizar_escala_historico,
        )

    def _visualizar_escala_historico(self, escala: Escala) -> None:
        """Define a escala do histórico como a ativa na tela."""
        self.escala_ativa = escala
        self.atualizar_tela()
