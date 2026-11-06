"""Lançador principal usado pelo PyInstaller para gerar o executável único (.exe).

Este arquivo fica na raiz do projeto para que os imports absolutos `src.escala...`
funcionem tanto em desenvolvimento quanto dentro do pacote congelado pelo PyInstaller.
"""

from src.escala.main import iniciar

if __name__ == "__main__":
    iniciar()
