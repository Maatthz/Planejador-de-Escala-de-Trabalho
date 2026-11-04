"""Testes para o módulo de textos de ajuda."""

from dataclasses import fields
import pytest

from src.escala.modelos import Configuracao
from src.escala.textos_ajuda import AJUDA, TextoAjuda, obter_ajuda


def test_todos_os_campos_de_configuracao_possuem_ajuda() -> None:
    """Garante que todos os campos da dataclass Configuracao possuem ajuda cadastrada."""
    campos_configuracao = {f.name for f in fields(Configuracao)}

    for campo in campos_configuracao:
        assert campo in AJUDA, f"Campo de configuração '{campo}' não possui texto de ajuda em AJUDA."


def test_backup_manual_possui_ajuda() -> None:
    """A opção avançada backup_manual (não é campo direto de Configuracao) deve possuir ajuda."""
    assert "backup_manual" in AJUDA


def test_textos_de_ajuda_preenchidos_corretamente() -> None:
    """Verifica se todos os textos de ajuda possuem título, explicação e exemplo não vazios."""
    for chave, ajuda in AJUDA.items():
        assert isinstance(ajuda, TextoAjuda)
        assert ajuda.titulo.strip(), f"Título da ajuda para '{chave}' está vazio."
        assert ajuda.explicacao.strip(), f"Explicação da ajuda para '{chave}' está vazia."
        assert ajuda.exemplo.strip(), f"Exemplo da ajuda para '{chave}' está vazio."


def test_obter_ajuda_sucesso_e_chave_inexistente() -> None:
    """obter_ajuda deve retornar o objeto correto ou levantar KeyError se a chave não existir."""
    ajuda = obter_ajuda("turnos")
    assert ajuda.titulo == "Turnos da semana"

    with pytest.raises(KeyError):
        obter_ajuda("chave_que_nao_existe")
