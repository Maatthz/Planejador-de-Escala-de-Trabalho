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

## 04/11/2026 — Transição do Design System para Modo Escuro Grafite (Charcoal)

**O que mudou:** a pedido do desenvolvedor para eliminar tonalidades azuladas e adotar uma estética neutra e sóbria, a paleta semântica do modo escuro foi refinada em `componentes.py` para tons de preto fosco e grafite profundo (`#121214` e `#1E1E22`), mantendo 100% dos testes automatizados verdes.

**Decisões:**
- Paleta neutra grafite/charcoal: fundo geral em `#121214` (grafite profundo quase preto), cartões e painéis em `#1E1E22` (superfície fosca), divisórias e bordas em `#2E2E34`, e botões secundários em `#2A2A30` com hover em `#3A3A42`.
- Tipografia neutra e nítida: texto principal em `#F4F4F5` e textos secundários em `#A1A1AA`, garantindo legibilidade perfeita sem tons azulados.
- Realce de ações preservado: botões primários em azul vivo (`#3B82F6`), confirmação em verde (`#16A34A`), ações destrutivas em vermelho (`#DC2626`) e avisos em âmbar neutro escuro (`#3D2406`).

**Conceitos aprendidos:**
- **Saturação vs. Neutralidade Cromática:** paletas com saturação azulada (*slate/navy*) geram sensação de frieza, enquanto tons neutros de cinza grafite (*zinc/charcoal*) proporcionam uma estética minimalista e moderna similar a ferramentas de desenvolvimento (VS Code, terminal, interfaces profissionais).
- **Consistência de Tokens de Interface:** ao centralizar cores em variáveis semânticas (`COR_FUNDO`, `COR_CARTAO`, `COR_BORDA`), a alteração de tema para toda a aplicação ocorre em um único ponto, sem tocar na lógica nem quebrar componentes.

## 04/11/2026 — Destaque em Amarelo Ouro para Integrantes Experientes (★)

**O que mudou:** a pedido do desenvolvedor, a estrela indicadora de integrantes experientes passou a ser exibida em amarelo ouro vibrante (`COR_ESTRELA = "#FACC15"`), com destaque visual na aba Equipe (`tela_equipe.py`), na aba Escala (`tela_escala.py`), no diálogo do Quadro de Justiça (`janela_justica.py`) e na caixa de seleção dos modais de cadastro e edição.

**Decisões:**
- Destaque cromático independente: no Tkinter, textos dentro de um mesmo rótulo compartilham uma única cor; para que a estrela fosse amarela sem forçar o nome da pessoa a ficar amarelo, ela passou a ser renderizada com `text_color=COR_ESTRELA`, respeitando o teto de 4 widgets internos por cartão na equipe.
- Checkbox temático nos formulários: a opção "Pessoa experiente no plantão (★)" passa a preencher o fundo da caixa em amarelo ouro ao ser ativada, oferecendo feedback visual claro e imediato.
- Clique integrado nas duplas: na grade de escala, clicar na estrela dourada também aciona o diálogo de substituição do membro da dupla.

**Conceitos aprendidos:**
- **Afetância Visual e Acentuação de Estado (Visual Affordance):** uso de uma cor quente (amarelo ouro) para um atributo especial (experiência), criando contraste instantâneo sobre superfícies grafite.
- **Composição de Widgets vs. Monocromia:** técnica de divisão de elementos visuais para viabilizar estilizações policromáticas em bibliotecas de interface desktop com controles de texto monocromáticos.





## 04/11/2026 — Ajuste fino de Performance (Memoização de Estado Visual e Lazy Init real)

**O que mudou:** corrigidos os 3 detalhes finos apontados no code review da Fase 7.1 em `componentes.py`,
`janela_principal.py`, `tela_equipe.py`, `tela_folgas.py` e `tela_escala.py`.

**Decisões:**
- **`inicializar_agora=False`** nas abas `Folgas` e `Escala` ao abrir a `JanelaPrincipal`: evita construir as 3 abas no arranque e depois destruir/reconstruir no primeiro clique.
- **Cache de estado visual (*memoização*)** nos 42 botões do `CalendarioMensal` (`_estado_botoes`), nos cartões de `TelaEquipe` (`_linhas_equipe`) e na lista de datas de `TelaFolgas` (`_datas_renderizadas`): `.configure()` só é chamado nos widgets cujo valor realmente mudou.
- Em `TelaFolgas._selecionar_pessoa`, apenas os 2 botões afetados (o anterior e o novo selecionado) são reconfigurados, em vez de percorrer e redesenhar os 28 botões.
- Passo de rolagem ajustado para `yscrollincrement=24`.

**Conceitos aprendidos:**
- **Memoização / Dirty Checking na UI:** guardar o último estado desenhado de um componente e só chamar a função de redesenho (`.configure()`) quando o estado novo for diferente do anterior.
- **Custo oculto de `.configure()` no CustomTkinter:** mesmo sem `destroy()`, chamar `.configure(fg_color=...)` sem necessidade força o `tk.Canvas` interno a redesenhar formas vetoriais.

## 04/11/2026 — Eliminação do Gargalo de Troca de Abas (`tkraise` + Reuso In-Place na `TelaEscala` + `RotuloSimples`)

**O que mudou:** eliminada a lentidão e o efeito cascata ao alternar entre `👥 Equipe`, `📅 Folgas` e `📋 Escala` por meio de quatro otimizações estruturais em `componentes.py`, `janela_principal.py`, `tela_escala.py`, `tela_equipe.py` e `tela_folgas.py`:
1. **`AbasRapidas` (`componentes.py`):** subclasse de `CTkTabview` que mantém as abas mapeadas na mesma célula da grade com `pack_propagate(False)` / `grid_propagate(False)` e alterna entre elas com `.tkraise()`, eliminando o `grid_forget()` + `grid()` que o `CTkTabview` padrão executava a cada clique.
2. **Reuso in-place na `TelaEscala` (`tela_escala.py`):** `_atualizar_cartoes_plantoes` e `_atualizar_faixa_status` deixaram de destruir todos os ~300 widgets a cada atualização (`617 ms`) e passaram a reutilizar o esqueleto de cartões, botões e estrelas in-place (`0,1 ms`).
3. **`RotuloSimples` (`componentes.py`):** rótulo nativo leve (`tk.Label` = 1 único `HWND`, sem `CTkCanvas` intermediário) com mesma tipografia e escala DPI do CustomTkinter para textos internos repetidos nos cartões de `TelaEquipe` e `TelaEscala`, eliminando mais de 120 instâncias de `CTkCanvas` (~250 `HWND`s do Windows).
4. **Pré-aquecimento assíncrono (`janela_principal.py`):** após abrir a janela principal, `_pre_aquecer_folgas` e `_pre_aquecer_escala` constroem e mapeiam os widgets das abas secundárias em segundo plano, tornando até o primeiro clique na aba `📋 Escala` instantâneo (`~65 ms`, antes `657–880 ms`).

**Conceitos aprendidos:**
- **Z-Order Stacking (`tkraise`) vs. Unmapping (`grid_forget`):** desmapear e remapear centenas de janelas filhas (`HWND`s) no Windows força o gerenciador de geometria a recalcular posições de cima para baixo; manter os containers empilhados e apenas alterar a ordem Z (`tkraise`) troca a visualização sem recalcular layout.
- **Isolamento de Propagação de Geometria (`pack_propagate(False)` / `grid_propagate(False)`):** impede que alterações internas em uma aba façam o Tkinter recalcular o tamanho da janela inteira e das abas vizinhas.
- **Peso de Widgets Compostos vs. Nativos:** cada `CTkLabel` cria 3 `HWND`s no Windows (`Frame` + `Canvas` + `Label`); em listas grandes com fundo sólido, usar um `tk.Label` nativo reduz em 3× o número de janelas que o sistema operacional precisa pintar.

## 06/11/2026 — Fase 8: Lançador `iniciar.py`, Logging Global e Empacotamento `.exe`

**O que mudou:** criado o lançador [`iniciar.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/iniciar.py) na raiz do projeto, configurado o sistema de registro de logs rotativo (`registro.log`) e captura global de exceções de callbacks em [`src/escala/main.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/main.py), adicionado teste automatizado em [`tests/test_versao.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/tests/test_versao.py) e gerado o executável único `dist/PlanejadorEscala.exe` (~11,1 MB) com PyInstaller.

**Decisões:**
- **`iniciar.py` na raiz:** como os módulos internos usam imports absolutos (`from src.escala...`), o script de entrada do PyInstaller precisa ficar na pasta pai de `src/` para que o pacote `src.escala` seja resolvido sem conflito de caminhos.
- **Captura de erros em modo `--windowed` (`report_callback_exception`):** como o `.exe` roda sem janela de terminal preta (`--windowed`), erros inesperados em cliques de botão não apareceriam em lugar nenhum. Redirecionamos `app.report_callback_exception` para gravar o *traceback* completo em `%APPDATA%/PlanejadorEscala/registro.log` (`RotatingFileHandler` de 1 MB com até 3 arquivos) e exibir uma mensagem amigável ao usuário.
- **`--collect-data customtkinter`:** inclui os arquivos de temas JSON e fontes do CustomTkinter dentro do `.exe`.

**Conceitos aprendidos:**
- **Empacotamento (*Freezing* com PyInstaller):** transforma o interpretador Python, o bytecode dos módulos `.py`, as DLLs nativas (como Tcl/Tk) e os arquivos de dados das bibliotecas em um único executável `.exe` autossuficiente que descompacta seus recursos em uma pasta temporária (`_MEIPASS`) ao abrir.
- **Rotação de Logs (`RotatingFileHandler`):** evita que o arquivo de log cresça infinitamente no computador do usuário; ao atingir 1 MB, ele é renomeado para `.log.1` (mantendo até 3 históricos) e um novo `registro.log` é iniciado.

## 06/11/2026 — Fase 9: Atualizador Automático (`atualizador.py`) com SHA-256 e Testes Offline

**O que mudou:** implementado o módulo [`src/escala/atualizador.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/atualizador.py), integrado à inicialização da [`JanelaPrincipal`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/interface/janela_principal.py) e validado por 10 testes em [`tests/test_atualizador.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/tests/test_atualizador.py).

**Decisões:**
- **Comparação semântica numérica (`comparar_versoes`):** converte `"v1.10.0"` em `(1, 10, 0)` antes de comparar, evitando o erro clássico de comparação alfabética onde `"1.10.0" < "1.9.9"` porque `'1' < '9'`.
- **Falha silenciosa na consulta (`buscar_atualizacao`):** se o usuário estiver sem internet, se o repositório ainda não estiver configurado ou se o GitHub estiver fora do ar, retorna `None` sem incomodar o usuário com janelas de erro.
- **Segurança por hash criptográfico (`calcular_sha256` / `baixar_e_verificar`):** exige links `https://`, calcula o SHA-256 do `.exe` baixado em blocos de 64 KB e compara com o arquivo `.sha256` da Release. Se divergir, apaga o arquivo imediatamente e levanta `ErroAtualizacao`.
- **Auto-substituição no Windows (`instalar_e_reiniciar`):** como o Windows bloqueia sobrescrever um `.exe` que está em execução, o programa gera um script temporário `atualizar_escala.bat` que aguarda 2 segundos após o encerramento (`sys.exit(0)`), move o novo `.exe` para o lugar do antigo, reabre o programa e apaga o próprio `.bat` (`del "%~f0"`).
- **Thread em segundo plano + `after(0, ...)`:** a consulta HTTP roda em uma `threading.Thread(..., daemon=True)` para não travar a abertura da janela, e devolve o aviso para a thread principal do Tkinter via `self.after(0, ...)`.

**Conceitos aprendidos:**
- **Versionamento Semântico (*SemVer*):** formato `MAIOR.MENOR.CORREÇÃO` comparado parte a parte como inteiros.
- **Hash Criptográfico (SHA-256):** impressão digital única de 256 bits (64 caracteres hexadecimais) de um arquivo; qualquer byte corrompido ou adulterado muda completamente o hash.
- **Threads Daemon e Thread Safety em GUI:** operações de rede nunca devem rodar na thread principal da interface (para não congelar a janela), e threads secundárias nunca devem criar widgets diretamente — usam `janela.after(0, callback)` para enfileirar a ação na thread principal.
- **Mocking / Monkeypatch em Testes:** substituição temporária de `requests.get` e `subprocess.Popen` durante os testes para simular internet, erros de rede e permissões de disco de forma instantânea e determinística.

## 06/11/2026 — Fase 10: GitHub Actions (`testes.yml` e `release.yml`) e Configuração do Repositório

**O que mudou:** configurado `REPOSITORIO_GITHUB = "Maatthz/Planejador-de-Escala-de-Trabalho"` em [`src/escala/versao.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/versao.py), adicionado `AGENTS.md` ao [`.gitignore`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/.gitignore) (removido do rastreamento remoto com `git rm --cached` mas preservado no disco local), conectado o controle remoto `origin` e criados os workflows [`.github/workflows/testes.yml`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/.github/workflows/testes.yml) e [`.github/workflows/release.yml`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/.github/workflows/release.yml).

**Decisões:**
- **Integração Contínua (`testes.yml`):** a cada `push` ou `pull_request` na branch `main`, uma máquina Windows na nuvem do GitHub instala o Python 3.12, as dependências e executa `pytest`.
- **Entrega Contínua (`release.yml`):** disparado automaticamente apenas quando uma *tag* começando com `v` (ex.: `v0.1.0`) é enviada ao GitHub. Roda os testes, valida que a tag coincide exatamente com `v` + `VERSAO` de `versao.py` (evitando publicar versão errada por engano), empacota o `PlanejadorEscala.exe`, gera o `PlanejadorEscala.exe.sha256` em minúsculas e cria a GitHub Release anexando os dois arquivos.
- **`git rm --cached AGENTS.md`:** remove o arquivo do repositório Git (para não aparecer no GitHub) sem apagá-lo da pasta local do projeto.

**Conceitos aprendidos:**
- **CI/CD (Integração Contínua e Entrega Contínua):** automação em servidores de nuvem que testa cada alteração (*CI*) e compila/publica o executável final pronto para o usuário quando uma versão é fechada (*CD*).
- **Git Index vs. Working Tree (`git rm --cached`):** diferença entre apagar um arquivo do disco (`rm`) e apenas parar de rastreá-lo no histórico do Git mantendo a cópia local intacta.

## 06/11/2026 — Fase 11: Manual do Usuário (`MANUAL_DO_USUARIO.md`), Guia do Desenvolvedor (`README.md`) e Fechamento

**O que mudou:** elaborado o guia completo para o usuário final leigo em [`docs/MANUAL_DO_USUARIO.md`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/docs/MANUAL_DO_USUARIO.md) e atualizado o [`README.md`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/README.md) na raiz com instruções de execução, testes, empacotamento `.exe`, publicação de Releases via tags e mapa da arquitetura.

**Decisões:**
- **Linguagem orientada à tarefa no Manual do Usuário:** em vez de descrever código ou estruturas de dados, o manual acompanha o fluxo mental semanal de quem monta a escala (1. Abrir o `.exe` e passar pelo aviso do Windows SmartScreen → 2. Cadastrar equipe e estrelas `★` → 3. Marcar folgas e férias → 4. Gerar rascunho, fazer trocas clicando no nome, confirmar e colar no WhatsApp).
- **Separação entre documentação de usuário e de desenvolvedor:** o `README.md` atende o desenvolvedor no GitHub (comandos PowerShell, PyInstaller e fluxo de tags do GitHub Actions), enquanto `docs/MANUAL_DO_USUARIO.md` fala diretamente com a pessoa leiga que utiliza o programa.

**Conceitos aprendidos:**
- **Documentação Orientada ao Usuário vs. Documentação Técnica:** adaptar vocabulário, exemplos e nível de abstração ao público-alvo faz parte da Engenharia de Software e da Experiência do Usuário (*UX Writing*).
- **Fluxo de Release Baseado em Tags (*Tag-based Release Workflow*):** ciclo completo de manutenção de software desktop em produção (alterar `VERSAO` → commit → `git tag vX.Y.Z` → build e distribuição automática).

## 07/11/2026 — Manutenção pós-entrega (`v0.1.1` a `v0.1.3`): Correções de Diálogo, Bootloader do PyInstaller 6 (`_PYI_APPLICATION_HOME_DIR` / `PYINSTALLER_RESET_ENVIRONMENT`) e UX de Atualização

**O que mudou:**
1. Corrigidas as 3 chamadas de `perguntar_sim_nao` em [`src/escala/interface/janela_configuracoes.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/interface/janela_configuracoes.py) (adicionado teste de regressão em [`tests/test_interface_configuracoes.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/tests/test_interface_configuracoes.py)).
2. Adicionado o parâmetro opcional `variante_confirmar: str = "perigo"` em `perguntar_sim_nao` ([`src/escala/interface/componentes.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/interface/componentes.py)) e usado `variante_confirmar="sucesso"` no convite de atualização em [`src/escala/interface/janela_principal.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/interface/janela_principal.py) para que o botão `"Sim, continuar"` fique verde nas ações positivas.
3. Criada `_ambiente_limpo_para_reinicio()` e atualizado `instalar_e_reiniciar` em [`src/escala/atualizador.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/atualizador.py) para remover variáveis internas herdadas tanto do PyInstaller antigo (`_MEIPASS`, `_MEIPASS2`) quanto do **PyInstaller 6** (`_PYI_APPLICATION_HOME_DIR`, `_PYI_ARCHIVE_FILE`, `_PYI_PARENT_PROCESS_LEVEL`, `_PYI_SPLASH_IPC`), além de definir `PYINSTALLER_RESET_ENVIRONMENT=1` e tentar `move /y` em laço antes de reabrir o novo `.exe`.

**Decisões:**
- **Por que ocorria `Failed to load Python DLL ...\_MEIxxxxxx\python312.dll` ao atualizar:** executáveis `--onefile` do PyInstaller 6 extraem seus arquivos em uma pasta temporária `_MEIxxxxxx` e definem variáveis de ambiente internas com prefixo `_PYI_` (`_PYI_APPLICATION_HOME_DIR`, `_PYI_PARENT_PROCESS_LEVEL`, `_PYI_ARCHIVE_FILE`) antes de criar o processo filho. Quando o programa antigo iniciava o script `.bat`, este herdava `_PYI_APPLICATION_HOME_DIR` apontando para a pasta temporária do processo antigo (que já havia sido apagada ao fechar). Ao iniciar o novo `.exe`, o *bootloader* via `_PYI_PARENT_PROCESS_LEVEL` e `_PYI_APPLICATION_HOME_DIR` preenchidos, achava que já tinha extraído suas DLLs e tentava carregar `python312.dll` da pasta antiga inexistente. Filtrar o prefixo `_PYI` e definir `PYINSTALLER_RESET_ENVIRONMENT=1` força o novo `.exe` a reiniciar seu *bootloader* do zero e extrair sua própria pasta `_MEI` nova.
- **Semântica de cores em diálogos de confirmação:** ações destrutivas (excluir, restaurar padrão) mantêm o botão de confirmação vermelho (`"perigo"`), enquanto ações construtivas como atualizar o programa usam verde (`"sucesso"`).

**Conceitos aprendidos:**
- **Herança de Variáveis de Ambiente em Processos Filhos (*Environment Inheritance*):** todo processo criado com `subprocess.Popen` copia as variáveis de ambiente do processo pai, a menos que um dicionário `env` explícito seja fornecido.
- **Bootloader em Dois Processos do PyInstaller 6 (`_PYI_APPLICATION_HOME_DIR` e `PYINSTALLER_RESET_ENVIRONMENT`):** arquitetura interna do modo `--onefile`, onde o processo pai descompacta a biblioteca Python em `%TEMP%\_MEIxxxxxx`, sinaliza o caminho via `_PYI_APPLICATION_HOME_DIR` ao processo filho e apaga a pasta assim que o filho termina; para um executável PyInstaller iniciar outro executável PyInstaller independente, é obrigatório ativar `PYINSTALLER_RESET_ENVIRONMENT=1` e limpar as variáveis `_PYI_*`.

## 07/11/2026 — Preenchimento e Ajuste Manual do Quadro de Justiça (`v0.1.4`)

**O que mudou:**
1. Adicionados os campos `ajuste_plantoes: int = 0`, `ajuste_feriados: int = 0` e `ultimo_plantao_manual: date | None = None` em `Pessoa` ([`src/escala/modelos.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/modelos.py)) com serialização e desserialização retrocompatível em [`src/escala/armazenamento.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/armazenamento.py).
2. Criada a função `ajustar_contadores_pessoa` e atualizados `calcular_contadores`, `registrar_plantao` e `quadro_de_justica` em [`src/escala/historico.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/historico.py) para partir do saldo manual e somar automaticamente as novas escalas confirmadas.
3. Adicionado o modo de edição em lote (**`✏️ Editar manualmente`** → **`💾 Salvar alterações`**) em [`src/escala/interface/janela_justica.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/interface/janela_justica.py) e repassado `ao_mudar` em [`src/escala/interface/tela_escala.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/src/escala/interface/tela_escala.py).
4. Adicionados testes automatizados em [`tests/test_historico.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/tests/test_historico.py) e [`tests/test_interface_escala.py`](file:///C:/Users/Matheus/Documents/GitHub/Planejador%20de%20Escala%20de%20Trabalho/tests/test_interface_escala.py).

**Decisões:**
- **Modelagem por delta/ajuste (`ajuste_plantoes = plantoes_feitos - plantoes_confirmados`):** em vez de perder o vínculo com as escalas confirmadas, quando o usuário digita que alguém tem `5` plantões na tabela, o programa calcula a diferença em relação aos plantões já confirmados no histórico e guarda em `ajuste_plantoes`. Assim, a tabela reflete exatamente o valor `5` digitado agora, e quando uma nova escala for confirmada amanhã, o total sobe automaticamente para `6` sem quebrar a fonte única de verdade.
- **Edição em tabela única (*Inline Batch Editing*):** em vez de obrigar o usuário a abrir 28 janelinhas separadas ao implantar o sistema numa equipe que já está em andamento, o botão **`✏️ Editar manualmente`** transforma as células da própria tabela em campos de digitação para preencher toda a equipe de uma só vez.

**Conceitos aprendidos:**
- **Migração de Sistema Legado / Carga Inicial (*Data Seeding / Onboarding*):** ao substituir um processo manual (planilha/papel) por um software, é essencial permitir importar ou digitar o estado acumulado até aquele momento para não zerar o histórico da equipe.
- **Persistência Retrocompatível (*Backward-Compatible Serialization*):** uso de `.get("campo", valor_padrao)` ao ler JSON para que arquivos `dados.json` salvos em versões anteriores continuem abrindo sem erro após adicionar novos atributos ao modelo.
