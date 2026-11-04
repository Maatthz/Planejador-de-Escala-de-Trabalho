"""Fixtures compartilhadas para os testes do Planejador de Escala."""

from datetime import date
import os
from pathlib import Path
import tkinter
import pytest

from src.escala.modelos import Configuracao, DadosDoPrograma, Pessoa

try:
    _tcl_lib = tkinter.Tcl().eval("info library")
    if _tcl_lib and os.path.exists(_tcl_lib):
        os.environ.setdefault("TCL_LIBRARY", _tcl_lib)
except Exception:
    pass


@pytest.fixture
def pasta_temporaria(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Configura PLANEJADOR_PASTA_DADOS para uma pasta temporária isolada."""
    monkeypatch.setenv("PLANEJADOR_PASTA_DADOS", str(tmp_path))
    return tmp_path


@pytest.fixture
def equipe_28() -> list[Pessoa]:
    """Cria uma equipe de 28 pessoas (10 experientes) com data de entrada antiga (01/01/2026)."""
    nomes = [
        "Ana", "Bruno", "Carla", "Diego", "Elisa", "Fábio", "Gabi", "Hugo",
        "Íris", "João", "Kelly", "Lucas", "Marina", "Natã", "Olívia", "Pedro",
        "Quênia", "Rafael", "Sara", "Thiago", "Úrsula", "Victor", "Wanessa", "Xavier",
        "Yasmin", "Zé", "Arthur", "Bia",
    ]
    pessoas: list[Pessoa] = []
    for i, nome in enumerate(nomes, start=1):
        experiente = i <= 10
        pessoas.append(
            Pessoa(
                id=i,
                nome=nome,
                experiente=experiente,
                ativo=True,
                data_entrada=date(2026, 1, 1),
                indisponibilidades=set(),
            )
        )
    return pessoas


@pytest.fixture
def dados_padrao(equipe_28: list[Pessoa]) -> DadosDoPrograma:
    """Retorna uma instância de DadosDoPrograma com a equipe de 28 pessoas e configuração padrão."""
    return DadosDoPrograma(
        pessoas=equipe_28,
        configuracao=Configuracao(),
        feriados=[],
        escalas=[],
        rascunho=None,
        proximo_id=len(equipe_28) + 1,
    )
