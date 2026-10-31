# Diário de Aprendizado

## 30/10/2026 — Fase 0: Ambiente

**O que mudou:** criado o repositório Git, o ambiente virtual (`.venv`), os arquivos de dependências,
a estrutura de pastas `src/escala` e `tests`, uma janela de teste e o primeiro teste automatizado.

**Decisões:**
- Mantido CustomTkinter (desktop, `.exe`) em vez de Streamlit: funciona sem internet e os dados ficam no PC.
- Dependências separadas: `requirements.txt` (programa) e `requirements-dev.txt` (desenvolvimento).

**Conceitos aprendidos:**
- **Ambiente virtual (venv):** pasta isolada com Python e bibliotecas só deste projeto.
- **pip / requirements.txt:** gerenciador de pacotes e lista de dependências.
- **Git:** controle de versão; `.gitignore` diz o que não deve ser versionado.
- **Pacote Python:** pasta com `__init__.py`, permite `import` organizado.
- **`if __name__ == "__main__"`:** código que só roda quando o arquivo é executado diretamente.
- **Laço de eventos (`mainloop`)**: a interface fica esperando ações do usuário.
- **pytest:** funções `test_*` com `assert` verificam se o código está correto.
