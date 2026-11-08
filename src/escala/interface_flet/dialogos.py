"""Diálogos modais da aba Escala: Troca inteligente, Justiça (com edição em lote), Histórico e Feriados."""

from collections.abc import Callable
from datetime import date, datetime
import flet as ft

from src.escala.datas import formatar_data, formatar_dia_completo, ler_data
from src.escala.edicao import excluir_escala, pessoas_para_troca, trocar_pessoa
from src.escala.historico import (
    ajustar_contadores_pessoa,
    calcular_contadores,
    quadro_de_justica,
)
from src.escala.modelos import DadosDoPrograma, ErroEscala, Escala, Feriado, Pessoa

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


def _criar_item_substituto(
    pessoa: Pessoa,
    obs: str,
    carga: int,
    ao_escolher: Callable[[int], None],
) -> ft.Container:
    """Monta a linha de um candidato na janela de troca (desabilita se bloqueado no dia)."""
    bloqueado = obs.startswith("já trabalha no dia")
    avatar = ft.CircleAvatar(
        content=ft.Text(iniciais_nome(pessoa.nome), size=12, weight=ft.FontWeight.BOLD),
        radius=17,
        bgcolor=ft.Colors.PRIMARY_CONTAINER if not bloqueado else ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )

    linha_nome: list[ft.Control] = [
        ft.Text(pessoa.nome, size=15, weight=ft.FontWeight.W_600),
    ]
    if pessoa.experiente:
        linha_nome.append(
            ft.Icon(ft.Icons.STAR_ROUNDED, color=COR_ESTRELA, size=18, tooltip="Experiente")
        )

    selos: list[ft.Control] = [
        criar_selo(f"{carga} plantão(ões)", ft.Icons.WORK_HISTORY_OUTLINED),
    ]
    if not obs:
        selos.append(
            criar_selo("Livre", ft.Icons.CHECK_CIRCLE_OUTLINE, "#DCFCE7", "#166534")
        )
    elif bloqueado:
        selos.append(
            criar_selo(obs, ft.Icons.BLOCK_ROUNDED, "#FEE2E2", "#991B1B")
        )
    else:
        selos.append(
            criar_selo(obs, ft.Icons.INFO_OUTLINE_ROUNDED, "#FEF3C7", "#92400E")
        )

    botao = ft.FilledTonalButton(
        "Substituir" if not bloqueado else "Indisponível",
        icon=ft.Icons.SWAP_HORIZ_ROUNDED if not bloqueado else ft.Icons.LOCK_OUTLINE_ROUNDED,
        disabled=bloqueado,
        on_click=lambda _, pid=pessoa.id: ao_escolher(pid),
    )

    return ft.Container(
        content=ft.Row(
            [
                avatar,
                ft.Column(
                    [ft.Row(linha_nome, spacing=4), ft.Row(selos, spacing=6, wrap=True)],
                    spacing=4,
                    expand=True,
                ),
                botao,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        border_radius=10,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        opacity=0.55 if bloqueado else 1.0,
    )


def abrir_dialogo_troca(
    page: ft.Page,
    escala: Escala,
    indice_plantao: int,
    id_sai: int,
    dados: DadosDoPrograma,
    ao_mudar: Callable[[], None],
) -> None:
    """Abre modal de troca com busca por nome, carga de trabalho e prioridade."""
    pessoa_sai = dados.buscar_pessoa(id_sai)
    nome_sai = pessoa_sai.nome if pessoa_sai else f"ID {id_sai}"
    contadores = calcular_contadores(dados)
    opcoes_brutas = pessoas_para_troca(escala, indice_plantao, dados)

    opcoes_ordenadas = sorted(
        opcoes_brutas,
        key=lambda item: (
            item[1].startswith("já trabalha no dia"),
            bool(item[1]),
            contadores.carga.get(item[0].id, 0),
            item[0].nome.lower(),
        ),
    )

    lista_container = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=360)

    def _efetivar(id_entra: int) -> None:
        try:
            avisos = trocar_pessoa(escala, indice_plantao, id_sai, id_entra, dados)
            page.pop_dialog()
            ao_mudar()
            if avisos:
                mostrar_notificacao(page, " • ".join(avisos), ft.Icons.WARNING_ROUNDED, COR_AVISO)
            else:
                mostrar_notificacao(page, "Substituição realizada com sucesso!")
        except ErroEscala as erro:
            mostrar_erro_modal(page, str(erro))

    def _filtrar(termo: str = "") -> None:
        filtro = termo.strip().lower()
        lista_container.controls.clear()
        for cand, obs in opcoes_ordenadas:
            if filtro and filtro not in cand.nome.lower():
                continue
            carga = contadores.carga.get(cand.id, 0)
            lista_container.controls.append(_criar_item_substituto(cand, obs, carga, _efetivar))
        page.update()

    campo_busca = ft.TextField(
        hint_text="Buscar integrante pelo nome...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        autofocus=True,
        on_change=lambda e: _filtrar(e.control.value or ""),
    )
    _filtrar()

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.Icons.SWAP_HORIZ_ROUNDED, color=COR_PRIMARIA),
                ft.Text(f"Substituir {nome_sai}", weight=ft.FontWeight.BOLD, size=19),
            ],
            spacing=8,
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Ordenado por disponibilidade e menor número de plantões realizados:",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    campo_busca,
                    lista_container,
                ],
                spacing=12,
                tight=True,
            ),
            width=560,
        ),
        actions=[ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog())],
    )
    page.show_dialog(dialogo)


def abrir_dialogo_justica(
    page: ft.Page,
    dados: DadosDoPrograma,
    ao_mudar: Callable[[], None] | None = None,
) -> None:
    """Exibe o Quadro de Justiça com opção de edição manual em lote dos contadores."""
    modo_edicao = False
    campos_edicao: dict[int, tuple[ft.TextField, ft.TextField, ft.TextField]] = {}
    area_tabela = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)
    acoes_container = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _montar_conteudo() -> None:
        campos_edicao.clear()
        linhas_justica = quadro_de_justica(dados)
        linhas_tabela: list[ft.DataRow] = []

        for item in linhas_justica:
            ult_str = (
                item.ultimo_plantao.strftime("%d/%m/%Y")
                if item.ultimo_plantao
                else ""
            )
            empatado = item.carga_justica > item.plantoes_reais
            selo_obs = (
                criar_selo("Entrou/voltou empatado", ft.Icons.BALANCE_ROUNDED, "#FEF3C7", "#92400E")
                if empatado
                else criar_selo("Regular", ft.Icons.CHECK_ROUNDED)
            )
            celula_nome = ft.Row(
                [
                    ft.Text(item.pessoa.nome, weight=ft.FontWeight.W_600),
                    ft.Icon(ft.Icons.STAR_ROUNDED, color=COR_ESTRELA, size=16)
                    if item.pessoa.experiente
                    else ft.Container(),
                ],
                spacing=4,
            )

            if not modo_edicao:
                cel_plantoes: ft.Control = ft.Text(str(item.plantoes_reais))
                cel_feriados: ft.Control = ft.Text(str(item.feriados_trabalhados))
                cel_ultimo: ft.Control = ft.Text(ult_str if ult_str else "Nunca")
            else:
                tf_p = ft.TextField(
                    value=str(item.plantoes_reais),
                    width=80,
                    dense=True,
                    text_align=ft.TextAlign.CENTER,
                )
                tf_f = ft.TextField(
                    value=str(item.feriados_trabalhados),
                    width=80,
                    dense=True,
                    text_align=ft.TextAlign.CENTER,
                )
                tf_u = ft.TextField(
                    value=ult_str,
                    hint_text="dd/mm/aaaa",
                    width=130,
                    dense=True,
                )
                campos_edicao[item.pessoa.id] = (tf_p, tf_f, tf_u)
                cel_plantoes = tf_p
                cel_feriados = tf_f
                cel_ultimo = tf_u

            linhas_tabela.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item.posicao}º", weight=ft.FontWeight.BOLD)),
                        ft.DataCell(celula_nome),
                        ft.DataCell(cel_plantoes),
                        ft.DataCell(cel_feriados),
                        ft.DataCell(cel_ultimo),
                        ft.DataCell(selo_obs),
                    ]
                )
            )

        tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fila", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Integrante", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Plantões", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Feriados", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Último Plantão", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Situação do Piso", weight=ft.FontWeight.BOLD)),
            ],
            rows=linhas_tabela,
            heading_row_height=42,
            data_row_max_height=54 if modo_edicao else 46,
        )
        area_tabela.controls = [tabela]

        if not modo_edicao:
            acoes_container.controls = [
                ft.OutlinedButton(
                    "Editar manualmente",
                    icon=ft.Icons.EDIT_NOTE_ROUNDED,
                    on_click=_ativar_edicao,
                ),
                ft.FilledButton("Fechar", on_click=lambda _: page.pop_dialog()),
            ]
        else:
            acoes_container.controls = [
                ft.TextButton("Cancelar edição", on_click=_cancelar_edicao),
                ft.FilledButton(
                    "Salvar alterações",
                    icon=ft.Icons.SAVE_ROUNDED,
                    bgcolor=COR_SUCESSO,
                    color=ft.Colors.WHITE,
                    on_click=_salvar_edicao_lote,
                ),
            ]

    def _ativar_edicao(_) -> None:
        nonlocal modo_edicao
        modo_edicao = True
        _montar_conteudo()
        page.update()

    def _cancelar_edicao(_) -> None:
        nonlocal modo_edicao
        modo_edicao = False
        _montar_conteudo()
        page.update()

    def _salvar_edicao_lote(_) -> None:
        nonlocal modo_edicao
        ajustes_validados: list[tuple[int, int, int, date | None]] = []
        for id_pessoa, (tf_p, tf_f, tf_u) in campos_edicao.items():
            pessoa = dados.buscar_pessoa(id_pessoa)
            nome_p = pessoa.nome if pessoa else f"ID {id_pessoa}"
            try:
                qtd_p = int((tf_p.value or "").strip())
                qtd_f = int((tf_f.value or "").strip())
            except ValueError:
                mostrar_erro_modal(
                    page,
                    f"Os números de plantões e feriados de '{nome_p}' devem ser inteiros.",
                )
                return

            txt_data = (tf_u.value or "").strip()
            if not txt_data or txt_data.lower() == "nunca":
                data_ult = None
            else:
                try:
                    data_ult = ler_data(txt_data)
                except ErroEscala as erro:
                    mostrar_erro_modal(page, f"Data inválida para '{nome_p}': {erro}")
                    return

            ajustes_validados.append((id_pessoa, qtd_p, qtd_f, data_ult))

        try:
            for id_pessoa, qtd_p, qtd_f, data_ult in ajustes_validados:
                ajustar_contadores_pessoa(dados, id_pessoa, qtd_p, qtd_f, data_ult)
        except ErroEscala as erro:
            mostrar_erro_modal(page, str(erro))
            return

        modo_edicao = False
        if ao_mudar is not None:
            ao_mudar()
        _montar_conteudo()
        page.update()
        mostrar_notificacao(page, "Contadores de justiça atualizados e reordenados!")

    _montar_conteudo()
    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.Icons.LEADERBOARD_ROUNDED, color=COR_PRIMARIA),
                ft.Text("Quadro de Justiça e Prioridade", weight=ft.FontWeight.BOLD, size=20),
            ],
            spacing=8,
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Quem está no topo da fila tem prioridade na próxima geração. "
                        "Pessoas novas ou que voltam de férias entram empatadas com a menor carga.",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    area_tabela,
                    acoes_container,
                ],
                spacing=12,
                tight=True,
            ),
            width=780,
        ),
    )
    page.show_dialog(dialogo)


def abrir_dialogo_historico(
    page: ft.Page,
    dados: DadosDoPrograma,
    ao_selecionar_indice: Callable[[int], None],
    ao_copiar_escala: Callable[[Escala], None],
    ao_mudar: Callable[[], None],
) -> None:
    """Lista escalas confirmadas permitindo visualizar/editar mesmo com rascunho ativo."""
    lista = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=380)

    def _renderizar() -> None:
        lista.controls.clear()
        if not dados.escalas:
            lista.controls.append(
                ft.Container(
                    content=ft.Text("Nenhuma escala confirmada no histórico ainda.", size=15),
                    padding=ft.Padding.all(24),
                )
            )
            page.update()
            return

        for idx in reversed(range(len(dados.escalas))):
            esc = dados.escalas[idx]
            periodo = f"{formatar_data(esc.primeiro_dia())} a {formatar_data(esc.ultimo_dia())}"
            gerada = esc.gerada_em.strftime("%d/%m/%Y às %H:%M")

            def _ver(_, i=idx):
                page.pop_dialog()
                ao_selecionar_indice(i)

            def _excluir(_, i=idx):
                def _confirmado():
                    excluir_escala(dados, i)
                    ao_mudar()
                    _renderizar()
                    mostrar_notificacao(page, "Escala removida e justiça recalculada.")

                confirmar_acao(
                    page,
                    "Excluir escala do histórico",
                    "Deseja excluir esta escala confirmada? Os contadores de justiça serão recalculados.",
                    _confirmado,
                    texto_confirmar="Excluir",
                    perigoso=True,
                )

            cartao = ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"Período: {periodo}", size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f"Confirmada em {gerada} • {len(esc.plantoes)} plantão(ões)",
                                    size=13,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                ft.FilledTonalButton(
                                    "Visualizar / Editar",
                                    icon=ft.Icons.VISIBILITY_ROUNDED,
                                    on_click=_ver,
                                ),
                                ft.OutlinedButton(
                                    "Copiar",
                                    icon=ft.Icons.CONTENT_COPY_ROUNDED,
                                    on_click=lambda _, e=esc: ao_copiar_escala(e),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                    icon_color=COR_PERIGO,
                                    tooltip="Excluir escala",
                                    on_click=_excluir,
                                ),
                            ],
                            spacing=6,
                        ),
                    ]
                ),
                padding=ft.Padding.all(14),
                border_radius=10,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            )
            lista.controls.append(cartao)
        page.update()

    _renderizar()
    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.Icons.HISTORY_ROUNDED, color=COR_PRIMARIA),
                ft.Text("Escalas Anteriores Confirmadas", weight=ft.FontWeight.BOLD, size=20),
            ],
            spacing=8,
        ),
        content=ft.Container(content=lista, width=680),
        actions=[ft.TextButton("Fechar", on_click=lambda _: page.pop_dialog())],
    )
    page.show_dialog(dialogo)


def abrir_dialogo_feriados(
    page: ft.Page,
    dados: DadosDoPrograma,
    data_sugerida: date,
    ao_mudar: Callable[[], None],
) -> None:
    """Gerencia feriados com seletor de data em calendário nativo do Flet."""
    campo_data = ft.TextField(
        label="Data",
        value=data_sugerida.strftime("%d/%m/%Y"),
        width=155,
    )
    campo_nome = ft.TextField(label="Nome do feriado", hint_text="Ex.: Natal", expand=True)
    periodos_padrao = dados.configuracao.feriado_periodos_padrao
    per_inicial = (
        next(iter(periodos_padrao.keys()))
        if periodos_padrao
        else (dados.configuracao.periodos[0] if dados.configuracao.periodos else "manhã")
    )
    dup_inicial = str(periodos_padrao.get(per_inicial, 4))

    dd_periodo = ft.Dropdown(
        label="Período",
        value=per_inicial,
        width=170,
        options=[ft.DropdownOption(key=p, text=p.capitalize()) for p in dados.configuracao.periodos],
    )
    dd_duplas = ft.Dropdown(
        label="Duplas",
        value=dup_inicial,
        width=145,
        options=[ft.DropdownOption(key=str(n), text=f"{n} duplas") for n in range(1, 7)],
    )
    lista_feriados = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=220)

    def _abrir_calendario(_):
        def _ao_escolher_data(e):
            if e.control.value:
                dt = e.control.value
                data_escolhida = dt.date() if isinstance(dt, datetime) else dt
                campo_data.value = data_escolhida.strftime("%d/%m/%Y")
                page.update()

        picker = ft.DatePicker(
            value=data_sugerida,
            first_date=date(2025, 1, 1),
            last_date=date(2030, 12, 31),
            on_change=_ao_escolher_data,
        )
        page.show_dialog(picker)

    def _atualizar_lista() -> None:
        lista_feriados.controls.clear()
        if not dados.feriados:
            lista_feriados.controls.append(
                ft.Text("Nenhum feriado cadastrado.", color=ft.Colors.ON_SURFACE_VARIANT)
            )
            page.update()
            return
        for fer in sorted(dados.feriados, key=lambda f: f.data):
            resumo_per = ", ".join(f"{p} ({q} duplas)" for p, q in fer.periodos.items())
            lista_feriados.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CELEBRATION_ROUNDED, color=COR_AVISO, size=18),
                            ft.Text(
                                f"{formatar_dia_completo(fer.data)} — {fer.nome or 'Feriado'} ({resumo_per})",
                                expand=True,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=COR_PERIGO,
                                on_click=lambda _, f=fer: _remover(f),
                            ),
                        ]
                    ),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                    border_radius=8,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                )
            )
        page.update()

    def _remover(feriado: Feriado) -> None:
        if feriado in dados.feriados:
            dados.feriados.remove(feriado)
            ao_mudar()
            _atualizar_lista()

    def _adicionar(_) -> None:
        try:
            dt = ler_data(campo_data.value or "")
        except ErroEscala as erro:
            mostrar_erro_modal(page, str(erro))
            return
        if any(f.data == dt for f in dados.feriados):
            mostrar_erro_modal(page, "Já existe um feriado cadastrado nesta data.")
            return
        dados.feriados.append(
            Feriado(
                data=dt,
                nome=(campo_nome.value or "").strip(),
                periodos={dd_periodo.value or "manhã": int(dd_duplas.value or "4")},
            )
        )
        campo_nome.value = ""
        ao_mudar()
        _atualizar_lista()
        mostrar_notificacao(page, "Feriado salvo com sucesso!")

    _atualizar_lista()
    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.Icons.CELEBRATION_ROUNDED, color=COR_AVISO),
                ft.Text("Feriados e Datas Especiais", weight=ft.FontWeight.BOLD, size=20),
            ],
            spacing=8,
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            campo_data,
                            ft.IconButton(
                                icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
                                tooltip="Escolher no calendário",
                                on_click=_abrir_calendario,
                            ),
                            campo_nome,
                        ],
                        spacing=8,
                    ),
                    ft.Row(
                        [
                            dd_periodo,
                            dd_duplas,
                            ft.FilledButton(
                                "Salvar feriado",
                                icon=ft.Icons.ADD_ROUNDED,
                                on_click=_adicionar,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(),
                    ft.Text("Feriados cadastrados:", weight=ft.FontWeight.BOLD),
                    lista_feriados,
                ],
                spacing=12,
                tight=True,
            ),
            width=580,
        ),
        actions=[ft.TextButton("Fechar", on_click=lambda _: page.pop_dialog())],
    )
    page.show_dialog(dialogo)
