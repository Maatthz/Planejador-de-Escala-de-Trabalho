"""Teste inicial: garante que o pytest funciona, a versão e o ponto de entrada estão corretos."""

from pathlib import Path

import iniciar as lancador
from src.escala.main import configurar_logging, iniciar
from src.escala.versao import VERSAO


def test_versao_tem_tres_numeros() -> None:
    """A versão deve ter o formato MAIOR.MENOR.CORREÇÃO, ex.: 1.2.0."""
    partes = VERSAO.split(".")
    assert len(partes) == 3
    assert all(parte.isdigit() for parte in partes)


def test_lancador_iniciar_e_logging(pasta_temporaria: Path) -> None:
    """Garante que iniciar.py aponta para main.iniciar e configurar_logging cria registro.log."""
    assert lancador.iniciar is iniciar

    logger = configurar_logging(pasta_temporaria)
    logger.info("Teste de inicialização do registro.log")

    for h in list(logger.handlers):
        h.flush()
        if getattr(h, "baseFilename", None) == str((pasta_temporaria / "registro.log").resolve()):
            h.close()
            logger.removeHandler(h)

    arquivo_log = pasta_temporaria / "registro.log"
    assert arquivo_log.exists()
    assert "Teste de inicialização do registro.log" in arquivo_log.read_text(encoding="utf-8")
