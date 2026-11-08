"""Visão principal da aba Escala na interface oficial em Flet.

Implementa:
- Barra de controle responsiva (botão 'Gerar escala' nunca é cortado);
- Faixa de status contextual com o período exato da escala exibida;
- Visualização e edição de escalas do histórico mesmo com rascunho aberto;
- Painel 'Quem folga nesta escala' com as pessoas livres na semana.
"""

from collections.abc import Callable
from datetime import date, datetime, timedelta
import flet as ft

from src.escala.datas import formatar_data, formatar_dia_completo, inicio_da_semana
from src.escala.edicao import confirmar_rascunho, escalas_sobrepostas, validar_escala
from src.escala.exportar import gerar_texto_whatsapp
from src.escala.gerador import gerar_escala
from src.escala.modelos import DadosDoPrograma, Dupla, ErroEscala, Escala, Plantao

from src.escala.interface_flet.dialogos import (
    abrir_dialogo_feriados,
    abrir_dialogo_historico,
    abrir_dialogo_justica,
    abrir_dialogo_troca,
)
from src.escala.interface_flet.tema import (
    COR_AVISO,
    COR_ESTRELA,
    COR_PERIGO,
    COR_PRIMARIA,
    COR_SUCESSO,
    confirmar_acao,
    criar_selo,
    iniciais_nome,
    mostrar_erro_modal,
    mostrar_notificacao,
)


class VisaoEscala:
    """Controlador e construtor visual da aba Escala em Flet."""

    def __init__(
        self,
        page: ft.Page,
        dados: DadosDoPrograma,
        clipboard: ft.Clipboard,
        ao_mudar: Callable[[], None],
    ) -> None:
        self.page = page
        self.dados = dados
        self.clipboard = clipboard
        self.ao_mudar = ao_mudar

        self.data_inicio: date = inicio_da_semana(date.today())
        self.modo_periodo: str = "esta"
        self.qtd_semanas: int = self.dados.configuracao.semanas_por_geracao
        self._semanas_cfg_anterior: int = self.dados.configuracao.semanas_por_geracao

        # Identifica qual escala está na tela: None = rascunho (ou última confirmada), int = índice no histórico
        self.indice_historico_ativo: int | None = None

        self.container_principal = ft.Column(expand=True, spacing=12)
        self.atualizar()

    def obter_escala_exibida(self) -> Escala | None:
        """Retorna a escala atualmente exibida (histórico selecionado ou rascunho)."""
        if self.indice_historico_ativo is not None:
            if 0 <= self.indice_historico_ativo < len(self.dados.escalas):
                return self.dados.escalas[self.indice_historico_ativo]
            self.indice_historico_ativo = None

        if self.dados.rascunho is not None:
            return self.dados.rascunho
        if self.dados.escalas:
            self.indice_historico_ativo = len(self.dados.escalas) - 1
            return self.dados.escalas[-1]
        return None

    def atualizar(self) -> None:
        """Reconstrói os componentes da aba Escala a partir do estado único."""
        if self.dados.configuracao.semanas_por_geracao != self._semanas_cfg_anterior:
            self._semanas_cfg_anterior = self.dados.configuracao.semanas_por_geracao
            self.qtd_semanas = self.dados.configuracao.semanas_por_geracao

        escala = self.obter_escala_exibida()
        self.container_principal.controls = [
            self._construir_barra_controle(),
            self._construir_faixa_status(escala),
            self._construir_area_plantoes(escala),
            self._construir_rodape(escala),
        ]

    def _construir_barra_controle(self) -> ft.Container:
        """Barra superior responsiva (nunca corta o botão Gerar escala)."""
        fim = self.data_inicio + timedelta(days=7 * self.qtd_semanas - 1)
        texto_intervalo = f"{formatar_data(self.data_inicio)} a {formatar_data(fim)}"

        seletor_periodo = ft.SegmentedButton(
            selected=[self.modo_periodo],
            allow_multiple_selection=False,
            show_selected_icon=False,
            on_change=self._ao_mudar_periodo,
            segments=[
                ft.Segment(value="esta", label=ft.Text("Esta semana")),
                ft.Segment(value="proxima", label=ft.Text("Próxima semana")),
                ft.Segment(
                    value="outra",
                    label=ft.Text("Escolher data"),
                    icon=ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=16),
                ),
            ],
        )

        dd_semanas = ft.Dropdown(
            value=str(self.qtd_semanas),
            width=150,
            dense=True,
            on_select=self._ao_mudar_semanas,
            options=[
                ft.DropdownOption(key="1", text="1 semana"),
                ft.DropdownOption(key="2", text="2 semanas"),
                ft.DropdownOption(key="3", text="3 semanas"),
                ft.DropdownOption(key="4", text="4 semanas"),
            ],
        )

        esquerda = ft.Row(
            [
                seletor_periodo,
                criar_selo(
                    f"Período: {texto_intervalo}",
                    ft.Icons.DATE_RANGE_ROUNDED,
                    ft.Colors.PRIMARY_CONTAINER,
                    ft.Colors.ON_PRIMARY_CONTAINER,
                ),
                dd_semanas,
            ],
            spacing=10,
            wrap=True,
        )

        direita = ft.Row(
            [
                ft.OutlinedButton(
                    "Feriados",
                    icon=ft.Icons.CELEBRATION_ROUNDED,
                    on_click=lambda _: abrir_dialogo_feriados(
                        self.page, self.dados, self.data_inicio, self._salvar_e_atualizar
                    ),
                ),
                ft.FilledButton(
                    "Gerar escala",
                    icon=ft.Icons.AUTO_AWESOME_ROUNDED,
                    bgcolor=COR_PRIMARIA,
                    color=ft.Colors.WHITE,
                    height=42,
                    on_click=self._acao_gerar_escala,
                ),
            ],
            spacing=10,
        )

        return ft.Container(
            content=ft.Row(
                [esquerda, direita],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                wrap=True,
            ),
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _construir_faixa_status(self, escala: Escala | None) -> ft.Control:
        """Faixa contextual com o período exato da escala exibida e avisos de validação."""
        if escala is None:
            return ft.Container()

        periodo_esc = f"{formatar_data(escala.primeiro_dia())} a {formatar_data(escala.ultimo_dia())}"
        avisos = validar_escala(escala, self.dados)
        blocos: list[ft.Control] = []

        if not escala.confirmada:
            acoes_rascunho = [
                ft.TextButton(
                    "Descartar rascunho",
                    icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                    on_click=self._acao_descartar_rascunho,
                ),
            ]
            blocos.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.PENDING_ACTIONS_ROUNDED, color="#B45309", size=22),
                            ft.Column(
                                [
                                    ft.Text(
                                        f"Rascunho em aberto ({periodo_esc}) — Ainda não está valendo",
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                        color="#78350F",
                                    ),
                                    ft.Text(
                                        "Clique em qualquer pessoa para fazer trocas ou em 'Confirmar escala' para salvar no histórico.",
                                        size=12,
                                        color="#92400E",
                                    ),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            *acoes_rascunho,
                        ],
                        spacing=10,
                    ),
                    bgcolor="#FEF3C7",
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=10,
                    border=ft.Border.all(1, "#F59E0B"),
                )
            )
        else:
            botoes_extra: list[ft.Control] = []
            if self.dados.rascunho is not None:
                botoes_extra.append(
                    ft.FilledTonalButton(
                        "Voltar ao rascunho",
                        icon=ft.Icons.ARROW_BACK_ROUNDED,
                        on_click=self._voltar_ao_rascunho,
                    )
                )
            blocos.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.VERIFIED_ROUNDED, color="#15803D", size=22),
                            ft.Text(
                                f"Escala confirmada ({periodo_esc}) — Salva no histórico oficial",
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                color="#14532D",
                                expand=True,
                            ),
                            *botoes_extra,
                        ],
                        spacing=10,
                    ),
                    bgcolor="#DCFCE7",
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=10,
                    border=ft.Border.all(1, "#22C55E"),
                )
            )

        if avisos:
            itens_aviso = [ft.Text(f"• {av}", size=13, color="#991B1B") for av in avisos]
            blocos.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.REPORT_PROBLEM_ROUNDED, color=COR_PERIGO, size=18),
                                    ft.Text(
                                        "Atenção às seguintes observações nesta escala:",
                                        weight=ft.FontWeight.BOLD,
                                        size=13,
                                        color="#991B1B",
                                    ),
                                ],
                                spacing=6,
                            ),
                            *itens_aviso,
                        ],
                        spacing=2,
                    ),
                    bgcolor="#FEE2E2",
                    padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                    border_radius=10,
                )
            )

        return ft.Column(blocos, spacing=8)

    def _construir_area_plantoes(self, escala: Escala | None) -> ft.Control:
        """Lista rolável com os cartões de plantão e o resumo de quem está de folga."""
        if escala is None:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.EVENT_NOTE_ROUNDED, size=56, color=ft.Colors.OUTLINE),
                        ft.Text(
                            "Nenhuma escala gerada no momento",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Escolha o período na barra superior e clique em 'Gerar escala'.",
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
                expand=True,
                alignment=ft.Alignment.CENTER,
            )

        cartoes: list[ft.Control] = [
            self._criar_cartao_plantao(escala, idx, plantao)
            for idx, plantao in enumerate(escala.plantoes)
        ]
        cartoes.append(self._criar_painel_folguistas(escala))

        return ft.Column(cartoes, spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

    def _criar_cartao_plantao(self, escala: Escala, idx_plantao: int, plantao: Plantao) -> ft.Container:
        """Cria o cartão visual de um plantão com cabeçalho semântico e grade de duplas."""
        dia_str = formatar_dia_completo(plantao.data)
        periodo_str = plantao.periodo.capitalize()
        icone_cab = ft.Icons.CELEBRATION_ROUNDED if plantao.eh_feriado else ft.Icons.CALENDAR_TODAY_ROUNDED
        cor_icone = COR_AVISO if plantao.eh_feriado else COR_PRIMARIA

        selos_cab: list[ft.Control] = []
        if plantao.eh_feriado:
            nome_fer = f"Feriado: {plantao.nome_feriado}" if plantao.nome_feriado else "Feriado"
            selos_cab.append(criar_selo(nome_fer, ft.Icons.CELEBRATION_ROUNDED, "#FEF3C7", "#92400E"))
        selos_cab.append(
            criar_selo(f"{len(plantao.duplas)} duplas ({len(plantao.duplas) * 2} pessoas)", ft.Icons.GROUPS_ROUNDED)
        )

        cabecalho = ft.Row(
            [
                ft.Row(
                    [
                        ft.Icon(icone_cab, color=cor_icone, size=20),
                        ft.Text(f"{dia_str} — {periodo_str}", size=17, weight=ft.FontWeight.BOLD),
                        *selos_cab,
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "Clique em um integrante para substituir",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            wrap=True,
        )

        colunas_duplas: list[ft.Control] = []
        for num, dupla in enumerate(plantao.duplas, start=1):
            colunas_duplas.append(
                ft.Container(
                    content=self._criar_linha_dupla(escala, idx_plantao, num, dupla),
                    col={"sm": 12, "md": 6},
                )
            )

        return ft.Container(
            content=ft.Column(
                [cabecalho, ft.Divider(height=8), ft.ResponsiveRow(colunas_duplas, spacing=10, run_spacing=10)],
                spacing=8,
            ),
            padding=ft.Padding.all(16),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, "#F59E0B" if plantao.eh_feriado else ft.Colors.OUTLINE_VARIANT),
        )

    def _criar_linha_dupla(
        self,
        escala: Escala,
        idx_plantao: int,
        numero: int,
        dupla: Dupla,
    ) -> ft.Container:
        """Cria um cartão compacto para uma dupla, com dois botões de integrantes."""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(f"{numero}", weight=ft.FontWeight.BOLD, size=13),
                        width=26,
                        height=26,
                        border_radius=13,
                        bgcolor=ft.Colors.SECONDARY_CONTAINER,
                        alignment=ft.Alignment.CENTER,
                    ),
                    self._criar_botao_integrante(escala, idx_plantao, dupla.pessoa_a),
                    ft.Text("&", weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE_VARIANT),
                    self._criar_botao_integrante(escala, idx_plantao, dupla.pessoa_b),
                ],
                spacing=8,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _criar_botao_integrante(self, escala: Escala, idx_plantao: int, id_pessoa: int) -> ft.Control:
        """Cria o chip clicável de uma pessoa da dupla com avatar e estrela de experiência."""
        pessoa = self.dados.buscar_pessoa(id_pessoa)
        nome = pessoa.nome if pessoa else f"ID {id_pessoa}"
        experiente = bool(pessoa and pessoa.experiente)

        itens: list[ft.Control] = [
            ft.CircleAvatar(
                content=ft.Text(iniciais_nome(nome), size=11, weight=ft.FontWeight.BOLD),
                radius=13,
                bgcolor=ft.Colors.PRIMARY_CONTAINER,
            ),
            ft.Text(
                nome,
                size=14,
                weight=ft.FontWeight.W_600,
                overflow=ft.TextOverflow.ELLIPSIS,
                expand=True,
            ),
        ]
        if experiente:
            itens.append(
                ft.Icon(
                    ft.Icons.STAR_ROUNDED,
                    color=COR_ESTRELA,
                    size=17,
                    tooltip="Integrante experiente",
                )
            )

        return ft.Container(
            content=ft.Row(itens, spacing=6),
            padding=ft.Padding.symmetric(horizontal=8, vertical=6),
            border_radius=8,
            ink=True,
            expand=True,
            tooltip=f"Clique para substituir {nome}",
            on_click=lambda _: abrir_dialogo_troca(
                self.page, escala, idx_plantao, id_pessoa, self.dados, self._salvar_e_atualizar
            ),
        )

    def _criar_painel_folguistas(self, escala: Escala) -> ft.Container:
        """Mostra quem está descansando nesta escala."""
        escalados = set().union(*(p.pessoas() for p in escala.plantoes))
        folguistas = [p for p in self.dados.pessoas_ativas() if p.id not in escalados]

        chips = [
            ft.Chip(
                label=ft.Text(p.nome, size=13),
                leading=ft.Icon(
                    ft.Icons.STAR_ROUNDED if p.experiente else ft.Icons.PERSON_OUTLINE_ROUNDED,
                    size=16,
                    color=COR_ESTRELA if p.experiente else ft.Colors.ON_SURFACE_VARIANT,
                ),
            )
            for p in folguistas
        ]

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.BEACH_ACCESS_ROUNDED, color=COR_SUCESSO, size=20),
                            ft.Text(
                                f"Quem folga nesta escala ({len(folguistas)} pessoas livres)",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Row(chips, spacing=8, run_spacing=8, wrap=True)
                    if chips
                    else ft.Text("Todos os integrantes ativos foram escalados neste período."),
                ],
                spacing=8,
            ),
            padding=ft.Padding.all(14),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _construir_rodape(self, escala: Escala | None) -> ft.Container:
        """Barra inferior com Quadro de Justiça, Histórico e ações contextuais."""
        eh_rascunho = bool(escala is not None and not escala.confirmada)

        botoes_direita: list[ft.Control] = []
        if eh_rascunho:
            botoes_direita.append(
                ft.FilledButton(
                    "Confirmar escala",
                    icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                    bgcolor=COR_SUCESSO,
                    color=ft.Colors.WHITE,
                    height=42,
                    on_click=self._acao_confirmar_escala,
                )
            )
        botoes_direita.append(
            ft.FilledTonalButton(
                "Copiar para WhatsApp",
                icon=ft.Icons.CONTENT_COPY_ROUNDED,
                height=42,
                disabled=(escala is None),
                on_click=lambda _: self._acao_copiar_whatsapp(escala),
            )
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.OutlinedButton(
                                "Quadro de justiça",
                                icon=ft.Icons.LEADERBOARD_ROUNDED,
                                on_click=lambda _: abrir_dialogo_justica(
                                    self.page, self.dados, self._salvar_e_atualizar
                                ),
                            ),
                            ft.OutlinedButton(
                                f"Escalas anteriores ({len(self.dados.escalas)})",
                                icon=ft.Icons.HISTORY_ROUNDED,
                                on_click=lambda _: abrir_dialogo_historico(
                                    self.page,
                                    self.dados,
                                    self._selecionar_escala_historico,
                                    self._acao_copiar_whatsapp,
                                    self._salvar_e_atualizar,
                                ),
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Row(botoes_direita, spacing=10),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True,
            ),
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _ao_mudar_periodo(self, e: ft.ControlEvent) -> None:
        """Atualiza a data de início ou abre o DatePicker nativo do Flet."""
        selecionados = list(e.control.selected or ["esta"])
        modo = selecionados[0] if selecionados else "esta"
        hoje_seg = inicio_da_semana(date.today())

        if modo == "esta":
            self.modo_periodo = "esta"
            self.data_inicio = hoje_seg
            self.atualizar()
            self.page.update()
        elif modo == "proxima":
            self.modo_periodo = "proxima"
            self.data_inicio = hoje_seg + timedelta(days=7)
            self.atualizar()
            self.page.update()
        else:
            def _escolheu(ev):
                if ev.control.value:
                    dt = ev.control.value
                    escolhida = dt.date() if isinstance(dt, datetime) else dt
                    self.data_inicio = inicio_da_semana(escolhida)
                    self.modo_periodo = "outra"
                    self.atualizar()
                    self.page.update()

            picker = ft.DatePicker(
                value=self.data_inicio,
                first_date=date(2025, 1, 1),
                last_date=date(2030, 12, 31),
                on_change=_escolheu,
            )
            self.page.show_dialog(picker)

    def _ao_mudar_semanas(self, e: ft.ControlEvent) -> None:
        """Altera o número de semanas a gerar."""
        try:
            self.qtd_semanas = int(e.control.value or "1")
        except ValueError:
            self.qtd_semanas = 1
        self.atualizar()
        self.page.update()

    def _acao_gerar_escala(self, _) -> None:
        """Gera a escala avisando antes caso já exista um rascunho em aberto."""
        def _executar():
            try:
                gerar_escala(self.dados, self.data_inicio, self.qtd_semanas)
                self.indice_historico_ativo = None
                self._salvar_e_atualizar()
                mostrar_notificacao(self.page, "Novo rascunho de escala gerado!")
            except ErroEscala as erro:
                mostrar_erro_modal(self.page, str(erro))

        if self.dados.rascunho is not None:
            confirmar_acao(
                self.page,
                "Substituir rascunho atual?",
                "Já existe um rascunho ainda não confirmado. Gerar uma nova escala irá substituí-lo.",
                _executar,
                texto_confirmar="Gerar nova escala",
            )
        else:
            _executar()

    def _acao_confirmar_escala(self, _) -> None:
        """Confirma o rascunho atual e move para o histórico oficial."""
        if self.dados.rascunho is None:
            return

        def _confirmar():
            confirmar_rascunho(self.dados)
            self.indice_historico_ativo = len(self.dados.escalas) - 1
            self._salvar_e_atualizar()
            mostrar_notificacao(self.page, "Escala confirmada e salva no histórico!")

        sobrepostas = escalas_sobrepostas(self.dados, self.dados.rascunho)
        if sobrepostas:
            confirmar_acao(
                self.page,
                "Substituir escala existente",
                "Já existe escala confirmada com datas em comum. Confirmar irá substituí-la.",
                _confirmar,
                texto_confirmar="Substituir e confirmar",
            )
        else:
            _confirmar()

    def _acao_descartar_rascunho(self, _) -> None:
        """Permite descartar o rascunho atual."""
        def _descartar():
            self.dados.rascunho = None
            self.indice_historico_ativo = (
                len(self.dados.escalas) - 1 if self.dados.escalas else None
            )
            self._salvar_e_atualizar()
            mostrar_notificacao(self.page, "Rascunho descartado.")

        confirmar_acao(
            self.page,
            "Descartar rascunho",
            "Deseja descartar o rascunho atual? Esta ação não afeta as escalas já confirmadas.",
            _descartar,
            texto_confirmar="Descartar",
            perigoso=True,
        )

    async def _acao_copiar_whatsapp(self, escala: Escala | None) -> None:
        """Copia o texto formatado para o WhatsApp e mostra SnackBar."""
        if escala is None:
            return
        texto = gerar_texto_whatsapp(escala, self.dados)
        await self.clipboard.set(texto)
        mostrar_notificacao(
            self.page,
            "Texto da escala copiado para a área de transferência (pronto para colar no WhatsApp)!",
            ft.Icons.CONTENT_COPY_ROUNDED,
        )

    def _selecionar_escala_historico(self, indice: int) -> None:
        """Exibe na tela a escala escolhida no histórico (mesmo com rascunho aberto)."""
        self.indice_historico_ativo = indice
        self.atualizar()
        self.page.update()

    def _voltar_ao_rascunho(self, _) -> None:
        """Retorna da visualização de histórico para o rascunho ativo."""
        self.indice_historico_ativo = None
        self.atualizar()
        self.page.update()

    def _salvar_e_atualizar(self) -> None:
        """Salva no armazenamento e reconstrói a tela."""
        self.ao_mudar()
        self.atualizar()
        self.page.update()
