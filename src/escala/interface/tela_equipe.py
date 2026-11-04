"""Aba de gerenciamento da Equipe de plantão.

Permite listar os membros da equipe, adicionar novas pessoas,
editar nomes e nível de experiência, e desativar ou reativar integrantes.
"""

from collections.abc import Callable
from datetime import date
import customtkinter as ctk

from src.escala.interface.componentes import (
    COR_AVISO_FUNDO,
    COR_AVISO_TEXTO,
    COR_CARTAO,
    COR_FUNDO,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_CORPO,
    FONTE_SUBTITULO,
    FONTE_TITULO,
    BotaoGrande,
    CartaoFrame,
    configurar_janela_modal,
    mostrar_erro,
    perguntar_sim_nao,
)
from src.escala.modelos import DadosDoPrograma, ErroEscala, Pessoa


class TelaEquipe(ctk.CTkFrame):
    """Visualização e controle de membros da equipe (Aba Equipe)."""

    def __init__(
        self,
        master,
        dados: DadosDoPrograma,
        ao_mudar: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(master=master, fg_color=COR_FUNDO, **kwargs)
        self.dados = dados
        self.ao_mudar = ao_mudar

        self._construir_estrutura()
        self.atualizar_tela()

    def _construir_estrutura(self) -> None:
        """Monta o cabeçalho superior e o container com rolagem para os cartões."""
        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.pack(fill="x", padx=20, pady=(20, 10))

        self.lbl_contador = ctk.CTkLabel(
            cabecalho,
            text="",
            font=FONTE_TITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        self.lbl_contador.pack(side="left", fill="x", expand=True)

        btn_adicionar = BotaoGrande(
            cabecalho,
            "+ Adicionar pessoa",
            comando=self._abrir_dialogo_adicionar,
            variante="primaria",
            height=40,
        )
        btn_adicionar.pack(side="right")

        self.scroll_lista = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_lista.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def atualizar_tela(self) -> None:
        """Reconstrói os elementos visuais a partir de self.dados (fluxo unidirecional)."""
        for filho in self.scroll_lista.winfo_children():
            filho.destroy()

        ativas = [p for p in self.dados.pessoas if p.ativo]
        experientes = [p for p in ativas if p.experiente]
        self.lbl_contador.configure(
            text=f"👥 Equipe — {len(ativas)} pessoas ativas ({len(experientes)} experientes)"
        )

        if not self.dados.pessoas:
            self._mostrar_estado_vazio()
            return

        # Lista as pessoas: ativas primeiro em ordem alfabética, depois inativas
        pessoas_ordenadas = sorted(
            self.dados.pessoas,
            key=lambda p: (not p.ativo, p.nome.lower()),
        )

        for pessoa in pessoas_ordenadas:
            self._criar_cartao_pessoa(pessoa)

    def _mostrar_estado_vazio(self) -> None:
        """Exibe orientação amigável quando não há ninguém cadastrado."""
        cartao_vazio = CartaoFrame(self.scroll_lista)
        cartao_vazio.pack(fill="x", pady=20, padx=10, ipady=30)

        lbl = ctk.CTkLabel(
            cartao_vazio,
            text="Nenhuma pessoa cadastrada ainda.\nClique em '+ Adicionar pessoa' acima para começar.",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO_SUAVE,
            justify="center",
        )
        lbl.pack(expand=True)

    def _criar_cartao_pessoa(self, pessoa: Pessoa) -> None:
        """Cria uma linha/cartão com as informações e ações da pessoa."""
        cartao = CartaoFrame(self.scroll_lista)
        cartao.pack(fill="x", pady=5, padx=5)

        info_frame = ctk.CTkFrame(cartao, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=16, pady=10)

        # Nome com destaque
        cor_nome = COR_TEXTO if pessoa.ativo else COR_TEXTO_SUAVE
        lbl_nome = ctk.CTkLabel(
            info_frame,
            text=pessoa.nome,
            font=FONTE_SUBTITULO if pessoa.ativo else FONTE_CORPO,
            text_color=cor_nome,
            anchor="w",
        )
        lbl_nome.pack(side="left")

        # Selos de status
        if pessoa.experiente and pessoa.ativo:
            lbl_exp = ctk.CTkLabel(
                info_frame,
                text="⭐ Experiente",
                font=FONTE_CORPO,
                text_color=COR_AVISO_TEXTO,
                fg_color=COR_AVISO_FUNDO,
                corner_radius=6,
                padx=8,
                pady=2,
            )
            lbl_exp.pack(side="left", padx=12)

        if not pessoa.ativo:
            lbl_inativo = ctk.CTkLabel(
                info_frame,
                text="(Inativo)",
                font=FONTE_CORPO,
                text_color=COR_TEXTO_SUAVE,
            )
            lbl_inativo.pack(side="left", padx=12)

        # Botões de ação
        acoes_frame = ctk.CTkFrame(cartao, fg_color="transparent")
        acoes_frame.pack(side="right", padx=16, pady=10)

        btn_editar = BotaoGrande(
            acoes_frame,
            "Editar",
            comando=lambda p=pessoa: self._abrir_dialogo_editar(p),
            variante="secundaria",
            height=34,
        )
        btn_editar.pack(side="left", padx=(0, 8))

        if pessoa.ativo:
            btn_status = BotaoGrande(
                acoes_frame,
                "Desativar",
                comando=lambda p=pessoa: self._alternar_status(p),
                variante="secundaria",
                height=34,
            )
        else:
            btn_status = BotaoGrande(
                acoes_frame,
                "Reativar",
                comando=lambda p=pessoa: self._alternar_status(p),
                variante="secundaria",
                height=34,
            )
        btn_status.pack(side="left")

    def _alternar_status(self, pessoa: Pessoa) -> None:
        """Ativa ou desativa a pessoa. Ao reativar, ajusta data_entrada para hoje."""
        if pessoa.ativo:
            pessoa.ativo = False
        else:
            pessoa.ativo = True
            pessoa.data_entrada = date.today()

        self.ao_mudar()

    def _abrir_dialogo_adicionar(self) -> None:
        """Abre janela modal para cadastrar novo membro."""
        janela = ctk.CTkToplevel(self)
        configurar_janela_modal(janela, self.winfo_toplevel(), "Adicionar pessoa", 420, 260)

        lbl_instrucao = ctk.CTkLabel(
            janela,
            text="Nome completo ou de preferência:",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
        )
        lbl_instrucao.pack(anchor="w", padx=24, pady=(20, 6))

        campo_nome = ctk.CTkEntry(
            janela,
            placeholder_text="Ex.: Carlos Silva",
            font=FONTE_CORPO,
            height=38,
        )
        campo_nome.pack(fill="x", padx=24, pady=(0, 14))
        campo_nome.focus_set()

        var_experiente = ctk.BooleanVar(value=False)
        check_exp = ctk.CTkCheckBox(
            janela,
            text="Pessoa experiente no plantão",
            variable=var_experiente,
            font=FONTE_CORPO,
        )
        check_exp.pack(anchor="w", padx=24, pady=(0, 20))

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack(fill="x", padx=24, pady=(0, 16))

        def _salvar(event=None):
            nome = campo_nome.get().strip()
            try:
                self.dados.adicionar_pessoa(nome, experiente=var_experiente.get())
                janela.destroy()
                self.ao_mudar()
            except ErroEscala as erro:
                mostrar_erro(janela, str(erro))

        campo_nome.bind("<Return>", _salvar)

        btn_cancelar = BotaoGrande(
            botoes,
            "Cancelar",
            janela.destroy,
            variante="secundaria",
            height=38,
        )
        btn_cancelar.pack(side="left", expand=True, padx=(0, 6))

        btn_confirmar = BotaoGrande(
            botoes,
            "Adicionar",
            _salvar,
            variante="primaria",
            height=38,
        )
        btn_confirmar.pack(side="right", expand=True, padx=(6, 0))

    def _abrir_dialogo_editar(self, pessoa: Pessoa) -> None:
        """Abre janela modal para editar dados cadastrais ou excluir pessoa."""
        janela = ctk.CTkToplevel(self)
        configurar_janela_modal(janela, self.winfo_toplevel(), f"Editar — {pessoa.nome}", 440, 310)

        lbl_instrucao = ctk.CTkLabel(
            janela,
            text="Nome:",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
        )
        lbl_instrucao.pack(anchor="w", padx=24, pady=(20, 6))

        campo_nome = ctk.CTkEntry(janela, font=FONTE_CORPO, height=38)
        campo_nome.insert(0, pessoa.nome)
        campo_nome.pack(fill="x", padx=24, pady=(0, 14))

        var_experiente = ctk.BooleanVar(value=pessoa.experiente)
        check_exp = ctk.CTkCheckBox(
            janela,
            text="Pessoa experiente no plantão",
            variable=var_experiente,
            font=FONTE_CORPO,
        )
        check_exp.pack(anchor="w", padx=24, pady=(0, 20))

        def _salvar_edicao(event=None):
            novo_nome = campo_nome.get().strip()
            if not novo_nome:
                mostrar_erro(janela, "O nome não pode ser vazio.")
                return

            # Se mudou o nome, verifica se já existe outro igual
            if novo_nome.lower() != pessoa.nome.lower():
                for p in self.dados.pessoas:
                    if p.id != pessoa.id and p.nome.lower() == novo_nome.lower():
                        mostrar_erro(janela, f"Já existe uma pessoa cadastrada com o nome '{p.nome}'.")
                        return

            pessoa.nome = novo_nome
            pessoa.experiente = var_experiente.get()
            janela.destroy()
            self.ao_mudar()

        campo_nome.bind("<Return>", _salvar_edicao)

        # Botão de exclusão definitiva (só se não estiver em escalas confirmadas)
        def _excluir_definitivo():
            # Verifica se está em escalas confirmadas
            em_escala = any(
                pessoa.id in plantao.pessoas()
                for escala in self.dados.escalas
                if escala.confirmada
                for plantao in escala.plantoes
            )
            if em_escala:
                mostrar_erro(
                    janela,
                    f"Não é possível excluir '{pessoa.nome}' definitivamente porque ela já consta "
                    "no histórico de escalas confirmadas. Para que ela não participe das próximas, desative-a.",
                )
                return

            if perguntar_sim_nao(
                janela,
                "Excluir pessoa",
                f"Tem certeza que deseja remover '{pessoa.nome}' definitivamente da equipe?",
            ):
                self.dados.pessoas.remove(pessoa)
                janela.destroy()
                self.ao_mudar()

        btn_excluir = BotaoGrande(
            janela,
            "Excluir pessoa do cadastro",
            _excluir_definitivo,
            variante="perigo",
            height=34,
        )
        btn_excluir.pack(anchor="w", padx=24, pady=(0, 16))

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
            "Salvar alterações",
            _salvar_edicao,
            variante="primaria",
            height=38,
        )
        btn_salvar.pack(side="right", expand=True, padx=(6, 0))
