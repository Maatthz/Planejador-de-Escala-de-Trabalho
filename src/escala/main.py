"""Ponto de entrada do programa: configura logging, carrega dados e abre a janela."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType

from src.escala.armazenamento import carregar, pasta_de_dados
from src.escala.interface.componentes import mostrar_erro
from src.escala.interface.janela_principal import JanelaPrincipal


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
    """Configura o registro de logs, carrega os dados e inicia a janela principal."""
    logger = configurar_logging()
    try:
        dados, aviso = carregar()
        app = JanelaPrincipal(dados=dados, aviso_inicial=aviso)

        def _tratar_erro_callback(
            exc_type: type[BaseException],
            exc_value: BaseException,
            exc_tb: TracebackType | None,
        ) -> None:
            logger.error(
                "Erro inesperado em evento da interface:",
                exc_info=(exc_type, exc_value, exc_tb),
            )
            mostrar_erro(
                app,
                "Ocorreu um erro inesperado. Os detalhes foram salvos no arquivo de registro.",
            )

        app.report_callback_exception = _tratar_erro_callback
        app.mainloop()
    except Exception:
        logger.exception("Falha crítica ao iniciar o programa.")
        raise


if __name__ == "__main__":
    iniciar()
