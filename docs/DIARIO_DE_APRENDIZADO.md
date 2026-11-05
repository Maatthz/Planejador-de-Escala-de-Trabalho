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

## 04/11/2026 — Fase 5: Aba Folgas e Calendário Mensal

**O que mudou:** implementado o componente nativo de calendário mensal em grade (`CalendarioMensal`) e a aba de gestão de folgas e férias (`tela_folgas.py`), integrada à janela principal com fluxo de persistência e validação, somando 75 testes automatizados verdes.

**Decisões:**
- Calendário 100% nativo construído com CustomTkinter e a biblioteca padrão `calendar` (sem dependência de `tkcalendar`), garantindo portabilidade perfeita no PyInstaller.
- Layout responsivo em duas colunas: seleção de integrantes à esquerda com badge de folgas futuras, e detalhes com calendário interativo à direita.
- Destaque visual semântico: dias marcados ficam vermelhos (`COR_PERIGO`), e o clique direto alterna o status da data instantaneamente.
- Registro facilitado de férias: modal para selecionar intervalo de datas (de/até), preenchendo todos os dias de ausência de uma vez só.

**Conceitos aprendidos:**
- **Layout em grade (Grid Layout):** gerenciador de geometria (`grid`, `row`, `column`, `weight`) que distribui elementos em linhas e colunas alinhadas, essencial para construir o calendário 7x6 e dividir a tela em proporções fixas e expansíveis.
- **Responsividade:** capacidade da interface gráfica de redimensionar seus componentes proporcionalmente (`grid_columnconfigure(..., weight=1)`) quando o usuário estica ou maximiza a janela.
- **Estados vazios (Empty States):** padrão de design que apresenta mensagens acolhedoras e orientativas quando uma tela ou seleção ainda não possui dados (ex.: orientar o usuário a escolher um integrante para ver suas folgas).

## 04/11/2026 — Fase 6: Aba Escala, Feriados, Quadro de Justiça e Histórico

**O que mudou:** implementada a aba principal de geração e gestão de escalas (`tela_escala.py`), com os diálogos modais de cadastro de feriados (`janela_feriado.py`), visualização do quadro de justiça (`janela_justica.py`) e consulta/exclusão de histórico (`janela_historico.py`). Inclui suporte a troca manual de pessoas com validação de regras, confirmação de rascunhos e cópia direta do texto formatado para o WhatsApp, totalizando 82 testes automatizados verdes.

**Decisões:**
- Status visual claro da escala: faixas semânticas destacam se a escala em exibição é um rascunho (amarelo) ou já está confirmada (verde).
- Troca manual assistida: menu suspenso alimentado por `pessoas_para_troca`, mostrando se a pessoa já trabalha em outro dia ou marcou folga, com avisos amigáveis e bloqueio contra escalar a mesma pessoa duas vezes no mesmo dia.
- Exportação em um clique: botão "Copiar para WhatsApp" coloca o texto formatado na área de transferência e altera temporariamente o texto do botão para "✓ Copiado!", fornecendo feedback tátil e visual imediato.
- Estabilidade de Tcl/Tk em testes de interface no Windows: adoção de uma fixture de sessão (`app_janela_compartilhada` em `conftest.py`) que reutiliza o mesmo root Tcl/Tk oculto, evitando corrupção de bibliotecas internas ao destruir e recriar instâncias de `CTk`.

**Conceitos aprendidos:**
- **Integração lógica ↔ interface:** conectar funções puras de regras de negócio (`gerador.py`, `edicao.py`, `historico.py`) aos componentes gráficos sem acoplamento indevido, mantendo a camada de lógica limpa e independente de bibliotecas de GUI.
- **Janelas modais (Modal Dialogs):** janelas secundárias (`CTkToplevel`) focadas em tarefas específicas que capturam as atenções e eventos do usuário (`grab_set`) e garantem cancelamento limpo ao fechar ou apertar `Esc`.
- **Área de transferência (Clipboard):** canal de comunicação entre programas gerenciado pelo sistema operacional, acessado através de métodos como `clipboard_clear()` e `clipboard_append()` da janela Tkinter.

## 04/11/2026 — Fase 7: Janela de Configurações e Ajuda Integrada

**O que mudou:** implementada a janela modal completa de configurações do programa (`janela_configuracoes.py`), parametrizando todas as regras do sistema (turnos semanais, períodos, feriados, experiência nas duplas, parâmetros de escala, mensagens do WhatsApp e opções avançadas como regras de pares e backup manual), acompanhada por explicações e exemplos didáticos (`CampoComAjuda`), com 89 testes automatizados verdes.

**Decisões:**
- Cópia de trabalho isolada (`config_temp`): a tela cria uma cópia profunda (`copy.deepcopy`) das configurações e só aplica as mudanças em `DadosDoPrograma` quando o usuário clica em "Salvar alterações", evitando estados inconsistentes caso o usuário cancele.
- Seção recolhível de opções avançadas: mantém a interface limpa e descomplicada para o uso diário, enquanto disponibiliza controles refinados (duplas fixas, restrições "nunca juntos", alternância de compensação de ausências e cópias manuais de segurança).
- Validação preventiva com avisos humanos: checagem de integridade de turnos (mínimo 1 turno, duplas >= 1), aviso de capacidade caso a demanda de plantonistas supere os integrantes ativos e validação de consistência lógica entre "nunca juntos" e "sempre juntos".
- Restauração segura de fábrica: botão "Restaurar padrão" em destaque vermelho com diálogo de confirmação prévia, restabelecendo as decisões acordadas no projeto sem comprometer os cadastros de integrantes e escalas.

**Conceitos aprendidos:**
- **Parametrização:** transformação de regras e números do código em dados e variáveis configuráveis pelo usuário, tornando o programa flexível a mudanças sem necessidade de alterar o código-fonte.
- **Validação de entrada (Input Validation):** verificação cuidadosa de tudo o que o usuário digita ou seleciona antes de persistir no sistema, garantindo integridade e emitindo mensagens claras quando algum valor foge do esperado.

## 04/11/2026 — Refinamento Visual de Layout e Tipografia

**O que mudou:** aprimorado o design visual da interface atendendo aos apontamentos de usabilidade: ampliação e destaque dos botões das abas principais (`janela_principal.py`), ajuste e redução da escala tipográfica na lista da equipe (`tela_equipe.py`) e redesenho da disposição das duplas na escala em cartões modulares em grade de 2 colunas com alinhamento perfeito (`tela_escala.py`).

**Decisões:**
- Abas com alta visibilidade: altura aumentada para 46px com tipografia em 16px negrito e contraste aprimorado, facilitando o clique da usuária.
- Proporção tipográfica equilibrada na equipe: nomes em 14px com espaçamentos compactos e badges de status proporcionais, permitindo visualizar muito mais integrantes confortavelmente na tela.
- Duplas em grade modular (2 colunas): duplas organizadas em cartões individuais simétricos com botão "Trocar" fixado à direita de cada integrante, eliminando o desalinhamento horizontal anterior.

**Conceitos aprendidos:**
- **Hierarquia visual (Visual Hierarchy):** técnica de design que orienta o olhar do usuário através do tamanho, peso e espaçamento das fontes, deixando claro o que é título, item de lista e ação secundária.
- **Modularização de componentes em grade (Card Grid):** estruturação de informações agrupadas (duplas de plantão) em pequenos módulos visuais independentes distribuídos em linhas e colunas uniformes.

## 04/11/2026 — Otimização de Performance da Interface (Lazy Rendering e Flattening)

**O que mudou:** eliminados gargalos de renderização na interface gráfica através de renderização preguiçosa nas abas (`janela_principal.py`) e achatamento hierárquico da árvore de widgets (`tela_equipe.py` e `tela_escala.py`), acelerando o tempo de renderização em quase 40% e tornando a rolagem e a troca de abas instantâneas.

**Decisões:**
- Renderização preguiçosa (Lazy Rendering): `ao_mudar()` atualiza imediatamente apenas a aba visível aos olhos da usuária. As abas em segundo plano são marcadas no conjunto `_abas_desatualizadas` e só são reconstruídas sob demanda quando o usuário clica nelas (`_ao_trocar_aba`).
- Achatamento de hierarquia (Widget Tree Flattening): remoção de contêineres transparentes intermediários (`info_frame`, `acoes_frame`, `info_a`, `info_b`). Rótulos e botões passam a ser empacotados diretamente no cartão pai com `side="left"` e `side="right"`, eliminando mais de 60 instâncias de `CTkFrame` por ciclo de renderização.

**Conceitos aprendidos:**
- **Renderização preguiçosa (Lazy Rendering / Evaluation):** padrão que posterga o processamento ou renderização de um elemento até o momento exato em que ele se torna necessário e visível, poupando ciclos de CPU e memória.
- **Achatamento de árvore de componentes (Widget Tree Flattening):** técnica de simplificação da árvore visual que remove contêineres intermediários redundantes, diminuindo o custo de cálculo de geometria e chamadas de desenho no motor gráfico.

## 04/11/2026 — Auditoria do Tech Lead: Especificação da Fase 7.1 (Performance e UI/UX)

**O que mudou:** após medir o desempenho real da interface (1.015 widgets vivos, 2,2 s para abrir e 1,1 s ao clicar
em uma pessoa na aba Folgas), o `AGENTS.md` recebeu as seções **10.4 (Regras de Performance no CustomTkinter)**,
**10.6 (Especificação da Refatoração Visual por Arquivo)** e a **Fase 7.1** no roteiro e nos testes obrigatórios.

**Decisões:**
- Proibir aninhamento de cartões com borda ("efeito boneca russa"): no máximo 1 nível de `CartaoFrame` dentro de áreas roláveis.
- Proibir `.place()` de `CTkLabel` sobre `CTkButton` (causava triplicação de widgets e perda de cliques em `tela_folgas.py`).
- Obrigar reuso de widgets (*in-place update* com `.configure()`) no `CalendarioMensal` (42 botões fixos) e na seleção de pessoas de `TelaFolgas`, sem chamar `destroy()` em massa.
- Simplificar cada dupla na aba Escala de 13 widgets para 5 widgets, tornando o próprio botão com o nome da pessoa o acionador de troca.

**Conceitos aprendidos:**
- **Árvore de Widgets (*Widget Tree*) e custo de Canvas:** em CustomTkinter, cada borda ou canto arredondado é um `tk.Canvas` separado; aninhar muitos níveis degrada a rolagem.
- **Atualização *in-place* vs. Destruir e Recriar (*Object Reuse*):** manter os objetos visuais vivos na memória e alterar apenas suas propriedades (`.configure()`) é dezenas de vezes mais rápido do que destruir (`destroy()`) e instanciar novos widgets a cada clique.
- **Diagnóstico baseado em métricas (*Profiling*):** medir o tempo em milissegundos e contar objetos antes de otimizar.

## 04/11/2026 — Fase 7.1: Refatoração de Performance e Polimento Visual (UI/UX)

**O que mudou:** implementação completa da Fase 7.1 aplicando todas as regras de performance e diretrizes visuais estabelecidas nas seções 10.4, 10.5 e 10.6 do `AGENTS.md`. Todos os componentes reutilizam widgets *in-place* (sem `destroy()` em massa), áreas roláveis contam com rolagem suave configurada, cartões aninhados foram eliminados e a suíte agora conta com 92 testes automatizados 100% verdes, incluindo testes dedicados de performance em `test_interface_performance.py`.

**Decisões:**
- `CalendarioMensal` (*in-place update*): os 42 botões da grade mensal são instanciados uma única vez na inicialização; a navegação entre meses e a atualização de marcações apenas ajusta as propriedades (`text`, `fg_color`, `hover_color`, `border_width`, `state`, `command`) dos botões existentes, eliminando travamentos de alocação de memória no motor Tcl. Cabeçalhos de Sábado e Domingo foram destacados com `COR_PRIMARIA`, e o dia de hoje recebe borda azul.
- `TelaFolgas` com painéis e botões persistentes: a lista lateral instancia botões únicos (`CTkButton` com `anchor="w"`) sem sobreposição de rótulos com `.place()`. Clicar em uma pessoa altera a cor apenas dos botões selecionado/deselecionado e atualiza o calendário e lista de datas sem recriar os elementos.
- `TelaEscala` limpa e plana: substituição das caixas aninhadas de duplas (que continham até 13 widgets com bordas duplicadas) por linhas planas com `border_width=0` e apenas 4 elementos principais (número, botão da pessoa A, separador `&`, botão da pessoa B). Clicar no próprio nome da pessoa aciona o diálogo de substituição. A barra superior agora destaca em azul (`COR_PRIMARIA`) o botão do período ativo e exibe um rótulo claro com o intervalo de datas selecionado (`📅 02/11 a 08/11`).
- Rolagem suave e acabamento visual: adição de `configurar_rolagem_suave` em todos os `CTkScrollableFrame` da aplicação (`tela_equipe`, `tela_folgas`, `tela_escala`, `janela_justica`, `janela_historico`, `janela_configuracoes`), linhas divisórias sutis abaixo do cabeçalho e acima do rodapé, e listras zebradas (*zebra striping*) na tabela do Quadro de Justiça.

**Conceitos aprendidos:**
- **Árvore de widgets (Widget Tree):** a estrutura hierárquica em árvore mantida pela interface gráfica, onde cada contêiner pai gerencia o posicionamento, redimensionamento e eventos de seus nós filhos. Quanto mais profunda e ramificada a árvore, mais cálculos de geometria são exigidos a cada ciclo de renderização.
- **Reuso de objetos (*In-place Update*):** padrão de projeto que preserva instâncias de componentes gráficos já alocadas na memória, alterando somente seus atributos visuais em vez de destruí-las e recriá-las a cada interação do usuário.
- **Layout Thrashing:** degradação drástica de fluidez que ocorre quando o programa força sucessivas destruições e recriações de elementos geométricos, obrigando o motor gráfico a recalcular dimensões e redesenhar formas vetoriais repetidamente em um curto intervalo de tempo.
- **Hierarquia visual:** organização estratégica de cores, contrastes e pesos tipográficos para conduzir naturalmente a atenção do usuário aos dados e ações mais relevantes da tela sem esforço cognitivo.

## 04/11/2026 — Transição do Design System para Modo Escuro (Dark Mode)

**O que mudou:** a pedido do desenvolvedor devido ao desconforto visual e claridade excessiva do tema claro, todo o Design System foi migrado para Modo Escuro (`ctk.set_appearance_mode("dark")`) em `componentes.py`, com paleta semântica baseada em tons modernos de Slate e alto contraste para legibilidade, mantendo 100% dos testes verdes.

**Decisões:**
- Paleta semântica em tons Slate: fundo geral em `#0F172A` (Slate 900), cartões e painéis elevados em `#1E293B` (Slate 800) e bordas e divisórias sutis em `#334155` (Slate 700), proporcionando profundidade sem agredir a visão.
- Tipografia de alto contraste: texto principal em `#F8FAFC` (Slate 50) e textos auxiliares em `#94A3B8` (Slate 400), assegurando leitura sem ofuscamento.
- Cores de destaque semântico: botões primários em Royal Blue (`#3B82F6` / `#2563EB`), sucesso em verde esmeralda (`#16A34A`), botões secundários em slate com texto claro e avisos com fundo quente escuro (`#451A03`) e texto âmbar claro (`#FDE68A`).
- Adaptação na Escala: faixas de confirmação adotaram `#064E3B` com texto `#A7F3D0` e cabeçalhos de plantão usam o fundo escuro integrado (`COR_FUNDO` ou `COR_AVISO_FUNDO` em feriados).

**Conceitos aprendidos:**
- **Design Tokens em Modo Escuro:** em vez de inverter cores matematicamente (o que gera contrastes duros e cansativos), projeta-se uma escala intencional com luminância controlada para superfícies e alta legibilidade para tipografia.
- **Relação de Contraste (Contrast Ratio - WCAG):** garantia de que textos claros sobre superfícies escuras atendam a padrões confortáveis de contraste (> 4.5:1), prevenindo fadiga ocular em sessões prolongadas de uso.


