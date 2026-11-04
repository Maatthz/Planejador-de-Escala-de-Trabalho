"""Ponto de entrada do programa: inicializa dados e abre a janela principal."""

from src.escala.interface.janela_principal import JanelaPrincipal


def iniciar() -> None:
    """Cria a janela principal e inicia o laço de eventos da interface."""
    app = JanelaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    iniciar()
