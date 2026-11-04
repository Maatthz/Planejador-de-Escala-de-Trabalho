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

## 04/11/2026 — Arquitetura final (debate "advogado do diabo")

**O que mudou:** o `AGENTS.md` foi reescrito como instrução para uma IA programadora: assinaturas de funções,
formato do JSON, algoritmo detalhado, fases com critério de "pronto" e testes obrigatórios.

**Decisões do debate:**
- Pessoa nova/volta de férias **não compensa**: entra empatada com quem menos trabalhou (regra do "piso").
- Escalas confirmadas podem ser editadas; os contadores são recalculados do histórico.
- Uma só usuária → sem login. Risco real é corromper o arquivo → **salvamento atômico** + recuperação por backup.
- Atualização verificada por **SHA-256**.
- Tudo configurável, com **explicação + exemplo** em cada opção; padrões = respostas do desenvolvedor.

**Conceitos aprendidos:**
- **Pontos cegos / advogado do diabo:** procurar falhas antes de programar é mais barato que corrigir depois.
- **Fonte única da verdade:** não guardar a mesma informação em dois lugares (contadores são calculados, não salvos).
- **Salvamento atômico:** gravar num arquivo temporário e trocar de uma vez, para nunca ficar "pela metade".
- **Hash (SHA-256):** "impressão digital" de um arquivo; se um byte mudar, o hash muda.
- **Parametrização:** regras viram dados configuráveis.
- **YAGNI:** não construir o que ninguém precisa ainda.
- **Contrato (assinaturas):** definir entradas/saídas das funções antes de implementar.

## 04/11/2026 — Arquitetura de Frontend (UI/UX) e Quadro de Justiça

**O que mudou:** a seção 10 do `AGENTS.md` foi expandida com regras rígidas de arquitetura de Frontend,
Design System e usabilidade (UI/UX), e foi adicionado o **📊 Quadro de justiça** (`quadro_de_justica` em `historico.py`
e `janela_justica.py` na interface).

**Decisões:**
- **Fluxo unidirecional de estado** na interface: `DadosDoPrograma` é a única fonte de verdade; as telas nunca guardam estado duplicado.
- **Design System com tokens visuais** em `componentes.py`: paleta semântica (azul = ação principal, verde = confirmar/copiar, cinza = secundário, vermelho = destrutivo, amarelo = aviso), tipografia `Segoe UI` (mínimo 14px para corpo) e espaçamento padronizado.
- **Quadro de justiça**: mostra a ordem atual da fila, quantos plantões/feriados cada pessoa realmente fez, a data do último plantão e se entrou/voltou empatada pelo piso.

**Conceitos aprendidos:**
- **Design System / Tokens visuais:** centralizar cores, fontes e tamanhos em constantes para manter consistência visual e facilitar mudanças.
- **Fluxo unidirecional de estado (MVC / Flux):** Dados → Tela → Ação → Lógica → Salvar → Atualizar tela; evita que a tela mostre uma coisa e o arquivo tenha outra.
- **Hierarquia visual e cores semânticas:** destacar apenas 1 botão principal por área para guiar o olhar do usuário.
- **Lei de Fitts:** quanto maior e mais próximo o botão, mais fácil e rápido é clicar nele (importante para usuários leigos).
- **Heurísticas de Nielsen (Visibilidade do status e Estados vazios):** o programa sempre informa o que está acontecendo (ex.: faixa "Rascunho", botão "✅ Copiado!", textos explicativos quando uma lista está vazia).

## 04/11/2026 — Fase 1: Modelos, Datas e Armazenamento

**O que mudou:** implementados os módulos fundamentais de dados (`modelos.py`), utilidades de calendário sem dependência de locale (`datas.py`), sistema de persistência com salvamento atômico, backups automáticos e recuperação de falhas (`armazenamento.py`), além de suite completa de 35 testes automatizados cobrindo todos os cenários.

**Decisões:**
- Utilização de `dataclasses` com `field(default_factory=...)` para estruturas limpas e com valores padrão seguros.
- `ErroEscala` centralizado em `modelos.py` para evitar importações circulares e padronizar mensagens amigáveis para o usuário.
- Formatação e leitura de datas manuais em português sem depender da configuração de idioma (`locale`) do Windows.
- Gravação atômica via arquivo temporário (`.tmp` + `os.replace`) e rotação automática de no máximo 10 backups.
- Recuperação transparente: se `dados.json` for corrompido, o sistema busca automaticamente o backup válido mais recente e restaura.

**Conceitos aprendidos:**
- **Dataclass:** funcionalidade do Python que gera automaticamente construtor (`__init__`), representação (`__repr__`) e métodos essenciais para classes focadas em dados.
- **Type hints:** anotações de tipos no código que tornam os contratos explícitos e previnem erros sutis.
- **Serialização e Desserialização:** processo de converter objetos em memória para texto estruturado (JSON/dicionários) e reconstruí-los de volta em objetos de classes.
- **Salvamento atômico:** técnica de gravar em um arquivo temporário e renomear de uma vez só (`os.replace`), evitando corromper dados se o computador desligar no meio.
- **Pathlib:** módulo moderno do Python para manipular caminhos de pastas e arquivos de forma segura e independente de sistema operacional.
- **Exceções customizadas:** classes de erro próprias (como `ErroEscala`) usadas para separar erros esperados de regras de negócio de falhas inesperadas de programação.
