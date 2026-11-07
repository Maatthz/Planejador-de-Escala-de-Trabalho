# 📋 Manual do Usuário — Planejador de Escala de Plantão

Bem-vindo(a) ao **Planejador de Escala de Plantão**! Este guia foi escrito passo a passo, em linguagem simples, para ajudar você a montar a escala de fim de semana e feriados da equipe de forma justa, rápida e pronta para colar no WhatsApp.

---

## 1. Como abrir o programa pela primeira vez

O programa é um arquivo único chamado **`PlanejadorEscala.exe`**. Você **não precisa instalar nada**.

1. Coloque o arquivo **`PlanejadorEscala.exe`** na sua pasta **Documentos** ou na **Área de Trabalho**.
2. Dê dois cliques nele para abrir.

> [!IMPORTANT]
> **Se aparecer uma tela azul do Windows dizendo "O Windows protegeu o seu computador":**
> Isso é normal na primeira vez que você abre um programa novo.
> 1. Clique no texto sublinhado **"Mais informações"**.
> 2. Clique no botão **"Executar assim mesmo"**.

> [!TIP]
> **Salvamento automático:** você nunca precisa procurar um botão "Salvar" ao cadastrar pessoas ou marcar folgas. Tudo o que você faz é salvo automaticamente no computador!

---

## 2. Passo a passo do uso semanal

Na parte superior do programa, existem **3 abas grandes**:
- **👥 Equipe** — onde você cadastra as pessoas.
- **📅 Folgas** — onde você marca quem não pode trabalhar em determinados dias ou está de férias.
- **📋 Escala** — onde você gera a escala, faz trocas e copia para o WhatsApp.

---

### Passo 1: Cadastrar e organizar a equipe (Aba `👥 Equipe`)

Você só precisa cadastrar a equipe inteira na primeira vez. Depois, só mexe aqui quando alguém entrar ou sair.

- **Adicionar uma pessoa:**
  1. Clique no botão azul **`+ Adicionar pessoa`** (canto superior direito).
  2. Digite o nome da pessoa.
  3. Se a pessoa for **experiente** no plantão, marque a caixinha **"Pessoa experiente no plantão (★)"**. Ela ganhará uma estrela dourada (**★**) ao lado do nome, e o programa tentará colocar pelo menos uma pessoa experiente em cada dupla.
  4. Clique em **`Adicionar`**.
- **Mudar nome ou experiência:** clique em **`Editar`** no cartão da pessoa.
- **Afastar temporariamente (`Desativar` / `Reativar`):**
  - Se alguém não puder ser escalado por um longo período, clique em **`Desativar`**. O histórico dela continua guardado, mas ela não entra nas próximas escalas.
  - Quando ela voltar, clique em **`Reativar`**.

> [!NOTE]
> **E quem entra novo ou volta de férias fica "devendo" plantão?**
> **Não!** Por padrão, quem entra na equipe ou volta de férias entra **empatado com quem menos trabalhou**. O objetivo do programa é distribuir o descanso de forma justa, e não punir quem estava de férias escalando a pessoa todo fim de semana seguido.

---

### Passo 2: Marcar folgas e férias (Aba `📅 Folgas`)

Antes de gerar a escala da semana, marque quem pediu dispensa ou está de férias:

1. Na lista da **esquerda**, clique no **nome da pessoa**.
2. No **calendário à direita**:
   - Use as setas **◀** e **▶** para mudar de mês.
   - **Clique em cima do dia** em que a pessoa não poderá trabalhar: o dia ficará **vermelho** (folga marcada).
   - Para desmarcar, basta clicar no mesmo dia novamente.
3. **Para marcar vários dias seguidos (Férias):**
   - Clique no botão azul **`Marcar período (férias)`** acima do calendário.
   - Digite a data inicial e a data final (no formato `dd/mm/aaaa`, por exemplo `01/12/2026` a `15/12/2026`) e clique em **`Marcar ausências`**.

---

### Passo 3: Gerar, ajustar e enviar a escala (Aba `📋 Escala`)

1. **Escolha o período** na barra superior:
   - **`Esta semana`**, **`Próxima semana`** ou **`Escolher data…`** (para digitar outra data).
   - Em **Semanas**, escolha quantas semanas quer montar de uma vez (`1` para semanal, `2` para quinzenal).
2. **Tem feriado na semana?**
   - Clique em **`+ Feriado`**, digite a data (ex.: `20/11/2026`), o nome (ex.: `Consciência Negra`) e quantas duplas trabalharão em cada período.
   - Se o feriado cair num sábado ou domingo, a configuração do feriado vale para aquele dia.
3. **Clique no botão azul `Gerar escala`:**
   - O programa monta os plantões escolhendo quem trabalhou menos, respeitando as folgas, variando os parceiros de dupla e evitando colocar a mesma pessoa em semanas seguidas.
4. **Rascunho (faixa amarela):**
   - Enquanto aparecer a faixa amarela *"⚠️ Rascunho — esta escala ainda não está valendo"*, você pode clicar em **`Gerar escala`** quantas vezes quiser ou fazer trocas à vontade sem alterar a contagem oficial de plantões.
5. **Fazer uma troca manual:**
   - Quer trocar alguém de dupla ou de plantão? **Clique diretamente em cima do nome da pessoa** no cartão do plantão.
   - Uma janela mostrará todas as outras pessoas disponíveis e avisará ao lado do nome se alguém estiver de folga ou já trabalhar em outro dia da semana. Clique em **`Escolher`** para substituir.
6. **Confirmar a escala (`✅ Confirmar escala`):**
   - Quando a escala estiver pronta e aprovada, clique no botão verde **`✅ Confirmar escala`** (canto inferior direito).
   - A faixa ficará verde (*"✅ Escala confirmada e salva no histórico"*) e os plantões passarão a contar na fila de justiça.
7. **Enviar no WhatsApp (`📋 Copiar para WhatsApp`):**
   - Clique em **`📋 Copiar para WhatsApp`**. O botão mudará para **`✅ Copiado!`**.
   - Abra o WhatsApp da equipe, clique na caixa de mensagem e cole (**Botão direito → Colar** ou **`Ctrl + V`**).

---

## 3. Consultas e trocas de última hora

Na barra inferior da aba **`📋 Escala`**, há dois botões de consulta:

- **`📊 Quadro de justiça`:** mostra a fila completa da equipe em ordem de prioridade (quem aparece no topo é o próximo a ser escalado), exibindo quantos plantões cada pessoa fez, quantos feriados trabalhou e a data do último plantão.
- **`📜 Escalas anteriores`:** lista todas as escalas já confirmadas.
  - **Precisou trocar alguém de última hora depois que a escala já estava confirmada?** Clique em **`📜 Escalas anteriores`** → **`Ver / Editar`** na escala desejada, clique no nome de quem saiu e escolha quem entrou no lugar. O programa **recalcula a justiça sozinho** na mesma hora!

---

## 4. Configurações do programa (`⚙️ Configurações`)

O programa já vem configurado para funcionar imediatamente (4 duplas no sábado de manhã e 4 duplas no domingo à tarde). Se a rotina da equipe mudar, clique em **`⚙️ Configurações`** no canto superior direito:

- **Turnos:** adicionar, alterar ou remover os dias e períodos de plantão da semana.
- **Feriados:** ligar/desligar plantões em feriados e definir o padrão de duplas.
- **Duplas:** escolher se ter 1 experiente (★) por dupla é uma *Preferência*, *Obrigatória* ou se deve *Ignorar*.
- **Mensagem:** personalizar o título e adicionar uma frase final fixa para o WhatsApp (ex.: *"Trocas: avisar a coordenação"*).
- **Avançadas:**
  - **Nunca juntos:** cadastrar duas pessoas que não devem formar a mesma dupla.
  - **Duplas fixas:** cadastrar duas pessoas que sempre trabalham juntas quando ambas estão disponíveis.
  - **Cópia de segurança (`Salvar cópia` / `Restaurar`):** permite salvar todos os dados em um pendrive ou pasta para transferir para outro computador.
  - **`Restaurar padrão`:** volta todas as opções de configuração para o padrão original (sem apagar as pessoas nem o histórico).

---

## 5. Perguntas frequentes

- **E se o computador desligar de repente ou faltar luz?**
  O programa salva os dados de forma protegida e guarda automaticamente as **últimas 10 cópias de segurança**. Se algum arquivo for afetado por queda de energia, ele recupera a cópia anterior sozinho e avisa você ao abrir.
- **Como recebo melhorias e correções do programa?**
  Sempre que você abre o `PlanejadorEscala.exe` conectado à internet, ele verifica silenciosamente se existe uma versão nova. Quando houver, aparecerá uma pergunta simples: *"Nova versão disponível! Deseja atualizar agora?"*. Basta clicar em **Sim, continuar** — seus dados e históricos permanecem intactos.
