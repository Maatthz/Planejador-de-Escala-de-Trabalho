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

## 04/11/2026 — Fase 2: Histórico, Algoritmo Gerador e Edição

**O que mudou:** implementados os módulos centrais da lógica da escala: contadores de justiça e regra do piso (`historico.py`), algoritmo guloso com ordenação por tupla e formação de duplas (`gerador.py`), e funções de validação, substituição e confirmação manual (`edicao.py`), totalizando 58 testes automatizados 100% verdes.

**Decisões:**
- Fonte única da verdade: contadores de justiça nunca são gravados no JSON, sendo sempre recalculados a partir das escalas confirmadas.
- Regra do piso ("não compensar"): pessoas recém-adicionadas ou que voltam de férias sobem automaticamente para a menor carga entre os presentes da semana.
- Algoritmo guloso baseado em ordenação por tupla lexicográfica de critérios (evita dois plantões na semana, equilibra carga acumulada, folgas recentes e turnos).
- Formação de duplas guiada por função de custo, garantindo que duplas fixas e pessoas experientes sejam pareadas antes de combinações residuais.
- Validação estrita na troca de pessoas (impede trabalhar no mesmo dia), permitindo trocas com folgas mediante avisos informativos.

**Conceitos aprendidos:**
- **Algoritmo guloso (Greedy):** técnica que toma a melhor decisão local a cada etapa (escolhendo as pessoas de maior prioridade para cada plantão), gerando um resultado global eficiente e justo.
- **Ordenação por tupla (ordem lexicográfica):** o Python compara tuplas elemento por elemento; se o primeiro empatar, avalia o segundo, permitindo encadear múltiplos critérios de desempate de forma elegante.
- **Conjuntos (sets):** estruturas de dados que garantem elementos únicos e consultas instantâneas $O(1)$, ideais para verificar indisponibilidades e presenças.
- **Dicionários (dicts):** estruturas de chave-valor usadas para contadores acumulados e busca rápida de registros.
- **Deepcopy:** clonagem profunda de estruturas em memória, usada para simular o avanço dos contadores durante a geração sem alterar os dados reais até o rascunho ser confirmado.
- **Fonte única da verdade:** princípio de arquitetura em que dados derivados (como o quadro de justiça) são sempre calculados a partir dos dados primários (escalas confirmadas), evitando inconsistências.

## 04/11/2026 — Fase 3: Exportação para WhatsApp e Textos de Ajuda

**O que mudou:** implementada a formatação de escala para divulgação no WhatsApp (`exportar.py`) e o catálogo completo de textos explicativos e exemplos para todas as opções de configuração (`textos_ajuda.py`), com 64 testes automatizados verdes.

**Decisões:**
- Formatação fiel ao padrão do WhatsApp: cabeçalhos com emojis (`📅`, `📋`), títulos em negrito (`*texto*`) e espaçamento limpo entre blocos e duplas.
- Todas as 12 configurações do programa mais a opção de backup manual possuem título em linguagem não técnica, explicação clara e exemplo prático.
- Isolamento total de texto: mensagens e dicas ficam centralizadas em `textos_ajuda.py`, facilitando futuras revisões de redação sem alterar código da interface.

**Conceitos aprendidos:**
- **f-strings (Formatted string literals):** recurso do Python (`f"texto {variavel}"`) que permite interpolar valores, expressões e aplicar formatações (como `:02d` ou `.capitalize()`) diretamente dentro de strings com alta performance e legibilidade.
- **Formatação de texto estruturado:** composição de texto em blocos usando métodos como `str.join()`, `strip()` e quebras de linha controladas (`\n\n`) para produzir saídas padronizadas e agradáveis para aplicativos de mensagens.

## 04/11/2026 — Fase 4: Interface Base, Design System e Aba Equipe

**O que mudou:** construída a fundação visual da aplicação com CustomTkinter: tokens visuais e componentes padronizados (`componentes.py`), janela principal com abas e cabeçalho (`janela_principal.py`), e a aba funcional de gerenciamento de membros da equipe (`tela_equipe.py`), atingindo 69 testes automatizados verdes.

**Decisões:**
- Design System semântico: definição rígida de cores (azul para ação principal, verde para confirmação, cinza para secundárias, vermelho para ações destrutivas) e tipografia `Segoe UI` (mínimo 14px).
- Fluxo unidirecional de estado: a tela nunca guarda dados em variáveis paralelas; ela apenas renderiza `DadosDoPrograma` e qualquer modificação dispara `ao_mudar()` (salvamento automático + reconstrução visual).
- Diálogos modais com foco capturado (`grab_set`) e tecla `Esc` para cancelamento rápido.
- Proteção de histórico: membros presentes em escalas confirmadas não podem ser excluídos definitivamente, apenas desativados.

**Conceitos aprendidos:**
- **GUI (Graphical User Interface):** interface gráfica com janelas, botões e campos de texto que substitui comandos de terminal por interação visual intuitiva.
- **Design System:** conjunto centralizado de padrões visuais (tokens de cores, fontes, espaçamentos) e componentes reutilizáveis que garantem identidade visual consistente em todas as telas.
- **Fluxo unidirecional de estado:** arquitetura onde o estado da aplicação flui em sentido único (Dados → Interface → Ação do Usuário → Camada de Lógica → Salvamento → Re-renderização), evitando que telas fiquem dessincronizadas com o arquivo em disco.
- **Eventos:** sinais emitidos pelo sistema operacional em resposta a ações do usuário (clique de mouse, tecla pressionada como `Enter` ou `Esc`).
- **Callbacks:** funções passadas como argumentos para serem executadas quando um evento específico acontecer (ex.: `command=self.ao_mudar`).
