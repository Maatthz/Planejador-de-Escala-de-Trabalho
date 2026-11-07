"""Diálogo modal com o Quadro de Justiça da equipe.

Apresenta a fila ordenada de prioridade dos integrantes, distinguindo
plantões reais realizados de compensações pelo piso de ausências, e permite
preencher ou ajustar manualmente os contadores de cada pessoa.
"""

from collections.abc import Callable
from datetime import date
import customtkinter as ctk

from src.escala.armazenamento import salvar
from src.escala.datas import formatar_data, ler_data
from src.escala.historico import ResumoJustica, ajustar_contadores_pessoa, quadro_de_justica
from src.escala.interface.componentes import (
    COR_AVISO_TEXTO,
    COR_BORDA,
    COR_ESTRELA,
    COR_FUNDO,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_AJUDA,
    FONTE_CORPO,
    FONTE_TITULO,
    BotaoGrande,
    CartaoFrame,
    configurar_janela_modal,
    configurar_rolagem_suave,
    mostrar_erro,
)
from src.escala.modelos import DadosDoPrograma, ErroEscala


def _interpretar_data_opcional(texto: str, nome_pessoa: str) -> date | None:
    """Converte texto 'dd/mm/aaaa' (ou 'dd/mm' usando o ano atual) em date, ou None se vazio."""
    limpo = texto.strip()
    if not limpo or limpo.lower() == "nunca":
        return None
    partes = limpo.split("/")
    if len(partes) == 2:
        limpo = f"{partes[0]}/{partes[1]}/{date.today().year}"
    try:
        return ler_data(limpo)
    except ErroEscala as erro:
        raise ErroEscala(
            f"Data do último plantão inválida para {nome_pessoa}: use o formato 07/11/2026 ou deixe em branco."
        ) from erro


class JanelaJustica(ctk.CTkToplevel):
    """Visualização e edição manual da fila de prioridade e contadores de justiça."""

    def __init__(
        self,
        pai,
        dados: DadosDoPrograma,
        ao_mudar: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(pai)
        self.dados = dados
        self.ao_mudar = ao_mudar
        self._modo_edicao = False
        self._campos_edicao: dict[int, tuple[ctk.CTkEntry, ctk.CTkEntry, ctk.CTkEntry]] = {}

        configurar_janela_modal(self, pai, "📊 Quadro de Justiça", 820, 580)
        self._construir_interface()

    def _construir_interface(self) -> None:
        """Monta o cabeçalho explicativo, a tabela rolável e o rodapé."""
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=24, pady=(20, 10))

        topo_esq = ctk.CTkFrame(topo, fg_color="transparent")
        topo_esq.pack(side="left", fill="x", expand=True)

        lbl_tit = ctk.CTkLabel(
            topo_esq,
            text="📊 Quadro de Justiça e Prioridade",
            font=FONTE_TITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_tit.pack(fill="x")

        self.lbl_desc = ctk.CTkLabel(
            topo_esq,
            text="",
            font=FONTE_CORPO,
            text_color=COR_TEXTO_SUAVE,
            anchor="w",
            wraplength=560,
            justify="left",
        )
        self.lbl_desc.pack(fill="x", pady=(4, 0))

        self.btn_editar = BotaoGrande(
            topo,
            "✏️ Editar manualmente",
            comando=self._ativar_modo_edicao,
            variante="primaria",
            height=38,
            width=210,
        )
        self.btn_editar.pack(side="right", padx=(12, 0))

        # Tabela com Cabeçalho e Conteúdo
        tabela_frame = CartaoFrame(self)
        tabela_frame.pack(fill="both", expand=True, padx=20, pady=(0, 14))

        cab_tab = ctk.CTkFrame(tabela_frame, fg_color=COR_BORDA, height=36, corner_radius=6)
        cab_tab.pack(fill="x", padx=10, pady=(10, 4))
        cab_tab.pack_propagate(False)

        colunas = [
            ("Fila", 55),
            ("Nome", 190),
            ("Plantões Feitos", 120),
            ("Em Feriados", 105),
            ("Último Plantão", 140),
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

        self.scroll_linhas = ctk.CTkScrollableFrame(tabela_frame, fg_color="transparent")
        self.scroll_linhas.pack(fill="both", expand=True, padx=6, pady=(0, 10))
        configurar_rolagem_suave(self.scroll_linhas)

        self.rodape = ctk.CTkFrame(self, fg_color="transparent")
        self.rodape.pack(fill="x", padx=20, pady=(0, 16))

        self._atualizar_conteudo()

    def _atualizar_conteudo(self) -> None:
        """Renderiza a tabela e o rodapé conforme o modo atual (visualização ou edição)."""
        for w in self.scroll_linhas.winfo_children():
            w.destroy()
        for w in self.rodape.winfo_children():
            w.destroy()
        self._campos_edicao.clear()

        linhas = quadro_de_justica(self.dados)

        if self._modo_edicao:
            self.lbl_desc.configure(
                text="Digite os valores atuais de cada pessoa (use dd/mm/aaaa no último plantão ou deixe vazio). As próximas escalas confirmadas somarão a partir daqui."
            )
            self.btn_editar.pack_forget()
        else:
            self.lbl_desc.configure(
                text="As pessoas no topo da lista têm prioridade para entrar na próxima escala (contando escalas confirmadas e ajustes manuais)."
            )
            if linhas:
                self.btn_editar.pack(side="right", padx=(12, 0))
            else:
                self.btn_editar.pack_forget()

        if not linhas:
            lbl_vazio = ctk.CTkLabel(
                self.scroll_linhas,
                text="Nenhuma pessoa ativa na equipe.",
                font=FONTE_CORPO,
                text_color=COR_TEXTO_SUAVE,
            )
            lbl_vazio.pack(pady=40)
            self._construir_rodape_visualizacao()
            return

        for idx, item in enumerate(linhas):
            self._criar_linha_pessoa(idx, item)

        if self._modo_edicao:
            self._construir_rodape_edicao()
        else:
            self._construir_rodape_visualizacao()

    def _criar_linha_pessoa(self, idx: int, item: ResumoJustica) -> None:
        """Cria uma linha da tabela (somente leitura ou com campos de edição)."""
        cor_linha = COR_FUNDO if idx % 2 == 0 else "transparent"
        linha = ctk.CTkFrame(self.scroll_linhas, fg_color=cor_linha, height=38, corner_radius=6)
        linha.pack(fill="x", pady=2)

        lbl_pos = ctk.CTkLabel(
            linha,
            text=f"{item.posicao}º",
            font=FONTE_CORPO,
            text_color=COR_TEXTO,
            width=55,
            anchor="w",
        )
        lbl_pos.pack(side="left", padx=4)

        frame_nome = ctk.CTkFrame(linha, fg_color="transparent", width=190, height=32)
        frame_nome.pack(side="left", padx=4)
        frame_nome.pack_propagate(False)

        lbl_nome = ctk.CTkLabel(
            frame_nome,
            text=item.pessoa.nome,
            font=FONTE_CORPO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_nome.pack(side="left")

        if item.pessoa.experiente:
            lbl_est = ctk.CTkLabel(
                frame_nome,
                text="★",
                font=("Segoe UI", 15, "bold"),
                text_color=COR_ESTRELA,
            )
            lbl_est.pack(side="left", padx=4)

        if self._modo_edicao:
            ent_plantoes = ctk.CTkEntry(linha, width=100, height=30, font=FONTE_CORPO)
            ent_plantoes.insert(0, str(item.plantoes_reais))
            ent_plantoes.pack(side="left", padx=(4, 24), pady=3)

            ent_feriados = ctk.CTkEntry(linha, width=90, height=30, font=FONTE_CORPO)
            ent_feriados.insert(0, str(item.feriados_trabalhados))
            ent_feriados.pack(side="left", padx=(4, 19), pady=3)

            ent_ultimo = ctk.CTkEntry(
                linha,
                width=130,
                height=30,
                font=FONTE_CORPO,
                placeholder_text="dd/mm/aaaa",
            )
            if item.ultimo_plantao is not None:
                ent_ultimo.insert(
                    0,
                    f"{formatar_data(item.ultimo_plantao)}/{item.ultimo_plantao.year}",
                )
            ent_ultimo.pack(side="left", padx=(4, 14), pady=3)

            self._campos_edicao[item.pessoa.id] = (ent_plantoes, ent_feriados, ent_ultimo)
        else:
            lbl_plantoes = ctk.CTkLabel(
                linha,
                text=str(item.plantoes_reais),
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
                width=120,
                anchor="w",
            )
            lbl_plantoes.pack(side="left", padx=4)

            lbl_feriados = ctk.CTkLabel(
                linha,
                text=str(item.feriados_trabalhados),
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
                width=105,
                anchor="w",
            )
            lbl_feriados.pack(side="left", padx=4)

            ult_texto = formatar_data(item.ultimo_plantao) if item.ultimo_plantao else "Nunca"
            lbl_ult = ctk.CTkLabel(
                linha,
                text=ult_texto,
                font=FONTE_CORPO,
                text_color=COR_TEXTO_SUAVE if not item.ultimo_plantao else COR_TEXTO,
                width=140,
                anchor="w",
            )
            lbl_ult.pack(side="left", padx=4)

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

    def _construir_rodape_visualizacao(self) -> None:
        """Exibe apenas o botão Fechar no modo de visualização."""
        btn_fechar = BotaoGrande(
            self.rodape,
            "Fechar",
            comando=self.destroy,
            variante="secundaria",
            height=38,
            width=160,
        )
        btn_fechar.pack()

    def _construir_rodape_edicao(self) -> None:
        """Exibe botões Cancelar e Salvar alterações no modo de edição."""
        btn_cancelar = BotaoGrande(
            self.rodape,
            "Cancelar",
            comando=self._cancelar_edicao,
            variante="secundaria",
            height=38,
            width=160,
        )
        btn_cancelar.pack(side="left", expand=True, padx=(80, 8))

        btn_salvar = BotaoGrande(
            self.rodape,
            "💾 Salvar alterações",
            comando=self._salvar_edicao,
            variante="sucesso",
            height=38,
            width=210,
        )
        btn_salvar.pack(side="right", expand=True, padx=(8, 80))

    def _ativar_modo_edicao(self) -> None:
        """Habilita os campos de texto na tabela para preenchimento manual."""
        self._modo_edicao = True
        self._atualizar_conteudo()

    def _cancelar_edicao(self) -> None:
        """Descarta alterações não salvas e volta para a visualização da fila."""
        self._modo_edicao = False
        self._atualizar_conteudo()

    def _salvar_edicao(self) -> None:
        """Valida todos os campos preenchidos, atualiza os contadores e salva os dados."""
        valores_validados: list[tuple[int, int, int, date | None]] = []

        try:
            for id_pessoa, (ent_p, ent_f, ent_u) in self._campos_edicao.items():
                pessoa = self.dados.buscar_pessoa(id_pessoa)
                nome = pessoa.nome if pessoa else f"ID {id_pessoa}"

                txt_p = ent_p.get().strip() or "0"
                try:
                    val_p = int(txt_p)
                except ValueError as erro:
                    raise ErroEscala(
                        f"Quantidade de plantões inválida para {nome}: digite um número inteiro."
                    ) from erro

                txt_f = ent_f.get().strip() or "0"
                try:
                    val_f = int(txt_f)
                except ValueError as erro:
                    raise ErroEscala(
                        f"Quantidade de feriados inválida para {nome}: digite um número inteiro."
                    ) from erro

                if val_p < 0 or val_f < 0:
                    raise ErroEscala(
                        f"Os números de plantões de {nome} não podem ser negativos."
                    )

                data_ult = _interpretar_data_opcional(ent_u.get(), nome)
                valores_validados.append((id_pessoa, val_p, val_f, data_ult))

            for id_pessoa, val_p, val_f, data_ult in valores_validados:
                ajustar_contadores_pessoa(self.dados, id_pessoa, val_p, val_f, data_ult)

        except ErroEscala as erro:
            mostrar_erro(self, str(erro))
            return

        if self.ao_mudar is not None:
            self.ao_mudar()
        else:
            salvar(self.dados)

        self._modo_edicao = False
        self._atualizar_conteudo()
