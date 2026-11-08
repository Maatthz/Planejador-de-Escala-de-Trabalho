"""Visões de Equipe e de Folgas na interface oficial em Flet.

Implementa:
- Cartões de equipe clicáveis com contadores reais e exclusão segura;
- Aba Folgas com calendário mensal interativo, botão 'Marcar período (férias)'
  e agrupamento inteligente de intervalos contínuos.
"""

import calendar
from collections.abc import Callable
from datetime import date, datetime, timedelta
import flet as ft

from src.escala.datas import formatar_data, formatar_dia_completo, ler_data
from src.escala.historico import calcular_contadores
from src.escala.modelos import DadosDoPrograma, ErroEscala, Pessoa

from src.escala.interface_flet.tema import (
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

MESES_NOMES: list[str] = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def agrupar_datas_continuas(datas: set[date]) -> list[tuple[date, date]]:
    """Agrupa datas consecutivas em intervalos (inicio, fim) para leitura limpa."""
    ordenadas = sorted(datas)
    if not ordenadas:
        return []
    grupos: list[tuple[date, date]] = []
    ini = ordenadas[0]
    fim = ordenadas[0]
    for d in ordenadas[1:]:
        if d == fim + timedelta(days=1):
            fim = d
        else:
            grupos.append((ini, fim))
            ini = d
            fim = d
    grupos.append((ini, fim))
    return grupos


class VisaoEquipe:
    """Aba Equipe com cartões clicáveis, busca e resumo de plantões/folgas."""

    def __init__(
        self,
        page: ft.Page,
        dados: DadosDoPrograma,
        ao_mudar: Callable[[], None],
    ) -> None:
        self.page = page
        self.dados = dados
        self.ao_mudar = ao_mudar
        self.termo_busca: str = ""
        self.container_principal = ft.Column(expand=True, spacing=12)
        self.atualizar()

    def atualizar(self) -> None:
        """Reconstrói o cabeçalho e a grade de integrantes."""
        ativas = [p for p in self.dados.pessoas if p.ativo]
        experientes = [p for p in ativas if p.experiente]
        contadores = calcular_contadores(self.dados)
        hoje = date.today()

        topo = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.GROUPS_ROUNDED, color=COR_PRIMARIA, size=26),
                            ft.Column(
                                [
                                    ft.Text(
                                        f"Equipe — {len(ativas)} ativas ({len(experientes)} experientes)",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Clique em qualquer cartão para editar nome, experiência (★), status ou excluir.",
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=1,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Row(
                        [
                            ft.TextField(
                                value=self.termo_busca,
                                hint_text="Filtrar por nome...",
                                prefix_icon=ft.Icons.SEARCH_ROUNDED,
                                width=220,
                                dense=True,
                                on_change=self._ao_filtrar,
                            ),
                            ft.FilledButton(
                                "Adicionar pessoa",
                                icon=ft.Icons.PERSON_ADD_ROUNDED,
                                bgcolor=COR_PRIMARIA,
                                color=ft.Colors.WHITE,
                                height=40,
                                on_click=lambda _: self._abrir_modal_pessoa(None),
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                wrap=True,
            ),
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

        ordenadas = sorted(self.dados.pessoas, key=lambda p: (not p.ativo, p.nome.lower()))
        filtro = self.termo_busca.strip().lower()
        cartoes: list[ft.Control] = []

        for pessoa in ordenadas:
            if filtro and filtro not in pessoa.nome.lower():
                continue
            carga = contadores.carga.get(pessoa.id, 0)
            folgas_fut = sum(1 for d in pessoa.indisponibilidades if d >= hoje)
            cartoes.append(
                ft.Container(
                    content=self._criar_cartao_pessoa(pessoa, carga, folgas_fut),
                    col={"sm": 12, "md": 6, "lg": 4},
                )
            )

        grade = ft.Column(
            [ft.ResponsiveRow(cartoes, spacing=10, run_spacing=10)],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.container_principal.controls = [topo, grade]

    def _criar_cartao_pessoa(self, pessoa: Pessoa, carga: int, folgas_fut: int) -> ft.Container:
        """Cria um cartão limpo para o integrante."""
        subtitulo = (
            f"{carga} plantão(ões) • {folgas_fut} folga(s) futura(s)"
            if pessoa.ativo
            else "Inativo (histórico preservado)"
        )
        return ft.Container(
            content=ft.Row(
                [
                    ft.CircleAvatar(
                        content=ft.Text(iniciais_nome(pessoa.nome), weight=ft.FontWeight.BOLD),
                        bgcolor=ft.Colors.PRIMARY_CONTAINER if pessoa.ativo else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(pessoa.nome, size=15, weight=ft.FontWeight.BOLD),
                                    ft.Icon(ft.Icons.STAR_ROUNDED, color=COR_ESTRELA, size=18)
                                    if (pessoa.experiente and pessoa.ativo)
                                    else ft.Container(),
                                ],
                                spacing=4,
                            ),
                            ft.Text(subtitulo, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color=ft.Colors.OUTLINE),
                ],
                spacing=12,
            ),
            padding=ft.Padding.all(14),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            opacity=1.0 if pessoa.ativo else 0.55,
            ink=True,
            on_click=lambda _: self._abrir_modal_pessoa(pessoa),
        )

    def _ao_filtrar(self, e: ft.ControlEvent) -> None:
        self.termo_busca = e.control.value or ""
        self.atualizar()
        self.page.update()

    def _abrir_modal_pessoa(self, pessoa: Pessoa | None) -> None:
        """Abre modal único para criar, editar ou excluir integrante."""
        editando = pessoa is not None
        campo_nome = ft.TextField(
            label="Nome completo",
            value=pessoa.nome if pessoa else "",
            autofocus=True,
        )
        sw_exp = ft.Switch(
            label="Integrante experiente no plantão (★)",
            value=pessoa.experiente if pessoa else False,
        )
        sw_ativo = ft.Switch(
            label="Integrante ativo na escala",
            value=pessoa.ativo if pessoa else True,
            visible=editando,
        )

        def _excluir(_) -> None:
            if pessoa is None:
                return
            em_escala = any(
                pessoa.id in plantao.pessoas()
                for escala in self.dados.escalas
                if escala.confirmada
                for plantao in escala.plantoes
            )
            if em_escala:
                mostrar_erro_modal(
                    self.page,
                    f"Não é possível excluir '{pessoa.nome}' definitivamente porque ela já consta "
                    "no histórico de escalas confirmadas. Para que ela não participe das próximas, desative-a.",
                )
                return

            def _confirmado() -> None:
                self.page.pop_dialog()
                self.dados.pessoas.remove(pessoa)
                self.dados.configuracao.nunca_juntos = [
                    par for par in self.dados.configuracao.nunca_juntos if pessoa.id not in par
                ]
                self.dados.configuracao.sempre_juntos = [
                    par for par in self.dados.configuracao.sempre_juntos if pessoa.id not in par
                ]
                if self.dados.rascunho is not None and any(
                    pessoa.id in pl.pessoas() for pl in self.dados.rascunho.plantoes
                ):
                    self.dados.rascunho = None
                self.ao_mudar()
                self.atualizar()
                self.page.update()
                mostrar_notificacao(self.page, f"'{pessoa.nome}' removida do cadastro.")

            confirmar_acao(
                self.page,
                "Excluir pessoa do cadastro",
                f"Tem certeza que deseja remover '{pessoa.nome}' definitivamente da equipe?",
                _confirmado,
                texto_confirmar="Excluir",
                perigoso=True,
            )

        def _salvar(_):
            nome = (campo_nome.value or "").strip()
            try:
                if not editando:
                    self.dados.adicionar_pessoa(nome, experiente=bool(sw_exp.value))
                else:
                    if not nome:
                        raise ErroEscala("O nome não pode ser vazio.")
                    for p in self.dados.pessoas:
                        if p.id != pessoa.id and p.nome.lower() == nome.lower():
                            raise ErroEscala(f"Já existe uma pessoa com o nome '{p.nome}'.")
                    pessoa.nome = nome
                    pessoa.experiente = bool(sw_exp.value)
                    novo_ativo = bool(sw_ativo.value)
                    if not pessoa.ativo and novo_ativo:
                        pessoa.data_entrada = date.today()
                    pessoa.ativo = novo_ativo
                self.page.pop_dialog()
                self.ao_mudar()
                self.atualizar()
                self.page.update()
                mostrar_notificacao(self.page, "Dados salvos com sucesso!")
            except ErroEscala as erro:
                mostrar_erro_modal(self.page, str(erro))

        acoes: list[ft.Control] = []
        if editando:
            acoes.append(
                ft.TextButton(
                    "Excluir do cadastro",
                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    on_click=_excluir,
                )
            )
        acoes.extend(
            [
                ft.TextButton("Cancelar", on_click=lambda _: self.page.pop_dialog()),
                ft.FilledButton("Salvar", on_click=_salvar),
            ]
        )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Editar — {pessoa.nome}" if editando else "Adicionar integrante",
                weight=ft.FontWeight.BOLD,
                size=19,
            ),
            content=ft.Container(
                content=ft.Column([campo_nome, sw_exp, sw_ativo], spacing=14, tight=True),
                width=420,
            ),
            actions=acoes,
        )
        self.page.show_dialog(dialogo)


class VisaoFolgas:
    """Aba Folgas com calendário mensal interativo, férias por período e intervalos agrupados."""

    def __init__(
        self,
        page: ft.Page,
        dados: DadosDoPrograma,
        ao_mudar: Callable[[], None],
    ) -> None:
        self.page = page
        self.dados = dados
        self.ao_mudar = ao_mudar

        ativas = self.dados.pessoas_ativas()
        self.id_selecionado: int | None = ativas[0].id if ativas else None
        hoje = date.today()
        self.ano: int = hoje.year
        self.mes: int = hoje.month

        self.container_principal = ft.Row(expand=True, spacing=16)
        self.atualizar()

    def atualizar(self) -> None:
        """Reconstrói a lista lateral de integrantes e o painel do calendário."""
        ativas = self.dados.pessoas_ativas()
        pessoa_atual = (
            self.dados.buscar_pessoa(self.id_selecionado)
            if self.id_selecionado is not None
            else None
        )
        if pessoa_atual is None or not pessoa_atual.ativo:
            pessoa_atual = ativas[0] if ativas else None
            self.id_selecionado = pessoa_atual.id if pessoa_atual else None

        self.container_principal.controls = [
            self._construir_lista_pessoas(ativas),
            self._construir_painel_calendario(pessoa_atual),
        ]

    def _construir_lista_pessoas(self, ativas: list[Pessoa]) -> ft.Container:
        """Painel lateral com integrantes e contador de folgas futuras."""
        hoje = date.today()
        itens: list[ft.Control] = []
        for p in ativas:
            selecionada = p.id == self.id_selecionado
            folgas = sum(1 for d in p.indisponibilidades if d >= hoje)
            itens.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                p.nome,
                                weight=ft.FontWeight.BOLD if selecionada else ft.FontWeight.W_500,
                                expand=True,
                            ),
                            criar_selo(f"{folgas}", cor_fundo="#FEE2E2", cor_texto="#991B1B")
                            if folgas > 0
                            else ft.Container(),
                        ]
                    ),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                    border_radius=8,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER if selecionada else ft.Colors.TRANSPARENT,
                    ink=True,
                    on_click=lambda _, pid=p.id: self._selecionar_pessoa(pid),
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Integrantes", size=17, weight=ft.FontWeight.BOLD),
                    ft.Column(itens, spacing=4, scroll=ft.ScrollMode.AUTO, expand=True),
                ],
                spacing=10,
            ),
            width=280,
            padding=ft.Padding.all(14),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _construir_painel_calendario(self, pessoa: Pessoa | None) -> ft.Container:
        """Painel direito com calendário interativo, botão de férias e lista agrupada."""
        if pessoa is None:
            return ft.Container(content=ft.Text("Selecione uma pessoa."), expand=True)

        grade_cal = self._montar_grade_mes(pessoa)
        grupos = agrupar_datas_continuas(pessoa.indisponibilidades)
        chips_grupos: list[ft.Control] = []

        for ini, fim in grupos:
            dias = (fim - ini).days + 1
            rotulo = (
                f"{formatar_dia_completo(ini)}"
                if ini == fim
                else f"{formatar_data(ini)} a {formatar_data(fim)} ({dias} dias)"
            )
            chips_grupos.append(
                ft.Chip(
                    label=ft.Text(rotulo, size=13),
                    delete_icon=ft.Icon(ft.Icons.CLOSE_ROUNDED, size=16),
                    on_delete=lambda _, i=ini, f=fim: self._remover_intervalo(pessoa, i, f),
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(f"Folgas de {pessoa.nome}", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        "Clique em qualquer dia no calendário para marcar ou desmarcar folga.",
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=2,
                            ),
                            ft.FilledButton(
                                "Marcar período (férias)",
                                icon=ft.Icons.DATE_RANGE_ROUNDED,
                                bgcolor=COR_PRIMARIA,
                                color=ft.Colors.WHITE,
                                on_click=lambda _: self._abrir_dialogo_ferias(pessoa),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        wrap=True,
                    ),
                    grade_cal,
                    ft.Divider(),
                    ft.Text("Períodos e dias registrados (agrupados):", weight=ft.FontWeight.BOLD),
                    ft.Row(chips_grupos, spacing=8, run_spacing=8, wrap=True)
                    if chips_grupos
                    else ft.Text("Nenhuma folga cadastrada.", color=ft.Colors.ON_SURFACE_VARIANT),
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=ft.Padding.all(18),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _abrir_dialogo_ferias(self, pessoa: Pessoa) -> None:
        """Abre modal para registrar um período contínuo de férias ou afastamento."""
        hoje = date(self.ano, self.mes, 1)
        sugestao_fim = hoje + timedelta(days=14)
        campo_ini = ft.TextField(
            label="Data inicial (dd/mm/aaaa)",
            value=hoje.strftime("%d/%m/%Y"),
            expand=True,
        )
        campo_fim = ft.TextField(
            label="Data final (dd/mm/aaaa)",
            value=sugestao_fim.strftime("%d/%m/%Y"),
            expand=True,
        )

        def _escolher_data(campo_alvo: ft.TextField, valor_padrao: date) -> None:
            def _ao_mudar(e):
                if e.control.value:
                    dt = e.control.value
                    escolhida = dt.date() if isinstance(dt, datetime) else dt
                    campo_alvo.value = escolhida.strftime("%d/%m/%Y")
                    self.page.update()

            picker = ft.DatePicker(
                value=valor_padrao,
                first_date=date(2025, 1, 1),
                last_date=date(2030, 12, 31),
                on_change=_ao_mudar,
            )
            self.page.show_dialog(picker)

        def _salvar(_) -> None:
            try:
                dt_ini = ler_data(campo_ini.value or "")
                dt_fim = ler_data(campo_fim.value or "")
            except ErroEscala as erro:
                mostrar_erro_modal(self.page, str(erro))
                return

            if dt_fim < dt_ini:
                mostrar_erro_modal(self.page, "A data final não pode ser anterior à data inicial.")
                return

            atual = dt_ini
            qtd = 0
            while atual <= dt_fim:
                pessoa.indisponibilidades.add(atual)
                atual += timedelta(days=1)
                qtd += 1

            self.ano = dt_ini.year
            self.mes = dt_ini.month
            self.page.pop_dialog()
            self.ao_mudar()
            self.atualizar()
            self.page.update()
            mostrar_notificacao(self.page, f"Período de {qtd} dia(s) registrado para {pessoa.nome}!")

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.BEACH_ACCESS_ROUNDED, color=COR_PRIMARIA),
                    ft.Text(f"Marcar período — {pessoa.nome}", weight=ft.FontWeight.BOLD, size=19),
                ],
                spacing=8,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Todos os dias entre a data inicial e a data final serão marcados como indisponíveis:",
                            size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Row(
                            [
                                campo_ini,
                                ft.IconButton(
                                    icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
                                    on_click=lambda _: _escolher_data(campo_ini, hoje),
                                ),
                            ],
                            spacing=6,
                        ),
                        ft.Row(
                            [
                                campo_fim,
                                ft.IconButton(
                                    icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
                                    on_click=lambda _: _escolher_data(campo_fim, sugestao_fim),
                                ),
                            ],
                            spacing=6,
                        ),
                    ],
                    spacing=12,
                    tight=True,
                ),
                width=420,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page.pop_dialog()),
                ft.FilledButton("Salvar período", bgcolor=COR_SUCESSO, color=ft.Colors.WHITE, on_click=_salvar),
            ],
        )
        self.page.show_dialog(dialogo)

    def _montar_grade_mes(self, pessoa: Pessoa) -> ft.Container:
        """Monta o calendário mensal em grade 7x6."""
        cab_mes = ft.Row(
            [
                ft.IconButton(ft.Icons.CHEVRON_LEFT_ROUNDED, on_click=lambda _: self._mudar_mes(-1)),
                ft.Text(f"{MESES_NOMES[self.mes]} de {self.ano}", size=17, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CHEVRON_RIGHT_ROUNDED, on_click=lambda _: self._mudar_mes(1)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        abrev = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        linha_dias_sem = ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        d,
                        weight=ft.FontWeight.BOLD,
                        size=13,
                        color=COR_PRIMARIA if idx >= 5 else ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                )
                for idx, d in enumerate(abrev)
            ]
        )

        linhas_semanas: list[ft.Control] = [cab_mes, linha_dias_sem]
        for semana in calendar.monthcalendar(self.ano, self.mes):
            celulas: list[ft.Control] = []
            for num_dia in semana:
                if num_dia == 0:
                    celulas.append(ft.Container(expand=True, height=40))
                else:
                    dt = date(self.ano, self.mes, num_dia)
                    marcado = dt in pessoa.indisponibilidades
                    celulas.append(
                        ft.Container(
                            content=ft.Text(
                                str(num_dia),
                                weight=ft.FontWeight.BOLD if marcado else ft.FontWeight.W_500,
                                color=ft.Colors.WHITE if marcado else None,
                            ),
                            expand=True,
                            height=40,
                            border_radius=8,
                            bgcolor=COR_PERIGO if marcado else ft.Colors.SURFACE,
                            border=ft.Border.all(1, COR_PERIGO if marcado else ft.Colors.OUTLINE_VARIANT),
                            alignment=ft.Alignment.CENTER,
                            ink=True,
                            on_click=lambda _, d=dt: self._alternar_dia(pessoa, d),
                        )
                    )
            linhas_semanas.append(ft.Row(celulas, spacing=6))

        return ft.Container(
            content=ft.Column(linhas_semanas, spacing=6),
            padding=ft.Padding.all(12),
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _selecionar_pessoa(self, id_pessoa: int) -> None:
        self.id_selecionado = id_pessoa
        self.atualizar()
        self.page.update()

    def _mudar_mes(self, delta: int) -> None:
        novo_mes = self.mes + delta
        if novo_mes < 1:
            self.mes = 12
            self.ano -= 1
        elif novo_mes > 12:
            self.mes = 1
            self.ano += 1
        else:
            self.mes = novo_mes
        self.atualizar()
        self.page.update()

    def _alternar_dia(self, pessoa: Pessoa, dia: date) -> None:
        if dia in pessoa.indisponibilidades:
            pessoa.indisponibilidades.remove(dia)
        else:
            pessoa.indisponibilidades.add(dia)
        self.ao_mudar()
        self.atualizar()
        self.page.update()

    def _remover_intervalo(self, pessoa: Pessoa, ini: date, fim: date) -> None:
        atual = ini
        while atual <= fim:
            pessoa.indisponibilidades.discard(atual)
            atual += timedelta(days=1)
        self.ao_mudar()
        self.atualizar()
        self.page.update()
