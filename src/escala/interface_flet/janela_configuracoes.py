"""Janela modal de Configurações completas em Flet com ajuda didática em todos os campos."""

from collections.abc import Callable
import copy
from pathlib import Path
import flet as ft

from src.escala.armazenamento import exportar_copia, importar_copia, pasta_de_dados
from src.escala.datas import DIAS_DA_SEMANA
from src.escala.modelos import (
    Configuracao,
    DadosDoPrograma,
    ErroEscala,
    ModeloDeTurno,
)
from src.escala.interface_flet.tema import (
    COR_PERIGO,
    COR_PRIMARIA,
    COR_SUCESSO,
    confirmar_acao,
    criar_bloco_ajuda,
    mostrar_erro_modal,
    mostrar_notificacao,
)


def abrir_dialogo_configuracoes(
    page: ft.Page,
    dados: DadosDoPrograma,
    ao_mudar: Callable[[], None],
) -> None:
    """Abre o diálogo de configurações em abas com explicação + exemplo em cada campo."""
    cfg_temp: Configuracao = copy.deepcopy(dados.configuracao)

    # --- 1. Turnos e Períodos ---
    lista_turnos_col = ft.Column(spacing=6)
    dd_dia_turno = ft.Dropdown(
        label="Dia",
        value="5",
        width=160,
        dense=True,
        options=[ft.DropdownOption(key=str(i), text=nome) for i, nome in enumerate(DIAS_DA_SEMANA)],
    )
    dd_per_turno = ft.Dropdown(
        label="Período",
        value=cfg_temp.periodos[0] if cfg_temp.periodos else "manhã",
        width=165,
        dense=True,
        options=[ft.DropdownOption(key=p, text=p.capitalize()) for p in cfg_temp.periodos],
    )
    dd_dup_turno = ft.Dropdown(
        label="Duplas",
        value="4",
        width=145,
        dense=True,
        options=[ft.DropdownOption(key=str(n), text=f"{n} duplas") for n in range(1, 9)],
    )

    def _renderizar_turnos() -> None:
        lista_turnos_col.controls.clear()
        for idx, t in enumerate(cfg_temp.turnos):
            nome_dia = DIAS_DA_SEMANA[t.dia_da_semana]
            lista_turnos_col.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SCHEDULE_ROUNDED, size=16, color=COR_PRIMARIA),
                        ft.Text(
                            f"{nome_dia} — {t.periodo} — {t.qtd_duplas} dupla(s)",
                            expand=True,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                            icon_color=COR_PERIGO,
                            tooltip="Remover turno",
                            on_click=lambda _, i=idx: _remover_turno(i),
                        ),
                    ]
                )
            )

    def _adicionar_turno(_) -> None:
        dia_idx = int(dd_dia_turno.value or "5")
        per = dd_per_turno.value or "manhã"
        qtd = int(dd_dup_turno.value or "4")
        cfg_temp.turnos.append(ModeloDeTurno(dia_idx, per, qtd))
        _renderizar_turnos()
        page.update()

    def _remover_turno(indice: int) -> None:
        if len(cfg_temp.turnos) <= 1:
            mostrar_erro_modal(page, "É necessário manter pelo menos 1 turno semanal configurado.")
            return
        cfg_temp.turnos.pop(indice)
        _renderizar_turnos()
        page.update()

    _renderizar_turnos()

    campo_periodos = ft.TextField(
        label="Períodos separados por vírgula",
        value=", ".join(cfg_temp.periodos),
        dense=True,
    )

    # --- 2. Feriados, Duplas e Escala ---
    sw_feriados_ativos = ft.Switch(
        label="Gerar plantão nos feriados cadastrados",
        value=cfg_temp.feriados_ativos,
    )
    per_fer_atual = next(iter(cfg_temp.feriado_periodos_padrao.keys()), "manhã")
    qtd_fer_atual = str(cfg_temp.feriado_periodos_padrao.get(per_fer_atual, 4))
    dd_fer_per = ft.Dropdown(
        label="Período padrão",
        value=per_fer_atual,
        width=175,
        dense=True,
        options=[ft.DropdownOption(key=p, text=p.capitalize()) for p in cfg_temp.periodos],
    )
    dd_fer_qtd = ft.Dropdown(
        label="Duplas padrão",
        value=qtd_fer_atual,
        width=160,
        dense=True,
        options=[ft.DropdownOption(key=str(n), text=f"{n} duplas") for n in range(1, 9)],
    )
    dd_modo_exp = ft.Dropdown(
        label="Modo de experiência",
        value=cfg_temp.modo_experiencia,
        width=310,
        dense=True,
        options=[
            ft.DropdownOption(key="preferencia", text="Preferência (recomendado)"),
            ft.DropdownOption(key="obrigatoria", text="Obrigatória (exige 1 por dupla)"),
            ft.DropdownOption(key="ignorar", text="Ignorar experiência"),
        ],
    )
    dd_semanas_padrao = ft.Dropdown(
        label="Semanas por vez",
        value=str(cfg_temp.semanas_por_geracao),
        width=180,
        dense=True,
        options=[ft.DropdownOption(key=str(n), text=f"{n} semana(s)") for n in range(1, 5)],
    )

    # --- 3. Mensagem WhatsApp ---
    campo_titulo_msg = ft.TextField(
        label="Título da mensagem",
        value=cfg_temp.titulo_mensagem,
        dense=True,
    )
    campo_final_msg = ft.TextField(
        label="Texto final (opcional)",
        value=cfg_temp.texto_final_mensagem,
        multiline=True,
        min_lines=2,
        max_lines=3,
    )

    # --- 4. Opções Avançadas (Descanso, Compensação, Pares e Backup) ---
    sw_evitar_seguidas = ft.Switch(
        label="Priorizar descanso para quem trabalhou na semana anterior",
        value=cfg_temp.evitar_semanas_seguidas,
    )
    sw_compensar = ft.Switch(
        label="Cobrar plantões de quem esteve ausente/férias",
        value=cfg_temp.compensar_ausencias,
    )

    ativas = dados.pessoas_ativas()
    opcoes_pessoas = [ft.DropdownOption(key=str(p.id), text=p.nome) for p in ativas]

    def _criar_editor_pares(lista_pares: list[tuple[int, int]], simbolo: str) -> ft.Column:
        col_itens = ft.Column(spacing=4)
        dd_a = ft.Dropdown(label="Pessoa 1", width=210, dense=True, options=opcoes_pessoas)
        dd_b = ft.Dropdown(label="Pessoa 2", width=210, dense=True, options=opcoes_pessoas)

        def _atualizar_pares() -> None:
            col_itens.controls.clear()
            for idx, (id_a, id_b) in enumerate(lista_pares):
                pa = dados.buscar_pessoa(id_a)
                pb = dados.buscar_pessoa(id_b)
                na = pa.nome if pa else f"ID {id_a}"
                nb = pb.nome if pb else f"ID {id_b}"
                col_itens.controls.append(
                    ft.Row(
                        [
                            ft.Text(f"{na}  {simbolo}  {nb}", expand=True, weight=ft.FontWeight.W_500),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=COR_PERIGO,
                                on_click=lambda _, i=idx: _remover_par(i),
                            ),
                        ]
                    )
                )

        def _adicionar_par(_) -> None:
            if not dd_a.value or not dd_b.value:
                return
            ia, ib = int(dd_a.value), int(dd_b.value)
            if ia == ib:
                mostrar_erro_modal(page, "Escolha duas pessoas diferentes para formar o par.")
                return
            par = (min(ia, ib), max(ia, ib))
            if par not in lista_pares:
                lista_pares.append(par)
                _atualizar_pares()
                page.update()

        def _remover_par(idx: int) -> None:
            lista_pares.pop(idx)
            _atualizar_pares()
            page.update()

        _atualizar_pares()
        return ft.Column(
            [
                col_itens,
                ft.Row(
                    [
                        dd_a,
                        dd_b,
                        ft.FilledTonalButton("Adicionar par", icon=ft.Icons.ADD_ROUNDED, on_click=_adicionar_par),
                    ],
                    spacing=8,
                    wrap=True,
                ),
            ],
            spacing=8,
        )

    caminho_padrao_bkp = str(pasta_de_dados() / "copia_seguranca_manual.json")
    campo_caminho_bkp = ft.TextField(
        label="Caminho do arquivo de cópia (.json)",
        value=caminho_padrao_bkp,
        expand=True,
        dense=True,
    )

    def _salvar_copia_manual(_) -> None:
        destino = Path((campo_caminho_bkp.value or caminho_padrao_bkp).strip())
        try:
            exportar_copia(dados, destino)
            mostrar_notificacao(page, f"Cópia salva em: {destino}")
        except Exception as erro:
            mostrar_erro_modal(page, f"Não foi possível salvar a cópia: {erro}")

    def _restaurar_copia_manual(_) -> None:
        origem = Path((campo_caminho_bkp.value or caminho_padrao_bkp).strip())

        def _confirmado() -> None:
            try:
                novos = importar_copia(origem)
                dados.pessoas = novos.pessoas
                dados.configuracao = novos.configuracao
                dados.feriados = novos.feriados
                dados.escalas = novos.escalas
                dados.rascunho = novos.rascunho
                dados.proximo_id = novos.proximo_id
                page.pop_dialog()
                ao_mudar()
                mostrar_notificacao(page, "Cópia de segurança restaurada com sucesso!")
            except ErroEscala as erro:
                mostrar_erro_modal(page, str(erro))

        confirmar_acao(
            page,
            "Restaurar cópia de segurança",
            "Restaurar uma cópia substituirá os dados atuais pelos dados do arquivo. Um backup automático será salvo antes. Continuar?",
            _confirmado,
            texto_confirmar="Restaurar",
        )

    # --- Montagem das seções com criar_bloco_ajuda ---
    conteudo_rolavel = ft.Column(
        [
            criar_bloco_ajuda(
                "turnos",
                ft.Column(
                    [
                        lista_turnos_col,
                        ft.Row(
                            [
                                dd_dia_turno,
                                dd_per_turno,
                                dd_dup_turno,
                                ft.FilledTonalButton(
                                    "Adicionar turno",
                                    icon=ft.Icons.ADD_ROUNDED,
                                    on_click=_adicionar_turno,
                                ),
                            ],
                            spacing=8,
                            wrap=True,
                        ),
                    ],
                    spacing=8,
                ),
            ),
            criar_bloco_ajuda("periodos", campo_periodos),
            criar_bloco_ajuda("feriados_ativos", sw_feriados_ativos),
            criar_bloco_ajuda(
                "feriado_periodos_padrao",
                ft.Row([dd_fer_per, dd_fer_qtd], spacing=10),
            ),
            criar_bloco_ajuda("modo_experiencia", dd_modo_exp),
            criar_bloco_ajuda("semanas_por_geracao", dd_semanas_padrao),
            criar_bloco_ajuda("titulo_mensagem", campo_titulo_msg),
            criar_bloco_ajuda("texto_final_mensagem", campo_final_msg),
            criar_bloco_ajuda("evitar_semanas_seguidas", sw_evitar_seguidas),
            criar_bloco_ajuda("compensar_ausencias", sw_compensar),
            criar_bloco_ajuda("nunca_juntos", _criar_editor_pares(cfg_temp.nunca_juntos, "✕")),
            criar_bloco_ajuda("sempre_juntos", _criar_editor_pares(cfg_temp.sempre_juntos, "+")),
            criar_bloco_ajuda(
                "backup_manual",
                ft.Column(
                    [
                        campo_caminho_bkp,
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    "Salvar cópia",
                                    icon=ft.Icons.DOWNLOAD_ROUNDED,
                                    on_click=_salvar_copia_manual,
                                ),
                                ft.OutlinedButton(
                                    "Restaurar cópia",
                                    icon=ft.Icons.UPLOAD_ROUNDED,
                                    on_click=_restaurar_copia_manual,
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=8,
                ),
            ),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        height=480,
    )

    def _restaurar_padrao(_) -> None:
        def _confirmado() -> None:
            dados.configuracao = Configuracao()
            page.pop_dialog()
            ao_mudar()
            mostrar_notificacao(page, "Configurações restauradas para o padrão de fábrica!")

        confirmar_acao(
            page,
            "Restaurar configurações padrão",
            "Deseja voltar todas as opções para o padrão original? A sua equipe e o histórico de escalas não serão apagados.",
            _confirmado,
            texto_confirmar="Restaurar padrão",
            perigoso=True,
        )

    def _salvar_tudo(_) -> None:
        novos_periodos = [p.strip() for p in (campo_periodos.value or "").split(",") if p.strip()]
        if not novos_periodos:
            mostrar_erro_modal(page, "Informe pelo menos um nome de período (ex.: manhã, tarde).")
            return
        cfg_temp.periodos = novos_periodos
        cfg_temp.feriados_ativos = bool(sw_feriados_ativos.value)
        cfg_temp.feriado_periodos_padrao = {
            dd_fer_per.value or novos_periodos[0]: int(dd_fer_qtd.value or "4")
        }
        cfg_temp.modo_experiencia = dd_modo_exp.value or "preferencia"
        cfg_temp.semanas_por_geracao = int(dd_semanas_padrao.value or "1")
        cfg_temp.titulo_mensagem = (campo_titulo_msg.value or "").strip() or "📋 *ESCALA DE PLANTÃO*"
        cfg_temp.texto_final_mensagem = (campo_final_msg.value or "").strip()
        cfg_temp.evitar_semanas_seguidas = bool(sw_evitar_seguidas.value)
        cfg_temp.compensar_ausencias = bool(sw_compensar.value)

        dados.configuracao = cfg_temp
        page.pop_dialog()
        ao_mudar()
        mostrar_notificacao(page, "Configurações salvas com sucesso!")

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.Icons.SETTINGS_ROUNDED, color=COR_PRIMARIA),
                ft.Text("Configurações do Planejador", weight=ft.FontWeight.BOLD, size=20),
            ],
            spacing=8,
        ),
        content=ft.Container(content=conteudo_rolavel, width=760),
        actions=[
            ft.TextButton(
                "Restaurar padrão",
                icon=ft.Icons.RESTORE_ROUNDED,
                on_click=_restaurar_padrao,
            ),
            ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
            ft.FilledButton(
                "Salvar configurações",
                icon=ft.Icons.CHECK_ROUNDED,
                bgcolor=COR_SUCESSO,
                color=ft.Colors.WHITE,
                on_click=_salvar_tudo,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )
    page.show_dialog(dialogo)
