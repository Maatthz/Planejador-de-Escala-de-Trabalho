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
    COR_ESTRELA,
    COR_ESTRELA_HOVER,
    COR_FUNDO,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_CORPO,
    FONTE_SUBTITULO,
    FONTE_TITULO,
    BotaoGrande,
    CartaoFrame,
    configurar_janela_modal,
    configurar_rolagem_suave,
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
            font=("Segoe UI", 16, "bold"),
            text_color=COR_TEXTO,
            anchor="w",
        )
        self.lbl_contador.pack(side="left", fill="x", expand=True)

        btn_adicionar = BotaoGrande(
            cabecalho,
            "+ Adicionar pessoa",
            comando=self._abrir_dialogo_adicionar,
            variante="primaria",
            height=36,
        )
        btn_adicionar.pack(side="right")

        self.scroll_lista = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_lista.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.scroll_lista.grid_columnconfigure(0, weight=1, uniform="col_equipe")
        self.scroll_lista.grid_columnconfigure(1, weight=1, uniform="col_equipe")
        configurar_rolagem_suave(self.scroll_lista)

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

        for idx, pessoa in enumerate(pessoas_ordenadas):
            self._criar_cartao_pessoa(pessoa, idx)

    def _mostrar_estado_vazio(self) -> None:
        """Exibe orientação amigável quando não há ninguém cadastrado (1 único filho)."""
        cartao_vazio = CartaoFrame(self.scroll_lista)
        cartao_vazio.grid(row=0, column=0, columnspan=2, sticky="ew", pady=20, padx=10, ipady=30)

        lbl = ctk.CTkLabel(
            cartao_vazio,
            text="Nenhuma pessoa cadastrada ainda.\nClique em '+ Adicionar pessoa' acima para começar.",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO_SUAVE,
            justify="center",
        )
        lbl.pack(expand=True)

    def _criar_cartao_pessoa(self, pessoa: Pessoa, idx: int = 0) -> None:
        """Cria uma linha/cartão em grade de 2 colunas com no máximo 4 widgets internos."""
        cartao = CartaoFrame(self.scroll_lista)
        cartao.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=6, pady=4)

        # 1. Nome com status integrado no texto se inativo
        if not pessoa.ativo:
            texto_nome = f"{pessoa.nome}  (Inativo)"
            cor_nome = COR_TEXTO_SUAVE
            fonte_nome = ("Segoe UI", 14)
        else:
            texto_nome = pessoa.nome
            cor_nome = COR_TEXTO
            fonte_nome = ("Segoe UI", 14, "bold")

        lbl_nome = ctk.CTkLabel(
            cartao,
            text=texto_nome,
            font=fonte_nome,
            text_color=cor_nome,
            anchor="w",
        )
        lbl_nome.pack(side="left", padx=(14, 0), pady=8)

        # 2. Estrela amarela para experientes ativos
        if pessoa.ativo and pessoa.experiente:
            lbl_estrela = ctk.CTkLabel(
                cartao,
                text="★",
                font=("Segoe UI", 16, "bold"),
                text_color=COR_ESTRELA,
            )
            lbl_estrela.pack(side="left", padx=(6, 0), pady=8)

        # 3. Botão Desativar/Reativar (à direita)
        if pessoa.ativo:
            btn_status = BotaoGrande(
                cartao,
                "Desativar",
                comando=lambda p=pessoa: self._alternar_status(p),
                variante="secundaria",
                height=30,
                width=84,
            )
        else:
            btn_status = BotaoGrande(
                cartao,
                "Reativar",
                comando=lambda p=pessoa: self._alternar_status(p),
                variante="secundaria",
                height=30,
                width=84,
            )
        btn_status.pack(side="right", padx=(4, 12), pady=8)

        # 4. Botão Editar
        btn_editar = BotaoGrande(
            cartao,
            "Editar",
            comando=lambda p=pessoa: self._abrir_dialogo_editar(p),
            variante="secundaria",
            height=30,
            width=68,
        )
        btn_editar.pack(side="right", padx=4, pady=8)

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
            text="Pessoa experiente no plantão (★)",
            variable=var_experiente,
            font=FONTE_CORPO,
            fg_color=COR_ESTRELA,
            hover_color=COR_ESTRELA_HOVER,
            checkmark_color="#121214",
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
            text="Pessoa experiente no plantão (★)",
            variable=var_experiente,
            font=FONTE_CORPO,
            fg_color=COR_ESTRELA,
            hover_color=COR_ESTRELA_HOVER,
            checkmark_color="#121214",
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
