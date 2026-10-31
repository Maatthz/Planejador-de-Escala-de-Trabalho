"""Ponto de entrada do programa: abre a janela principal.

Por enquanto (Fase 0) só abre uma janela de teste, para confirmar
que o CustomTkinter foi instalado corretamente.
"""

import customtkinter as ctk

from src.escala.versao import VERSAO


def iniciar() -> None:
    """Cria a janela e inicia o laço de eventos da interface."""
    janela = ctk.CTk()
    janela.title(f"Planejador de Escala — versão {VERSAO}")
    janela.geometry("600x300")

    texto = ctk.CTkLabel(janela, text="Ambiente pronto! 🎉", font=("Segoe UI", 24))
    texto.pack(expand=True)

    # mainloop() fica "escutando" cliques e teclas até a janela ser fechada
    janela.mainloop()


# Só executa iniciar() se este arquivo for rodado diretamente
# (e não quando for importado por outro arquivo, como nos testes).
if __name__ == "__main__":
    iniciar()
