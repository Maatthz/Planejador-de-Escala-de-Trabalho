"""Teste inicial: garante que o pytest funciona e que a versão está no formato certo."""

from src.escala.versao import VERSAO


def test_versao_tem_tres_numeros() -> None:
    """A versão deve ter o formato MAIOR.MENOR.CORREÇÃO, ex.: 1.2.0."""
    partes = VERSAO.split(".")
    assert len(partes) == 3
    assert all(parte.isdigit() for parte in partes)
