"""Diálogo modal para adicionar e gerenciar feriados com plantão.

Permite cadastrar datas especiais, nomear o feriado e definir
quantas duplas trabalharão em cada período daquele dia.
"""

from collections.abc import Callable
from datetime import date
import customtkinter as ctk

from src.escala.datas import formatar_dia_completo, ler_data
from src.escala.interface.componentes import (
    COR_BORDA,
    COR_CARTAO,
    COR_FUNDO,
    COR_PERIGO,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_AJUDA,
    FONTE_CORPO,
    FONTE_SUBTITULO,
    FONTE_TITULO,
    BotaoGrande,
    CartaoFrame,
    configurar_janela_modal,
    mostrar_erro,
)
from src.escala.modelos import DadosDoPrograma, ErroEscala, Feriado


class JanelaFeriado(ctk.CTkToplevel):
    """Janela modal para cadastro de feriados."""

    def __init__(
        self,
        pai,
        dados: DadosDoPrograma,
        ao_mudar: Callable[[], None],
        data_sugerida: date | None = None,
    ) -> None:
        super().__init__(pai)
        self.dados = dados
        self.ao_mudar = ao_mudar

        configurar_janela_modal(self, pai, "Feriados e Datas Especiais", 500, 520)
        self._construir_interface(data_sugerida)

    def _construir_interface(self, data_sugerida: date | None) -> None:
        """Monta o formulário de novo feriado e a listagem dos já cadastrados."""
        lbl_titulo = ctk.CTkLabel(
            self,
            text="🎉 Adicionar Feriado com Plantão",
            font=FONTE_TITULO,
            text_color=COR_TEXTO,
        )
        lbl_titulo.pack(padx=24, pady=(20, 10), anchor="w")

        form = CartaoFrame(self)
        form.pack(fill="x", padx=20, pady=(0, 16))

        # Data
        lbl_data = ctk.CTkLabel(form, text="Data (dd/mm/aaaa):", font=FONTE_CORPO, text_color=COR_TEXTO)
        lbl_data.pack(padx=16, pady=(12, 2), anchor="w")
        self.campo_data = ctk.CTkEntry(form, font=FONTE_CORPO, height=36)
        if data_sugerida:
            self.campo_data.insert(0, data_sugerida.strftime("%d/%m/%Y"))
        self.campo_data.pack(fill="x", padx=16, pady=(0, 8))

        # Nome
        lbl_nome = ctk.CTkLabel(form, text="Nome do feriado:", font=FONTE_CORPO, text_color=COR_TEXTO)
        lbl_nome.pack(padx=16, pady=(0, 2), anchor="w")
        self.campo_nome = ctk.CTkEntry(form, placeholder_text="Ex.: Consciência Negra, Natal", font=FONTE_CORPO, height=36)
        self.campo_nome.pack(fill="x", padx=16, pady=(0, 8))

        # Período e Duplas
        linha_opcoes = ctk.CTkFrame(form, fg_color="transparent")
        linha_opcoes.pack(fill="x", padx=16, pady=(0, 14))

        col_per = ctk.CTkFrame(linha_opcoes, fg_color="transparent")
        col_per.pack(side="left", expand=True, fill="x", padx=(0, 8))
        lbl_per = ctk.CTkLabel(col_per, text="Período:", font=FONTE_AJUDA, text_color=COR_TEXTO)
        lbl_per.pack(anchor="w")
        self.combo_periodo = ctk.CTkOptionMenu(
            col_per,
            values=self.dados.configuracao.periodos,
            height=36,
            font=FONTE_CORPO,
        )
        self.combo_periodo.pack(fill="x")

        col_dup = ctk.CTkFrame(linha_opcoes, fg_color="transparent")
        col_dup.pack(side="right", expand=True, fill="x", padx=(8, 0))
        lbl_dup = ctk.CTkLabel(col_dup, text="Nº de duplas:", font=FONTE_AJUDA, text_color=COR_TEXTO)
        lbl_dup.pack(anchor="w")
        self.combo_duplas = ctk.CTkOptionMenu(
            col_dup,
            values=["1", "2", "3", "4", "5", "6"],
            height=36,
            font=FONTE_CORPO,
        )
        # Padrão
        padrao_duplas = "4"
        if self.dados.configuracao.feriado_periodos_padrao:
            primeiro_valor = next(iter(self.dados.configuracao.feriado_periodos_padrao.values()))
            padrao_duplas = str(primeiro_valor)
        self.combo_duplas.set(padrao_duplas)
        self.combo_duplas.pack(fill="x")

        btn_adicionar = BotaoGrande(
            form,
            "+ Salvar feriado",
            comando=self._salvar_feriado,
            variante="primaria",
            height=38,
        )
        btn_adicionar.pack(fill="x", padx=16, pady=(0, 14))

        # Feriados cadastrados
        lbl_cadastrados = ctk.CTkLabel(
            self,
            text="Feriados cadastrados:",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
        )
        lbl_cadastrados.pack(padx=24, pady=(0, 6), anchor="w")

        self.scroll_feriados = ctk.CTkScrollableFrame(self, fg_color="transparent", height=120)
        self.scroll_feriados.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._atualizar_lista_feriados()

    def _atualizar_lista_feriados(self) -> None:
        """Lista os feriados com botão para exclusão."""
        for filho in self.scroll_feriados.winfo_children():
            filho.destroy()

        if not self.dados.feriados:
            lbl_vazio = ctk.CTkLabel(
                self.scroll_feriados,
                text="Nenhum feriado cadastrado ainda.",
                font=FONTE_CORPO,
                text_color=COR_TEXTO_SUAVE,
            )
            lbl_vazio.pack(pady=10)
            return

        for feriado in sorted(self.dados.feriados, key=lambda f: f.data):
            cartao = CartaoFrame(self.scroll_feriados)
            cartao.pack(fill="x", pady=3)

            info = f"{formatar_dia_completo(feriado.data)} — {feriado.nome or 'Feriado'}"
            lbl = ctk.CTkLabel(cartao, text=info, font=FONTE_CORPO, text_color=COR_TEXTO)
            lbl.pack(side="left", padx=12, pady=8)

            btn_remover = BotaoGrande(
                cartao,
                "Remover",
                comando=lambda f=feriado: self._remover_feriado(f),
                variante="secundaria",
                height=28,
            )
            btn_remover.pack(side="right", padx=12)

    def _salvar_feriado(self) -> None:
        """Valida e adiciona o novo feriado."""
        try:
            data_feriado = ler_data(self.campo_data.get())
        except ErroEscala as erro:
            mostrar_erro(self, str(erro))
            return

        # Verifica duplicidade de data
        for f in self.dados.feriados:
            if f.data == data_feriado:
                mostrar_erro(self, f"Já existe um feriado cadastrado para o dia {self.campo_data.get().strip()}.")
                return

        nome = self.campo_nome.get().strip()
        periodo = self.combo_periodo.get()
        qtd_duplas = int(self.combo_duplas.get())

        novo_feriado = Feriado(
            data=data_feriado,
            nome=nome,
            periodos={periodo: qtd_duplas},
        )
        self.dados.feriados.append(novo_feriado)
        self.ao_mudar()

        self.campo_nome.delete(0, "end")
        self.campo_data.delete(0, "end")
        self._atualizar_lista_feriados()

    def _remover_feriado(self, feriado: Feriado) -> None:
        """Remove o feriado da lista e persiste."""
        if feriado in self.dados.feriados:
            self.dados.feriados.remove(feriado)
            self.ao_mudar()
            self._atualizar_lista_feriados()
