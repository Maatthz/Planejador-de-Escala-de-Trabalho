"""Utilidades de manipulação e formatação de datas em português.

Funções seguras para lidar com calendário semanal, anos ISO e formatação
sem depender de configurações regionais (locale) do sistema operacional.
"""

from datetime import date, timedelta

from src.escala.modelos import ErroEscala

DIAS_DA_SEMANA: list[str] = [
    "Segunda",
    "Terça",
    "Quarta",
    "Quinta",
    "Sexta",
    "Sábado",
    "Domingo",
]


def inicio_da_semana(dia: date) -> date:
    """Retorna a segunda-feira da semana de `dia`."""
    return dia - timedelta(days=dia.weekday())


def chave_da_semana(dia: date) -> tuple[int, int]:
    """Identifica a semana: (ano ISO, nº da semana ISO)."""
    iso = dia.isocalendar()
    return (iso.year, iso.week)


def dias_do_periodo(inicio: date, qtd_semanas: int) -> list[date]:
    """Todos os dias de `qtd_semanas` semanas a partir da segunda-feira de `inicio`."""
    segunda = inicio_da_semana(inicio)
    total_dias = qtd_semanas * 7
    return [segunda + timedelta(days=i) for i in range(total_dias)]


def formatar_data(dia: date) -> str:
    """Ex.: date(2026, 11, 7) -> '07/11'."""
    return f"{dia.day:02d}/{dia.month:02d}"


def formatar_dia_completo(dia: date) -> str:
    """Ex.: date(2026, 11, 7) -> 'Sábado, 07/11'."""
    nome_dia = DIAS_DA_SEMANA[dia.weekday()]
    return f"{nome_dia}, {formatar_data(dia)}"


def ler_data(texto: str) -> date:
    """Converte 'dd/mm/aaaa' em date. Levanta ErroEscala('Data inválida: use o formato 25/12/2026.')."""
    partes = texto.strip().split("/")
    if len(partes) != 3 or len(partes[2]) != 4:
        raise ErroEscala("Data inválida: use o formato 25/12/2026.")

    try:
        dia = int(partes[0])
        mes = int(partes[1])
        ano = int(partes[2])
        return date(ano, mes, dia)
    except (ValueError, TypeError):
        raise ErroEscala("Data inválida: use o formato 25/12/2026.")
