"""Ponto de entrada do programa: configura logging, trava de instância única, carrega dados e abre a janela Flet."""

import logging
from logging.handlers import RotatingFileHandler
import msvcrt
import os
from pathlib import Path
import sys
from typing import TextIO

from src.escala.armazenamento import carregar, pasta_de_dados
from src.escala.interface_flet.app_flet import iniciar_app_flet

_ARQUIVO_TRAVA: TextIO | None = None


def _garantir_streams_padrao() -> None:
    """No modo --windowed do PyInstaller, redireciona stdout/stderr nulos para devnull."""
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")


def adquirir_trava_instancia(pasta: Path | None = None) -> bool:
    """Garante que apenas uma instância do programa rode por vez na mesma pasta de dados."""
    global _ARQUIVO_TRAVA
    diretorio = pasta if pasta is not None else pasta_de_dados()
    diretorio.mkdir(parents=True, exist_ok=True)
    caminho_lock = diretorio / "programa.lock"
    try:
        arq = caminho_lock.open("a+", encoding="utf-8")
        arq.seek(0)
        msvcrt.locking(arq.fileno(), msvcrt.LK_NBLCK, 1)
        _ARQUIVO_TRAVA = arq
        return True
    except OSError:
        return False


def configurar_logging(pasta: Path | None = None) -> logging.Logger:
    """Configura o arquivo registro.log (1 MB, até 3 arquivos) na pasta de dados."""
    diretorio = pasta if pasta is not None else pasta_de_dados()
    diretorio.mkdir(parents=True, exist_ok=True)
    arquivo_log = diretorio / "registro.log"

    logger = logging.getLogger("escala")
    logger.setLevel(logging.INFO)

    caminhos_existentes = {
        getattr(h, "baseFilename", None) for h in logger.handlers
    }
    if str(arquivo_log.resolve()) not in caminhos_existentes:
        handler = RotatingFileHandler(
            arquivo_log,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        formato = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formato)
        logger.addHandler(handler)

    return logger


def iniciar() -> None:
    """Configura o registro de logs, carrega os dados e inicia a janela principal em Flet."""
    _garantir_streams_padrao()
    logger = configurar_logging()
    if not adquirir_trava_instancia():
        logger.warning("Tentativa de abrir segunda instância bloqueada (programa.lock ativo).")
        return

    try:
        dados, aviso = carregar()
        iniciar_app_flet(dados=dados, aviso_inicial=aviso)
    except Exception:
        logger.exception("Falha crítica ao iniciar o programa.")
        raise


if __name__ == "__main__":
    iniciar()
