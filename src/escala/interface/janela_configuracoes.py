"""Janela modal de configurações do programa com explicações e exemplos didáticos.

Permite configurar turnos semanais, períodos, feriados, formação de duplas,
parâmetros de escala, mensagens para WhatsApp, opções avançadas e cópia de segurança.
"""

from collections.abc import Callable
import copy
from datetime import date
from pathlib import Path
import tkinter.filedialog as filedialog
import customtkinter as ctk

from src.escala.armazenamento import exportar_copia, importar_copia
from src.escala.datas import DIAS_DA_SEMANA
from src.escala.interface.componentes import (
    COR_BORDA,
    COR_CARTAO,
    COR_FUNDO,
    COR_PERIGO,
    COR_PRIMARIA,
    COR_SECUNDARIA,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    FONTE_AJUDA,
    FONTE_BOTAO,
    FONTE_CORPO,
    FONTE_SUBTITULO,
    FONTE_TITULO,
    BotaoGrande,
    CampoComAjuda,
    CartaoFrame,
    configurar_janela_modal,
    configurar_rolagem_suave,
    mostrar_erro,
    mostrar_info,
    perguntar_sim_nao,
)
from src.escala.modelos import (
    Configuracao,
    DadosDoPrograma,
    ErroEscala,
    ModeloDeTurno,
    Pessoa,
)

MAPA_MODO_EXIBICAO: dict[str, str] = {
    "preferencia": "Preferência",
    "obrigatoria": "Obrigatória",
    "ignorar": "Ignorar",
}

MAPA_MODO_VALOR: dict[str, str] = {
    "Preferência": "preferencia",
    "Obrigatória": "obrigatoria",
    "Ignorar": "ignorar",
}


class JanelaConfiguracoes(ctk.CTkToplevel):
    """Janela modal para ajuste de todas as configurações do sistema."""

    def __init__(
        self,
        pai: ctk.CTk | ctk.CTkToplevel,
        dados: DadosDoPrograma,
        ao_mudar: Callable[[], None],
    ) -> None:
        super().__init__(master=pai)
        self.pai = pai
        self.dados = dados
        self.ao_mudar = ao_mudar

        # Cópia de trabalho temporária para não alterar dados reais antes de salvar
        self.config_temp: Configuracao = copy.deepcopy(dados.configuracao)
        self.avancadas_expandidas: bool = False

        configurar_janela_modal(self, pai, "⚙️ Configurações do Programa", 840, 700)
        self._construir_interface()

    def _construir_interface(self) -> None:
        """Monta o cabeçalho fixo, área rolável de seções e rodapé com botões de ação."""
        # 1. Cabeçalho fixo
        cabecalho = ctk.CTkFrame(self, fg_color=COR_CARTAO, height=65, corner_radius=0)
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)

        lbl_titulo = ctk.CTkLabel(
            cabecalho,
            text="⚙️ Configurações do Programa",
            font=FONTE_TITULO,
            text_color=COR_TEXTO,
        )
        lbl_titulo.pack(side="left", padx=24, pady=10)

        # 2. Rodapé fixo
        rodape = ctk.CTkFrame(self, fg_color=COR_CARTAO, height=70, corner_radius=0)
        rodape.pack(fill="x", side="bottom")
        rodape.pack_propagate(False)

        btn_restaurar = BotaoGrande(
            rodape,
            "Restaurar padrão",
            comando=self._restaurar_padrao,
            variante="perigo",
            height=38,
        )
        btn_restaurar.pack(side="left", padx=24, pady=16)

        btn_salvar = BotaoGrande(
            rodape,
            "Salvar alterações",
            comando=self._salvar,
            variante="primaria",
            height=38,
        )
        btn_salvar.pack(side="right", padx=(8, 24), pady=16)

        btn_cancelar = BotaoGrande(
            rodape,
            "Cancelar",
            comando=self.destroy,
            variante="secundaria",
            height=38,
        )
        btn_cancelar.pack(side="right", padx=8, pady=16)

        # 3. Área rolável com as seções
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=16)
        configurar_rolagem_suave(self.scroll)

        self._construir_secao_turnos()
        self._construir_secao_feriados()
        self._construir_secao_duplas()
        self._construir_secao_escala()
        self._construir_secao_mensagem()
        self._construir_secao_avancadas()

    def _construir_secao_turnos(self) -> None:
        """Seção de turnos semanais e nomes dos períodos."""
        cartao = CartaoFrame(self.scroll)
        cartao.pack(fill="x", pady=(0, 14), padx=4)

        lbl_sec = ctk.CTkLabel(
            cartao,
            text="📅 Turnos Semanais e Horários",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_sec.pack(fill="x", padx=16, pady=(16, 8))

        # Campo: Turnos
        frame_turnos_container = ctk.CTkFrame(cartao, fg_color="transparent")
        self.campo_turnos = CampoComAjuda(
            cartao,
            "turnos",
            widget_controle=frame_turnos_container,
        )
        self.campo_turnos.pack(fill="x", padx=16, pady=(0, 14))

        # Lista visual de turnos atuais
        self.frame_lista_turnos = ctk.CTkFrame(frame_turnos_container, fg_color="transparent")
        self.frame_lista_turnos.pack(fill="x", pady=(0, 8))
        self._atualizar_lista_turnos()

        # Linha para adicionar novo turno
        frame_add_turno = ctk.CTkFrame(frame_turnos_container, fg_color=COR_FUNDO, corner_radius=8)
        frame_add_turno.pack(fill="x", pady=(4, 0), padx=2, ipady=6)

        lbl_novo_t = ctk.CTkLabel(
            frame_add_turno,
            text="Novo turno:",
            font=FONTE_CORPO,
            text_color=COR_TEXTO,
        )
        lbl_novo_t.pack(side="left", padx=(10, 6))

        self.combo_novo_dia = ctk.CTkOptionMenu(
            frame_add_turno,
            values=DIAS_DA_SEMANA,
            width=110,
        )
        self.combo_novo_dia.set("Sábado")
        self.combo_novo_dia.pack(side="left", padx=4)

        self.combo_novo_periodo = ctk.CTkOptionMenu(
            frame_add_turno,
            values=self.config_temp.periodos,
            width=110,
        )
        if self.config_temp.periodos:
            self.combo_novo_periodo.set(self.config_temp.periodos[0])
        self.combo_novo_periodo.pack(side="left", padx=4)

        lbl_duplas = ctk.CTkLabel(
            frame_add_turno,
            text="Duplas:",
            font=FONTE_CORPO,
            text_color=COR_TEXTO,
        )
        lbl_duplas.pack(side="left", padx=(8, 4))

        self.combo_nova_qtd = ctk.CTkOptionMenu(
            frame_add_turno,
            values=["1", "2", "3", "4", "5", "6", "7", "8"],
            width=65,
        )
        self.combo_nova_qtd.set("4")
        self.combo_nova_qtd.pack(side="left", padx=4)

        btn_add_t = ctk.CTkButton(
            frame_add_turno,
            text="+ Adicionar",
            command=self._adicionar_turno,
            fg_color=COR_PRIMARIA,
            height=32,
            width=90,
        )
        btn_add_t.pack(side="left", padx=10)

        # Campo: Períodos
        self.entry_periodos = ctk.CTkEntry(
            cartao,
            height=36,
            font=FONTE_CORPO,
        )
        self.entry_periodos.insert(0, ", ".join(self.config_temp.periodos))

        self.campo_periodos = CampoComAjuda(
            cartao,
            "periodos",
            widget_controle=self.entry_periodos,
        )
        self.campo_periodos.pack(fill="x", padx=16, pady=(0, 16))

    def _atualizar_lista_turnos(self) -> None:
        """Renderiza a lista visual dos turnos cadastrados."""
        for filho in self.frame_lista_turnos.winfo_children():
            filho.destroy()

        for i, turno in enumerate(self.config_temp.turnos):
            linha = ctk.CTkFrame(self.frame_lista_turnos, fg_color=COR_CARTAO, border_color=COR_BORDA, border_width=1, corner_radius=6)
            linha.pack(fill="x", pady=2)

            nome_dia = DIAS_DA_SEMANA[turno.dia_da_semana] if 0 <= turno.dia_da_semana < len(DIAS_DA_SEMANA) else f"Dia {turno.dia_da_semana}"
            txt = f"• {nome_dia} — {turno.periodo.capitalize()} ({turno.qtd_duplas} duplas = {turno.qtd_duplas * 2} pessoas)"

            lbl = ctk.CTkLabel(
                linha,
                text=txt,
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
                anchor="w",
            )
            lbl.pack(side="left", padx=12, pady=6)

            if len(self.config_temp.turnos) > 1:
                btn_remover = ctk.CTkButton(
                    linha,
                    text="Excluir",
                    command=lambda idx=i: self._remover_turno(idx),
                    fg_color=COR_SECUNDARIA,
                    text_color=COR_PERIGO,
                    hover_color=COR_BORDA,
                    height=28,
                    width=60,
                )
                btn_remover.pack(side="right", padx=8, pady=4)

    def _adicionar_turno(self) -> None:
        """Adiciona um novo modelo de turno à lista temporária."""
        dia_texto = self.combo_novo_dia.get()
        if dia_texto not in DIAS_DA_SEMANA:
            mostrar_erro(self, "Dia da semana inválido.")
            return

        dia_idx = DIAS_DA_SEMANA.index(dia_texto)
        periodo = self.combo_novo_periodo.get().strip().lower()
        if not periodo:
            mostrar_erro(self, "Período inválido.")
            return

        try:
            qtd = int(self.combo_nova_qtd.get())
        except ValueError:
            qtd = 4

        # Evita duplicar o mesmo dia e período
        for t in self.config_temp.turnos:
            if t.dia_da_semana == dia_idx and t.periodo.lower() == periodo:
                mostrar_erro(self, f"Já existe um turno cadastrado para {dia_texto} ({periodo}).")
                return

        self.config_temp.turnos.append(ModeloDeTurno(dia_idx, periodo, qtd))
        self._atualizar_lista_turnos()

    def _remover_turno(self, indice: int) -> None:
        """Remove o turno especificado se houver mais de um."""
        if len(self.config_temp.turnos) <= 1:
            mostrar_erro(self, "É necessário manter pelo menos um turno semanal.")
            return
        if 0 <= indice < len(self.config_temp.turnos):
            self.config_temp.turnos.pop(indice)
            self._atualizar_lista_turnos()

    def _construir_secao_feriados(self) -> None:
        """Seção de configuração de plantão em feriados."""
        cartao = CartaoFrame(self.scroll)
        cartao.pack(fill="x", pady=(0, 14), padx=4)

        lbl_sec = ctk.CTkLabel(
            cartao,
            text="🎉 Feriados e Datas Especiais",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_sec.pack(fill="x", padx=16, pady=(16, 8))

        # Campo: Feriados ativos (Switch)
        self.var_feriados_ativos = ctk.BooleanVar(value=self.config_temp.feriados_ativos)
        self.switch_feriados = ctk.CTkSwitch(
            cartao,
            text="Incluir plantão em feriados cadastrados",
            variable=self.var_feriados_ativos,
            font=FONTE_CORPO,
            text_color=COR_TEXTO,
        )
        self.campo_feriados_ativos = CampoComAjuda(
            cartao,
            "feriados_ativos",
            widget_controle=self.switch_feriados,
        )
        self.campo_feriados_ativos.pack(fill="x", padx=16, pady=(0, 14))

        # Campo: Padrão para feriados
        frame_feriado_padrao = ctk.CTkFrame(cartao, fg_color="transparent")
        periodo_ini = next(iter(self.config_temp.feriado_periodos_padrao.keys()), "manhã")
        qtd_ini = str(next(iter(self.config_temp.feriado_periodos_padrao.values()), 4))

        lbl_p_f = ctk.CTkLabel(frame_feriado_padrao, text="Período padrão:", font=FONTE_CORPO, text_color=COR_TEXTO)
        lbl_p_f.pack(side="left", padx=(0, 6))

        self.combo_periodo_feriado = ctk.CTkOptionMenu(
            frame_feriado_padrao,
            values=self.config_temp.periodos,
            width=120,
        )
        if periodo_ini in self.config_temp.periodos:
            self.combo_periodo_feriado.set(periodo_ini)
        elif self.config_temp.periodos:
            self.combo_periodo_feriado.set(self.config_temp.periodos[0])
        self.combo_periodo_feriado.pack(side="left", padx=4)

        lbl_q_f = ctk.CTkLabel(frame_feriado_padrao, text="Duplas:", font=FONTE_CORPO, text_color=COR_TEXTO)
        lbl_q_f.pack(side="left", padx=(12, 6))

        self.combo_duplas_feriado = ctk.CTkOptionMenu(
            frame_feriado_padrao,
            values=["1", "2", "3", "4", "5", "6", "7", "8"],
            width=65,
        )
        self.combo_duplas_feriado.set(qtd_ini)
        self.combo_duplas_feriado.pack(side="left", padx=4)

        self.campo_feriado_padrao = CampoComAjuda(
            cartao,
            "feriado_periodos_padrao",
            widget_controle=frame_feriado_padrao,
        )
        self.campo_feriado_padrao.pack(fill="x", padx=16, pady=(0, 16))

    def _construir_secao_duplas(self) -> None:
        """Seção de experiência e modo de formação de duplas."""
        cartao = CartaoFrame(self.scroll)
        cartao.pack(fill="x", pady=(0, 14), padx=4)

        lbl_sec = ctk.CTkLabel(
            cartao,
            text="👥 Formação das Duplas",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_sec.pack(fill="x", padx=16, pady=(16, 8))

        # Campo: Modo de Experiência
        modo_atual = MAPA_MODO_EXIBICAO.get(self.config_temp.modo_experiencia, "Preferência")
        self.seg_experiencia = ctk.CTkSegmentedButton(
            cartao,
            values=["Preferência", "Obrigatória", "Ignorar"],
            height=36,
            font=FONTE_CORPO,
        )
        self.seg_experiencia.set(modo_atual)

        self.campo_experiencia = CampoComAjuda(
            cartao,
            "modo_experiencia",
            widget_controle=self.seg_experiencia,
        )
        self.campo_experiencia.pack(fill="x", padx=16, pady=(0, 16))

    def _construir_secao_escala(self) -> None:
        """Seção de parâmetros da escala."""
        cartao = CartaoFrame(self.scroll)
        cartao.pack(fill="x", pady=(0, 14), padx=4)

        lbl_sec = ctk.CTkLabel(
            cartao,
            text="📋 Geração da Escala",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_sec.pack(fill="x", padx=16, pady=(16, 8))

        # Campo: Semanas por geração
        self.seg_semanas = ctk.CTkSegmentedButton(
            cartao,
            values=["1 semana", "2 semanas (quinzenal)", "3 semanas", "4 semanas"],
            height=36,
            font=FONTE_CORPO,
        )
        val_semanas = f"{self.config_temp.semanas_por_geracao} semana{'s' if self.config_temp.semanas_por_geracao > 1 else ''}"
        if self.config_temp.semanas_por_geracao == 2:
            val_semanas = "2 semanas (quinzenal)"
        self.seg_semanas.set(val_semanas if val_semanas in self.seg_semanas.cget("values") else "1 semana")

        self.campo_semanas = CampoComAjuda(
            cartao,
            "semanas_por_geracao",
            widget_controle=self.seg_semanas,
        )
        self.campo_semanas.pack(fill="x", padx=16, pady=(0, 16))

    def _construir_secao_mensagem(self) -> None:
        """Seção de formatação de mensagens para o WhatsApp."""
        cartao = CartaoFrame(self.scroll)
        cartao.pack(fill="x", pady=(0, 14), padx=4)

        lbl_sec = ctk.CTkLabel(
            cartao,
            text="💬 Mensagem para WhatsApp",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
            anchor="w",
        )
        lbl_sec.pack(fill="x", padx=16, pady=(16, 8))

        # Campo: Título da mensagem
        self.entry_titulo_msg = ctk.CTkEntry(cartao, height=36, font=FONTE_CORPO)
        self.entry_titulo_msg.insert(0, self.config_temp.titulo_mensagem)

        self.campo_titulo_msg = CampoComAjuda(
            cartao,
            "titulo_mensagem",
            widget_controle=self.entry_titulo_msg,
        )
        self.campo_titulo_msg.pack(fill="x", padx=16, pady=(0, 14))

        # Campo: Texto final da mensagem
        self.entry_texto_final = ctk.CTkEntry(
            cartao,
            height=36,
            font=FONTE_CORPO,
            placeholder_text="Opcional. Ex.: Trocas: avisar com 48h de antecedência.",
        )
        if self.config_temp.texto_final_mensagem:
            self.entry_texto_final.insert(0, self.config_temp.texto_final_mensagem)

        self.campo_texto_final = CampoComAjuda(
            cartao,
            "texto_final_mensagem",
            widget_controle=self.entry_texto_final,
        )
        self.campo_texto_final.pack(fill="x", padx=16, pady=(0, 16))

    def _construir_secao_avancadas(self) -> None:
        """Seção recolhível de opções avançadas (regras finas e cópia de segurança)."""
        cartao = CartaoFrame(self.scroll)
        cartao.pack(fill="x", pady=(0, 14), padx=4)

        cabecalho_avancadas = ctk.CTkFrame(cartao, fg_color="transparent")
        cabecalho_avancadas.pack(fill="x", padx=16, pady=12)

        lbl_sec = ctk.CTkLabel(
            cabecalho_avancadas,
            text="🛠️ Opções Avançadas",
            font=FONTE_SUBTITULO,
            text_color=COR_TEXTO,
        )
        lbl_sec.pack(side="left")

        self.btn_toggle_avancadas = ctk.CTkButton(
            cabecalho_avancadas,
            text="▶ Mostrar opções avançadas",
            command=self._alternar_avancadas,
            fg_color=COR_SECUNDARIA,
            text_color=COR_TEXTO,
            hover_color=COR_BORDA,
            height=32,
        )
        self.btn_toggle_avancadas.pack(side="right")

        # Container interno das opções avançadas (recolhido por padrão)
        self.frame_conteudo_avancadas = ctk.CTkFrame(cartao, fg_color="transparent")

        # 1. Evitar semanas seguidas (Switch)
        self.var_evitar_semanas = ctk.BooleanVar(value=self.config_temp.evitar_semanas_seguidas)
        self.switch_evitar_semanas = ctk.CTkSwitch(
            self.frame_conteudo_avancadas,
            text="Tentar dar folga a quem trabalhou na semana anterior",
            variable=self.var_evitar_semanas,
            font=FONTE_CORPO,
            text_color=COR_TEXTO,
        )
        self.campo_evitar_semanas = CampoComAjuda(
            self.frame_conteudo_avancadas,
            "evitar_semanas_seguidas",
            widget_controle=self.switch_evitar_semanas,
        )
        self.campo_evitar_semanas.pack(fill="x", padx=16, pady=(4, 14))

        # 2. Compensar ausências (Switch)
        self.var_compensar_ausencias = ctk.BooleanVar(value=self.config_temp.compensar_ausencias)
        self.switch_compensar_ausencias = ctk.CTkSwitch(
            self.frame_conteudo_avancadas,
            text="Quem se ausenta acumula dívida de plantões (não recomendado)",
            variable=self.var_compensar_ausencias,
            font=FONTE_CORPO,
            text_color=COR_TEXTO,
        )
        self.campo_compensar = CampoComAjuda(
            self.frame_conteudo_avancadas,
            "compensar_ausencias",
            widget_controle=self.switch_compensar_ausencias,
        )
        self.campo_compensar.pack(fill="x", padx=16, pady=(0, 14))

        # 3. Nunca juntos
        frame_nunca_container = ctk.CTkFrame(self.frame_conteudo_avancadas, fg_color="transparent")
        self.campo_nunca_juntos = CampoComAjuda(
            self.frame_conteudo_avancadas,
            "nunca_juntos",
            widget_controle=frame_nunca_container,
        )
        self.campo_nunca_juntos.pack(fill="x", padx=16, pady=(0, 14))

        self.frame_lista_nunca = ctk.CTkFrame(frame_nunca_container, fg_color="transparent")
        self.frame_lista_nunca.pack(fill="x", pady=(0, 6))
        self._atualizar_lista_nunca_juntos()

        self._construir_seletor_par(
            frame_nunca_container,
            botao_texto="+ Adicionar restrição",
            comando=self._adicionar_nunca_juntos,
            prefixo="nunca",
        )

        # 4. Sempre juntos (Duplas fixas)
        frame_sempre_container = ctk.CTkFrame(self.frame_conteudo_avancadas, fg_color="transparent")
        self.campo_sempre_juntos = CampoComAjuda(
            self.frame_conteudo_avancadas,
            "sempre_juntos",
            widget_controle=frame_sempre_container,
        )
        self.campo_sempre_juntos.pack(fill="x", padx=16, pady=(0, 14))

        self.frame_lista_sempre = ctk.CTkFrame(frame_sempre_container, fg_color="transparent")
        self.frame_lista_sempre.pack(fill="x", pady=(0, 6))
        self._atualizar_lista_sempre_juntos()

        self._construir_seletor_par(
            frame_sempre_container,
            botao_texto="+ Adicionar dupla fixa",
            comando=self._adicionar_sempre_juntos,
            prefixo="sempre",
        )

        # 5. Cópia de segurança manual (backup_manual)
        frame_backup = ctk.CTkFrame(self.frame_conteudo_avancadas, fg_color="transparent")
        btn_salvar_copia = BotaoGrande(
            frame_backup,
            "💾 Salvar cópia de segurança…",
            comando=self._salvar_copia_manual,
            variante="secundaria",
            height=34,
        )
        btn_salvar_copia.pack(side="left", padx=(0, 10))

        btn_restaurar_copia = BotaoGrande(
            frame_backup,
            "📂 Restaurar de uma cópia…",
            comando=self._restaurar_copia_manual,
            variante="secundaria",
            height=34,
        )
        btn_restaurar_copia.pack(side="left", padx=10)

        self.campo_backup = CampoComAjuda(
            self.frame_conteudo_avancadas,
            "backup_manual",
            widget_controle=frame_backup,
        )
        self.campo_backup.pack(fill="x", padx=16, pady=(0, 16))

    def _alternar_avancadas(self) -> None:
        """Expande ou recolhe a seção de opções avançadas."""
        self.avancadas_expandidas = not self.avancadas_expandidas
        if self.avancadas_expandidas:
            self.btn_toggle_avancadas.configure(text="▼ Ocultar opções avançadas")
            self.frame_conteudo_avancadas.pack(fill="x", pady=(4, 0))
        else:
            self.btn_toggle_avancadas.configure(text="▶ Mostrar opções avançadas")
            self.frame_conteudo_avancadas.pack_forget()

    def _obter_nomes_pessoas(self) -> tuple[list[str], dict[str, int]]:
        """Retorna lista de opções de nomes e dicionário mapeando nome -> id."""
        pessoas = self.dados.pessoas_ativas()
        mapa: dict[str, int] = {}
        nomes: list[str] = []
        for p in pessoas:
            rotulo = f"{p.nome} (ID {p.id})"
            nomes.append(rotulo)
            mapa[rotulo] = p.id
        return nomes, mapa

    def _construir_seletor_par(
        self,
        master: ctk.CTkFrame,
        botao_texto: str,
        comando: Callable[[], None],
        prefixo: str,
    ) -> None:
        """Gera controles de seleção de duas pessoas para formar pares (nunca ou sempre juntos)."""
        frame_linha = ctk.CTkFrame(master, fg_color=COR_FUNDO, corner_radius=8)
        frame_linha.pack(fill="x", pady=(4, 0), padx=2, ipady=6)

        nomes, mapa = self._obter_nomes_pessoas()
        if not nomes:
            lbl_vazio = ctk.CTkLabel(frame_linha, text="Cadastre pessoas na aba Equipe para configurar pares.", font=FONTE_AJUDA, text_color=COR_TEXTO_SUAVE)
            lbl_vazio.pack(padx=12, pady=6)
            return

        setattr(self, f"mapa_pessoas_{prefixo}", mapa)

        combo_a = ctk.CTkOptionMenu(frame_linha, values=nomes, width=170)
        combo_a.set(nomes[0])
        combo_a.pack(side="left", padx=(10, 4))
        setattr(self, f"combo_{prefixo}_a", combo_a)

        lbl_sep = ctk.CTkLabel(frame_linha, text="✕" if prefixo == "nunca" else "+", font=FONTE_SUBTITULO, text_color=COR_TEXTO)
        lbl_sep.pack(side="left", padx=4)

        combo_b = ctk.CTkOptionMenu(frame_linha, values=nomes, width=170)
        combo_b.set(nomes[1] if len(nomes) > 1 else nomes[0])
        combo_b.pack(side="left", padx=4)
        setattr(self, f"combo_{prefixo}_b", combo_b)

        btn_add = ctk.CTkButton(
            frame_linha,
            text=botao_texto,
            command=comando,
            fg_color=COR_PRIMARIA,
            height=32,
        )
        btn_add.pack(side="left", padx=10)

    def _atualizar_lista_nunca_juntos(self) -> None:
        """Renderiza os pares atualmente proibidos de trabalhar juntos."""
        for filho in self.frame_lista_nunca.winfo_children():
            filho.destroy()

        if not self.config_temp.nunca_juntos:
            lbl = ctk.CTkLabel(
                self.frame_lista_nunca,
                text="Nenhum par proibido cadastrado.",
                font=FONTE_AJUDA,
                text_color=COR_TEXTO_SUAVE,
            )
            lbl.pack(anchor="w", padx=4, pady=2)
            return

        for i, (id_a, id_b) in enumerate(self.config_temp.nunca_juntos):
            linha = ctk.CTkFrame(self.frame_lista_nunca, fg_color=COR_CARTAO, border_color=COR_BORDA, border_width=1, corner_radius=6)
            linha.pack(fill="x", pady=2)

            p_a = self.dados.buscar_pessoa(id_a)
            p_b = self.dados.buscar_pessoa(id_b)
            nome_a = p_a.nome if p_a else f"ID {id_a}"
            nome_b = p_b.nome if p_b else f"ID {id_b}"

            lbl = ctk.CTkLabel(
                linha,
                text=f"• {nome_a} ✕ {nome_b}",
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
            )
            lbl.pack(side="left", padx=12, pady=4)

            btn_rem = ctk.CTkButton(
                linha,
                text="Remover",
                command=lambda idx=i: self._remover_nunca_juntos(idx),
                fg_color=COR_SECUNDARIA,
                text_color=COR_PERIGO,
                hover_color=COR_BORDA,
                height=26,
                width=65,
            )
            btn_rem.pack(side="right", padx=8, pady=4)

    def _adicionar_nunca_juntos(self) -> None:
        """Adiciona um novo par de restrição 'nunca juntos'."""
        mapa = getattr(self, "mapa_pessoas_nunca", {})
        combo_a = getattr(self, "combo_nunca_a", None)
        combo_b = getattr(self, "combo_nunca_b", None)
        if not combo_a or not combo_b:
            return

        id_a = mapa.get(combo_a.get())
        id_b = mapa.get(combo_b.get())
        if id_a is None or id_b is None:
            mostrar_erro(self, "Selecione duas pessoas válidas.")
            return

        if id_a == id_b:
            mostrar_erro(self, "Selecione duas pessoas diferentes.")
            return

        par = (min(id_a, id_b), max(id_a, id_b))
        if par in self.config_temp.nunca_juntos:
            mostrar_erro(self, "Este par já está na lista de restrições.")
            return

        if par in self.config_temp.sempre_juntos:
            mostrar_erro(self, "Este par já está configurado como dupla fixa.")
            return

        self.config_temp.nunca_juntos.append(par)
        self._atualizar_lista_nunca_juntos()

    def _remover_nunca_juntos(self, indice: int) -> None:
        """Remove o par proibido selecionado."""
        if 0 <= indice < len(self.config_temp.nunca_juntos):
            self.config_temp.nunca_juntos.pop(indice)
            self._atualizar_lista_nunca_juntos()

    def _atualizar_lista_sempre_juntos(self) -> None:
        """Renderiza as duplas fixas atualmente configuradas."""
        for filho in self.frame_lista_sempre.winfo_children():
            filho.destroy()

        if not self.config_temp.sempre_juntos:
            lbl = ctk.CTkLabel(
                self.frame_lista_sempre,
                text="Nenhuma dupla fixa cadastrada.",
                font=FONTE_AJUDA,
                text_color=COR_TEXTO_SUAVE,
            )
            lbl.pack(anchor="w", padx=4, pady=2)
            return

        for i, (id_a, id_b) in enumerate(self.config_temp.sempre_juntos):
            linha = ctk.CTkFrame(self.frame_lista_sempre, fg_color=COR_CARTAO, border_color=COR_BORDA, border_width=1, corner_radius=6)
            linha.pack(fill="x", pady=2)

            p_a = self.dados.buscar_pessoa(id_a)
            p_b = self.dados.buscar_pessoa(id_b)
            nome_a = p_a.nome if p_a else f"ID {id_a}"
            nome_b = p_b.nome if p_b else f"ID {id_b}"

            lbl = ctk.CTkLabel(
                linha,
                text=f"• {nome_a} + {nome_b}",
                font=FONTE_CORPO,
                text_color=COR_TEXTO,
            )
            lbl.pack(side="left", padx=12, pady=4)

            btn_rem = ctk.CTkButton(
                linha,
                text="Remover",
                command=lambda idx=i: self._remover_sempre_juntos(idx),
                fg_color=COR_SECUNDARIA,
                text_color=COR_PERIGO,
                hover_color=COR_BORDA,
                height=26,
                width=65,
            )
            btn_rem.pack(side="right", padx=8, pady=4)

    def _adicionar_sempre_juntos(self) -> None:
        """Adiciona uma nova dupla fixa ('sempre juntos')."""
        mapa = getattr(self, "mapa_pessoas_sempre", {})
        combo_a = getattr(self, "combo_sempre_a", None)
        combo_b = getattr(self, "combo_sempre_b", None)
        if not combo_a or not combo_b:
            return

        id_a = mapa.get(combo_a.get())
        id_b = mapa.get(combo_b.get())
        if id_a is None or id_b is None:
            mostrar_erro(self, "Selecione duas pessoas válidas.")
            return

        if id_a == id_b:
            mostrar_erro(self, "Selecione duas pessoas diferentes.")
            return

        par = (min(id_a, id_b), max(id_a, id_b))
        if par in self.config_temp.sempre_juntos:
            mostrar_erro(self, "Este par já está na lista de duplas fixas.")
            return

        if par in self.config_temp.nunca_juntos:
            mostrar_erro(self, "Este par já está configurado na lista de restrições (nunca juntos).")
            return

        # Uma pessoa não pode pertencer a mais de uma dupla fixa ao mesmo tempo
        for a, b in self.config_temp.sempre_juntos:
            if id_a in (a, b) or id_b in (a, b):
                mostrar_erro(self, "Uma pessoa não pode pertencer a mais de uma dupla fixa ao mesmo tempo.")
                return

        self.config_temp.sempre_juntos.append(par)
        self._atualizar_lista_sempre_juntos()

    def _remover_sempre_juntos(self, indice: int) -> None:
        """Remove a dupla fixa selecionada."""
        if 0 <= indice < len(self.config_temp.sempre_juntos):
            self.config_temp.sempre_juntos.pop(indice)
            self._atualizar_lista_sempre_juntos()

    def _salvar_copia_manual(self) -> None:
        """Salva todos os dados atuais em um arquivo JSON à escolha da usuária."""
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar cópia de segurança",
            defaultextension=".json",
            filetypes=[("Arquivo JSON", "*.json")],
            initialfile=f"copia_escala_{date.today().strftime('%Y%m%d')}.json",
        )
        if not caminho:
            return
        try:
            exportar_copia(self.dados, Path(caminho))
            mostrar_info(self, "Cópia de segurança salva com sucesso!")
        except ErroEscala as erro:
            mostrar_erro(self, str(erro))

    def _restaurar_copia_manual(self) -> None:
        """Restaura todos os dados a partir de um arquivo de cópia de segurança."""
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Restaurar de uma cópia de segurança",
            filetypes=[("Arquivo JSON", "*.json")],
        )
        if not caminho:
            return

        if not perguntar_sim_nao(
            self,
            "Atenção: Restaurar uma cópia de segurança substituirá todos os dados atuais "
            "(equipe, folgas, escalas e configurações).\n\nDeseja realmente continuar?",
        ):
            return

        try:
            novos_dados = importar_copia(Path(caminho))
            self.dados.pessoas = novos_dados.pessoas
            self.dados.configuracao = novos_dados.configuracao
            self.dados.feriados = novos_dados.feriados
            self.dados.escalas = novos_dados.escalas
            self.dados.rascunho = novos_dados.rascunho
            self.dados.proximo_id = novos_dados.proximo_id
            self.ao_mudar()
            self.destroy()
            mostrar_info(self.pai, "Cópia de segurança restaurada com sucesso!")
        except ErroEscala as erro:
            mostrar_erro(self, str(erro))

    def _restaurar_padrao(self) -> None:
        """Restaura todas as configurações para os padrões de fábrica após confirmação."""
        if not perguntar_sim_nao(
            self,
            "Deseja restaurar todas as configurações para os padrões de fábrica?\n\n"
            "Todas as preferências personalizadas de turnos, duplas e mensagens serão redefinidas.",
        ):
            return

        self.dados.configuracao = Configuracao()
        self.ao_mudar()
        self.destroy()
        mostrar_info(self.pai, "Configurações restauradas para o padrão com sucesso!")

    def _salvar(self) -> None:
        """Valida todos os campos e persiste as alterações em DadosDoPrograma."""
        try:
            # 1. Validação de turnos
            if not self.config_temp.turnos:
                raise ErroEscala("É necessário cadastrar pelo menos um turno semanal.")

            for t in self.config_temp.turnos:
                if t.qtd_duplas < 1:
                    raise ErroEscala(f"A quantidade de duplas do turno de {DIAS_DA_SEMANA[t.dia_da_semana]} deve ser no mínimo 1.")

            # Avisar se 2 × duplas de um mesmo dia > pessoas ativas
            pessoas_ativas = self.dados.pessoas_ativas()
            duplas_por_dia: dict[int, int] = {}
            for t in self.config_temp.turnos:
                duplas_por_dia[t.dia_da_semana] = duplas_por_dia.get(t.dia_da_semana, 0) + t.qtd_duplas

            for dia_idx, total_duplas in duplas_por_dia.items():
                pessoas_necessarias = total_duplas * 2
                if pessoas_necessarias > len(pessoas_ativas):
                    nome_dia = DIAS_DA_SEMANA[dia_idx] if 0 <= dia_idx < len(DIAS_DA_SEMANA) else str(dia_idx)
                    if not perguntar_sim_nao(
                        self,
                        f"Aviso de capacidade:\n\nNo {nome_dia}, são necessárias {pessoas_necessarias} pessoas "
                        f"({total_duplas} duplas), mas há apenas {len(pessoas_ativas)} pessoas ativas na equipe.\n\n"
                        f"Deseja salvar as configurações mesmo assim?",
                    ):
                        return

            # 2. Validação de períodos
            texto_periodos = self.entry_periodos.get().strip()
            periodos_digitados = [p.strip().lower() for p in texto_periodos.split(",") if p.strip()]
            if not periodos_digitados:
                raise ErroEscala("Informe pelo menos um período válido (ex.: manhã, tarde).")
            self.config_temp.periodos = periodos_digitados

            # 3. Feriados
            self.config_temp.feriados_ativos = self.var_feriados_ativos.get()
            periodo_f = self.combo_periodo_feriado.get().strip().lower()
            if not periodo_f:
                periodo_f = self.config_temp.periodos[0] if self.config_temp.periodos else "manhã"
            try:
                qtd_f = int(self.combo_duplas_feriado.get())
            except ValueError:
                qtd_f = 4
            self.config_temp.feriado_periodos_padrao = {periodo_f: qtd_f}

            # 4. Modo de experiência
            modo_texto = self.seg_experiencia.get()
            self.config_temp.modo_experiencia = MAPA_MODO_VALOR.get(modo_texto, "preferencia")

            # 5. Semanas por geração
            semanas_texto = self.seg_semanas.get()
            try:
                semanas_num = int(semanas_texto.split()[0])
            except (ValueError, IndexError):
                semanas_num = 1
            self.config_temp.semanas_por_geracao = max(1, semanas_num)

            # 6. Título da mensagem
            titulo = self.entry_titulo_msg.get().strip()
            if not titulo:
                raise ErroEscala("O título da mensagem não pode ser vazio.")
            self.config_temp.titulo_mensagem = titulo

            # 7. Texto final da mensagem
            self.config_temp.texto_final_mensagem = self.entry_texto_final.get().strip()

            # 8. Opções avançadas
            self.config_temp.evitar_semanas_seguidas = self.var_evitar_semanas.get()
            self.config_temp.compensar_ausencias = self.var_compensar_ausencias.get()

            # Aplica no estado único do programa e salva
            self.dados.configuracao = self.config_temp
            self.ao_mudar()
            self.destroy()
            mostrar_info(self.pai, "Configurações salvas com sucesso!")

        except ErroEscala as erro:
            mostrar_erro(self, str(erro))
