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

## 04/11/2026 — Regras de negócio definidas

**O que mudou:** o `AGENTS.md` foi atualizado com as respostas sobre como a escala funciona de verdade.

**Decisões:**
- O plantão é por **turno** (meio período), não pelo fim de semana inteiro. Padrão: 4 duplas sábado manhã + 4 duplas domingo tarde, configurável.
- **Feriados** entram na escala, e os plantões de feriado são distribuídos por igual (contador separado).
- Pessoas podem ser marcadas como **experientes**; o algoritmo tenta colocar 1 por dupla (preferência, não regra).
- A escala gerada é um **rascunho** até ser confirmada; só escalas confirmadas contam para a justiça.
- Removido o Excel (`openpyxl`): a divulgação é só pelo WhatsApp.

**Conceitos aprendidos:**
- **Levantamento de requisitos:** entender as regras do negócio antes de programar.
- **Regras obrigatórias × desejáveis** (restrições *rígidas* × *flexíveis*): as primeiras nunca podem ser quebradas; as outras o algoritmo tenta otimizar.
- **Configuração × código fixo:** deixar valores que podem mudar (turnos, nº de duplas) como dados, não "chumbados" no código.
- **Função de custo:** dar uma nota a cada opção (ex.: custo de um par) e escolher a menor.
