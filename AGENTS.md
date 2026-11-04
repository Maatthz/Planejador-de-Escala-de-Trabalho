# AGENTS.md — Planejador de Escala de Plantão

> **Para a IA programadora:** este documento é a sua instrução de sistema. Ele contém **todas** as decisões já tomadas
> em debate com o desenvolvedor. Leia-o inteiro antes de qualquer ação, siga as fases em ordem e **não reabra decisões
> já tomadas** (seção 4) sem perguntar ao desenvolvedor.

---

## 0. Como usar este documento

1. Leia as seções 1 e 2 (quem é o desenvolvedor e regras rígidas) — valem para **toda** resposta.
2. Veja a seção 16 (**Status**) para saber em que fase o projeto está.
3. Execute **somente a próxima fase** (seção 13), respeitando as assinaturas (seção 9) e os testes (seção 14).
4. Ao concluir a fase: testes passando → explicação didática → diário atualizado → seção 16 atualizada → commit.

---

## 1. Quem é o desenvolvedor (LEIA COM ATENÇÃO)

- **Iniciante em programação**, estudante de **Ciência da Computação**.
- O projeto tem **dois objetivos de igual importância**: (a) entregar um programa útil para o usuário final; (b) **ensinar** o desenvolvedor.
- Ele usa a IA no plano gratuito (poucos tokens): seja **objetivo**, sem repetir explicações já dadas — referencie o diário.
- Ele vai **ler e estudar** o seu código. Código claro vale mais que código curto.

### 1.1 Modo professor (OBRIGATÓRIO em toda alteração)
Ao final de cada tarefa, responda com:

1. **O que foi feito** — 1 a 3 frases.
2. **Por que** — qual problema resolve.
3. **Como funciona** — passo a passo, citando arquivos e funções.
4. **Conceitos envolvidos** — nomeie e explique em 1–2 frases cada conceito novo (ex.: *dataclass*, *serialização*, *thread*, *algoritmo guloso*). Conceito já explicado antes: apenas cite.
5. **Para aprender mais** (opcional) — 1 ou 2 termos para pesquisar.

E registre em `docs/DIARIO_DE_APRENDIZADO.md`: data, o que mudou, decisões, conceitos aprendidos (mesmo formato das entradas existentes).

---

## 2. Regras rígidas para a IA programadora

### 2.1 Processo
- Uma fase por vez. **Não** adiante trabalho de fases futuras.
- Dúvida sobre **regra de negócio** → pergunte ao desenvolvedor. Dúvida **técnica** pequena → escolha a opção mais simples e explique.
- Assinaturas da seção 9 são o contrato. Pode criar funções auxiliares privadas (prefixo `_`); mudar uma assinatura pública exige justificar e atualizar este arquivo.
- Antes de encerrar uma fase: `pytest` 100% verde. **Nunca** apague, pule ou enfraqueça um teste para fazê-lo passar.
- Mudou estrutura de pastas, dependências ou decisões? Atualize este arquivo na mesma tarefa.
- Commit ao fim de cada fase: `Fase N: <resumo>` (branch `main`).

### 2.2 Código
- **Python 3.12+**. Nomes de variáveis, funções, classes e comentários **em português** (sem acentos em identificadores: `funcao`, não `função`).
- Toda função/classe pública: **type hints** + **docstring curta em português**.
- Funções curtas (meta: ≤ 40 linhas). Sem "one-liners espertos", sem metaprogramação, sem herança desnecessária.
- Comentários explicam o **porquê**.
- Caminhos com `pathlib.Path`. Datas com `datetime.date`.
- **Nunca** use `locale`/`strftime("%A")` para nomes de dias (depende do idioma do Windows) — use `datas.py`.
- **Nunca** use o `random` global: use uma instância `random.Random(semente)` recebida como parâmetro (testes reproduzíveis).
- Registre erros inesperados com `logging` no arquivo `registro.log` (pasta de dados).

### 2.3 Arquitetura
- **Camada de lógica** (`modelos`, `datas`, `armazenamento`, `historico`, `gerador`, `edicao`, `exportar`, `atualizador`, `textos_ajuda`) **nunca** importa `customtkinter` nem nada de `interface/`.
- A interface **nunca** lê/escreve JSON diretamente: sempre via `armazenamento.py`.
- Erros de regra são `ErroEscala` com mensagem **já pronta para o usuário**. A interface captura exceções e mostra mensagens humanas — **nunca** um *traceback*.

### 2.4 Limites
- Dependências permitidas: as da seção 5. Qualquer outra exige justificativa + aprovação do desenvolvedor.
- Nunca salvar dados ao lado do `.exe`. Nunca apagar dados do usuário sem confirmação **e** backup.
- Nunca colocar tokens/senhas no código.

---

## 3. O produto

Programa de desktop (Windows) para **montar a escala de plantão de fim de semana** de uma equipe, em duplas.

| Item | Valor |
|---|---|
| Equipe | 28 pessoas (qualquer número) |
| Plantão | Duplas, em turnos de meio período |
| Padrão semanal | 4 duplas sábado manhã + 4 duplas domingo tarde (16 pessoas; 12 folgam) |
| Feriados | Também têm plantão |
| Geração | Semanal (às vezes quinzenal) |
| Divulgação | Texto copiado e colado no WhatsApp |
| Usuário final | **Uma única pessoa**, em um computador, **leiga em informática** |
| Distribuição | Um `.exe` único: baixa e abre, sem instalar nada |
| Atualização | Automática via GitHub Releases |

### Princípios de UX (não negociáveis)
- Funciona **sem configurar nada** (padrões = respostas do desenvolvedor).
- Botões grandes, fonte ≥ 14, português simples ("Gerar escala", nunca "Executar algoritmo").
- Toda configuração tem **explicação + exemplo** visíveis (seção 11).
- Ações destrutivas pedem confirmação. Salvamento **automático**.
- Mensagens de erro humanas: ❌ `KeyError: 12` → ✅ "Não há pessoas suficientes no sábado 07/11 (manhã): precisa de 8, há 6."

---

## 4. Decisões de negócio (fechadas em 04/11/2026)

### 4.1 Regras confirmadas
| Tema | Decisão |
|---|---|
| Funções das duplas | Todas fazem a mesma coisa |
| Duração | Meio período (turno). Turnos configuráveis |
| Restrições de dupla | Por padrão nenhuma; duplas sempre variam |
| Experiência | Preferível 1 experiente por dupla, não obrigatório |
| Feriados | Entram na escala; usuário escolhe turnos e nº de duplas |
| Período | Semanal; às vezes quinzenal |
| Divulgação | Só WhatsApp (sem Excel/PDF) |
| Pessoa nova / volta de férias | **Não compensa**: volta empatada com quem menos trabalhou (objetivo é descanso, não "dívida") |
| Editar escala já confirmada | Sim (registrar trocas de última hora); a justiça se recalcula sozinha |
| Usuários | Uma pessoa, um computador → **sem login/controle de acesso** |
| Backup manual | Não é necessário no uso normal (fica em "Opções avançadas") |
| Segurança da atualização | Verificação SHA-256 do `.exe` (invisível ao usuário) + 2FA na conta GitHub do desenvolvedor |
| Grupos de 3+ pessoas | **Fora do escopo** (YAGNI) |

### 4.2 Tudo é configurável (parametrização)
As respostas acima são o **padrão**; as alternativas ficam em **⚙️ Configurações**.

| Configuração | Padrão | Alternativas | Seção na tela |
|---|---|---|---|
| Turnos semanais | Sáb manhã 4 + Dom tarde 4 | Qualquer dia/período/nº de duplas | Turnos |
| Nomes dos períodos | manhã, tarde, noite, dia inteiro | Editar/adicionar | Turnos |
| Plantão em feriados | Ligado | Desligado | Feriados |
| Padrão de feriado | `{"manhã": 4}` | Qualquer período/nº | Feriados |
| Experiência na dupla | Preferência | Obrigatória / Ignorar | Duplas |
| Semanas por geração | 1 | 2 (quinzenal) ou N | Escala |
| Título / texto final da mensagem | "📋 *ESCALA DE PLANTÃO*" / vazio | Texto livre | Mensagem |
| Evitar semanas seguidas | Ligado | Desligado | Avançadas |
| Compensar ausências | Desligado | Ligado | Avançadas |
| Nunca juntos | (vazio) | Pares de pessoas | Avançadas |
| Duplas fixas (sempre juntos) | (vazio) | Pares de pessoas | Avançadas |
| Cópia de segurança manual | — | Botões "Salvar cópia" / "Restaurar" | Avançadas |

Botão **"Restaurar padrão"** desfaz todas as configurações (com confirmação).

---

## 5. Stack tecnológica

| Tecnologia | Uso | Justificativa (do debate) |
|---|---|---|
| Python 3.12+ | Linguagem | Didática, usada na faculdade |
| CustomTkinter | Interface | Desktop moderno e simples; vai dentro do `.exe` (usuário não instala nada). Streamlit foi descartado: na nuvem exige banco externo e internet; em `.exe` fica pesado e frágil |
| JSON (stdlib) | Dados | Legível, didático; 1 usuário e poucos dados → banco de dados seria exagero |
| requests | HTTP (atualizador) | Padrão de mercado |
| hashlib, threading, logging, dataclasses (stdlib) | SHA-256, segundo plano, log, modelos | Já vêm com o Python |
| pytest *(dev)* | Testes | Garante o algoritmo |
| PyInstaller *(dev)* | `.exe` único | Empacota Python + bibliotecas |
| GitHub Actions | CI/CD | Testa e publica Releases ao criar uma *tag* |

`requirements.txt`: `customtkinter`, `requests`. `requirements-dev.txt`: `-r requirements.txt`, `pytest`, `pyinstaller`.
**Sem** `tkcalendar` (o calendário é um componente próprio — bom exercício e evita problemas no PyInstaller).

---

## 6. Estrutura de diretórios

```
Planejador de Escala de Trabalho/
├── AGENTS.md                    # Este arquivo
├── README.md                    # Guia do desenvolvedor (rodar, testar, publicar)
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .gitignore
├── iniciar.py                   # Lançador usado pelo PyInstaller (chama src.escala.main.iniciar)
├── src/
│   └── escala/
│       ├── __init__.py
│       ├── main.py              # Configura logging, carrega dados, abre a janela
│       ├── versao.py            # VERSAO e REPOSITORIO_GITHUB
│       ├── modelos.py           # Dataclasses (seção 7)
│       ├── datas.py             # Utilidades de data em português
│       ├── armazenamento.py     # JSON, backups, salvamento atômico, recuperação
│       ├── historico.py         # Contadores de justiça a partir das escalas confirmadas
│       ├── gerador.py           # ALGORITMO da escala (coração do projeto)
│       ├── edicao.py            # Trocar pessoas, validar, confirmar rascunho
│       ├── exportar.py          # Texto para WhatsApp
│       ├── textos_ajuda.py      # Explicações + exemplos de cada configuração
│       ├── atualizador.py       # GitHub Releases + SHA-256 + substituição do .exe
│       └── interface/
│           ├── __init__.py
│           ├── componentes.py           # BotaoGrande, CampoComAjuda, CalendarioMensal, diálogos
│           ├── janela_principal.py      # Janela, abas, cabeçalho, rodapé
│           ├── tela_equipe.py           # Aba 👥 Equipe
│           ├── tela_folgas.py           # Aba 📅 Folgas
│           ├── tela_escala.py           # Aba 📋 Escala
│           ├── janela_feriado.py        # Diálogo "Adicionar feriado"
│           ├── janela_justica.py        # Diálogo "📊 Quadro de justiça" (fila e contadores)
│           ├── janela_historico.py      # Escalas anteriores (ver/editar/excluir)
│           └── janela_configuracoes.py  # ⚙️ Configurações (com ajuda)
├── tests/
│   ├── conftest.py              # Fixtures: equipe de 28, configuração padrão, pasta temporária
│   ├── test_versao.py
│   ├── test_modelos.py
│   ├── test_datas.py
│   ├── test_armazenamento.py
│   ├── test_historico.py
│   ├── test_gerador.py
│   ├── test_edicao.py
│   ├── test_exportar.py
│   ├── test_textos_ajuda.py
│   └── test_atualizador.py      # Sem internet: usa monkeypatch
├── docs/
│   ├── DIARIO_DE_APRENDIZADO.md
│   └── MANUAL_DO_USUARIO.md
└── .github/
    └── workflows/
        ├── testes.yml           # pytest a cada push
        └── release.yml          # Tag v* → testes → .exe → .sha256 → Release
```

---

## 7. Modelo de dados

### 7.1 Classes (`modelos.py`)
```python
from dataclasses import dataclass, field
from datetime import date, datetime

PERIODOS_PADRAO: list[str] = ["manhã", "tarde", "noite", "dia inteiro"]
MODOS_EXPERIENCIA: list[str] = ["preferencia", "obrigatoria", "ignorar"]


@dataclass
class Pessoa:
    """Uma pessoa da equipe."""
    id: int
    nome: str
    experiente: bool = False
    ativo: bool = True                    # desativar = não escalar, mas manter histórico
    data_entrada: date = field(default_factory=date.today)  # ao reativar, vira a data de hoje
    indisponibilidades: set[date] = field(default_factory=set)


@dataclass
class ModeloDeTurno:
    """Turno que se repete toda semana. Ex.: sábado (5), manhã, 4 duplas."""
    dia_da_semana: int                    # 0 = segunda ... 5 = sábado, 6 = domingo (date.weekday())
    periodo: str
    qtd_duplas: int


@dataclass
class Feriado:
    """Data especial com plantão próprio."""
    data: date
    nome: str = ""
    periodos: dict[str, int] = field(default_factory=lambda: {"manhã": 4})  # período -> nº de duplas


@dataclass
class Dupla:
    """Duas pessoas (por id) trabalhando juntas."""
    pessoa_a: int
    pessoa_b: int

    def ids(self) -> tuple[int, int]:
        """Retorna os dois ids."""

    def contem(self, id_pessoa: int) -> bool:
        """Diz se a pessoa está nesta dupla."""


@dataclass
class Plantao:
    """Um turno em uma data específica, com suas duplas."""
    data: date
    periodo: str
    qtd_duplas: int
    eh_feriado: bool = False
    nome_feriado: str = ""
    duplas: list[Dupla] = field(default_factory=list)

    def pessoas(self) -> set[int]:
        """Ids de todas as pessoas escaladas neste plantão."""


@dataclass
class Escala:
    """Conjunto de plantões gerados de uma vez (1 ou mais semanas)."""
    plantoes: list[Plantao]
    gerada_em: datetime
    confirmada: bool = False

    def primeiro_dia(self) -> date:
        """Data do primeiro plantão."""

    def ultimo_dia(self) -> date:
        """Data do último plantão."""

    def pessoas_no_dia(self, dia: date) -> set[int]:
        """Ids de quem trabalha em qualquer plantão nesta data."""


@dataclass
class Configuracao:
    """Todas as opções que o usuário pode mudar. Os valores padrão são as decisões da seção 4."""
    turnos: list[ModeloDeTurno] = field(default_factory=lambda: [
        ModeloDeTurno(5, "manhã", 4), ModeloDeTurno(6, "tarde", 4)])
    periodos: list[str] = field(default_factory=lambda: list(PERIODOS_PADRAO))  # também define a ORDEM no dia
    feriados_ativos: bool = True
    feriado_periodos_padrao: dict[str, int] = field(default_factory=lambda: {"manhã": 4})
    modo_experiencia: str = "preferencia"
    semanas_por_geracao: int = 1
    titulo_mensagem: str = "📋 *ESCALA DE PLANTÃO*"
    texto_final_mensagem: str = ""
    evitar_semanas_seguidas: bool = True
    compensar_ausencias: bool = False
    nunca_juntos: list[tuple[int, int]] = field(default_factory=list)
    sempre_juntos: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class DadosDoPrograma:
    """Tudo o que é salvo no arquivo de dados."""
    pessoas: list[Pessoa] = field(default_factory=list)
    configuracao: Configuracao = field(default_factory=Configuracao)
    feriados: list[Feriado] = field(default_factory=list)
    escalas: list[Escala] = field(default_factory=list)   # SOMENTE confirmadas (histórico)
    rascunho: Escala | None = None                       # última gerada, ainda não confirmada
    proximo_id: int = 1

    def buscar_pessoa(self, id_pessoa: int) -> Pessoa | None:
        """Retorna a pessoa com esse id (ou None)."""

    def pessoas_ativas(self) -> list[Pessoa]:
        """Lista das pessoas ativas, em ordem alfabética."""

    def adicionar_pessoa(self, nome: str, experiente: bool = False) -> Pessoa:
        """Cria a pessoa com novo id. Levanta ErroEscala se o nome for vazio ou repetido (ignora maiúsculas)."""
```
> `ErroEscala` é definido em `modelos.py` (para todos os módulos poderem usá-lo sem importação circular):
> `class ErroEscala(Exception): """Erro de regra com mensagem pronta para o usuário."""`

### 7.2 Arquivo de dados
- Local: `%APPDATA%/PlanejadorEscala/dados.json` (variável de ambiente `PLANEJADOR_PASTA_DADOS` substitui a pasta — usada nos testes).
- Backups: `%APPDATA%/PlanejadorEscala/backups/dados_AAAAMMDD_HHMMSS.json` — cópia **antes** de cada salvamento; manter os 10 mais recentes.
- Log: `%APPDATA%/PlanejadorEscala/registro.log` (`RotatingFileHandler`, 1 MB, 3 arquivos).
- **Salvamento atômico**: grava em `dados.json.tmp` e depois `os.replace()` → um desligamento no meio nunca corrompe o arquivo.
- **Recuperação**: se `dados.json` estiver corrompido, carregar o backup válido mais recente e avisar o usuário.
- Datas em ISO (`"2026-11-07"`); conjuntos viram listas ordenadas; tuplas viram listas.

```json
{
  "versao_dados": 1,
  "proximo_id": 3,
  "pessoas": [
    {"id": 1, "nome": "Ana", "experiente": true, "ativo": true,
     "data_entrada": "2026-11-01", "indisponibilidades": ["2026-11-14"]},
    {"id": 2, "nome": "Bruno", "experiente": false, "ativo": true,
     "data_entrada": "2026-11-01", "indisponibilidades": []}
  ],
  "configuracao": {
    "turnos": [{"dia_da_semana": 5, "periodo": "manhã", "qtd_duplas": 4},
               {"dia_da_semana": 6, "periodo": "tarde", "qtd_duplas": 4}],
    "periodos": ["manhã", "tarde", "noite", "dia inteiro"],
    "feriados_ativos": true,
    "feriado_periodos_padrao": {"manhã": 4},
    "modo_experiencia": "preferencia",
    "semanas_por_geracao": 1,
    "titulo_mensagem": "📋 *ESCALA DE PLANTÃO*",
    "texto_final_mensagem": "",
    "evitar_semanas_seguidas": true,
    "compensar_ausencias": false,
    "nunca_juntos": [],
    "sempre_juntos": []
  },
  "feriados": [{"data": "2026-11-20", "nome": "Consciência Negra", "periodos": {"manhã": 4}}],
  "rascunho": null,
  "escalas": [
    {"gerada_em": "2026-11-04T17:00:00", "confirmada": true,
     "plantoes": [{"data": "2026-11-07", "periodo": "manhã", "qtd_duplas": 4,
                   "eh_feriado": false, "nome_feriado": "", "duplas": [[1, 2]]}]}
  ]
}
```

---

## 8. Algoritmo da escala

### 8.1 Definições
- **Plantão**: um turno numa data (ex.: sábado 07/11, manhã, 4 duplas).
- **Semana**: segunda a domingo (`date.isocalendar()`), incluindo feriados dela.
- **Presente na semana**: pessoa ativa, com `data_entrada` ≤ último dia da semana e disponível em pelo menos um plantão da semana. Caso contrário, **ausente**.

### 8.2 Regras
**Obrigatórias (nunca violar; se impossível → `ErroEscala`):**
1. Cada plantão tem exatamente `qtd_duplas` duplas.
2. Ninguém em dois plantões no mesmo dia.
3. Ninguém escalado em data indisponível.
4. Só pessoas ativas.
5. Se configurado: "nunca juntos" nunca formam dupla; experiência "obrigatória" é garantida.

**Desejáveis (em ordem de importância):**
6. Equilíbrio geral: diferença de carga entre quem mais e quem menos trabalhou ≤ 1.
7. Equilíbrio de feriados (contador separado).
8. No máximo um plantão por pessoa por semana (só repete se faltar gente, ex.: Carnaval).
9. Um experiente por dupla (modo "preferencia").
10. Variedade de parceiros.
11. Descanso: evitar semanas seguidas (se ligado).
12. (Leve) Alternar dia/período.

### 8.3 Contadores de justiça (`historico.py`)
São **sempre recalculados** a partir das escalas **confirmadas** (fonte única da verdade — nada de contador salvo no JSON). Editar uma escala confirmada corrige a justiça automaticamente.

Reprocessar as semanas em ordem cronológica:
1. Para cada plantão da semana: `carga[id] += 1`; se feriado, `feriados[id] += 1`; atualizar `ultimo_plantao`, `vezes_juntos`, `vezes_no_turno`, `semanas_trabalhadas`.
2. **Piso (regra "não compensar")**: ao fim da semana, cada pessoa **ausente** recebe `carga = max(carga, menor carga entre os presentes)` (idem para `feriados`).
   - Com `compensar_ausencias = True`, indisponibilidade **não** torna a pessoa ausente (ela "fica devendo"). Semanas antes de `data_entrada` sempre contam como ausência (pessoa nova nunca deve plantões).
   - Resultado: pessoa nova, reativada ou que volta de férias **entra empatada com quem menos trabalhou**.

### 8.4 Geração (`gerador.py`) — algoritmo guloso
1. `montar_plantoes_vazios`: para cada dia do período, se for feriado (e `feriados_ativos`) usa os períodos do feriado — **um feriado num sábado substitui os turnos do sábado**; senão, usa os `turnos` do dia da semana. Ordenar por data e pela ordem de `configuracao.periodos`.
2. Copiar os contadores do histórico (`copy.deepcopy`). Para cada plantão em ordem:
   1. **Candidatos**: ativos, disponíveis na data, ainda não escalados nesse dia.
   2. Se `len(candidatos) < 2 × qtd_duplas` → `ErroEscala("Não há pessoas suficientes no sábado 07/11 (manhã): precisa de 8, há 6.")`.
   3. **Ordenar** pela tupla (menor = maior prioridade):
      ```
      (trabalha_nesta_semana: 0/1,
       carga,
       feriados se o plantão for feriado, senão 0,
       trabalhou_semana_anterior: 0/1   (0 se evitar_semanas_seguidas=False),
       -dias_desde_ultimo_plantao        (0 se evitar_semanas_seguidas=False; nunca trabalhou = 9999),
       vezes_no_turno[(id, dia_da_semana, periodo)],
       sorteio.random())
      ```
   4. **Escolher** os `2 × qtd_duplas` primeiros. Duplas fixas: ao escolher alguém com par fixo que também é candidato, levar os dois (se couber; senão pular para o próximo). Par fixo indisponível → a pessoa entra sozinha normalmente.
   5. Modo **obrigatória**: se houver menos experientes que `qtd_duplas` entre os escolhidos, trocar os não experientes de menor prioridade pelos experientes não escolhidos de maior prioridade. Ainda insuficiente → `ErroEscala` sugerindo mudar a opção para "Preferência".
   6. **Formar duplas** (`formar_duplas`):
      1. Duplas fixas escolhidas primeiro.
      2. Se modo ≠ "ignorar": cada experiente (em ordem de prioridade) com o não experiente de menor `vezes_juntos`.
      3. Restantes: repetidamente, o par de menor `custo_do_par`.
      - `custo_do_par` = (10 se nenhum experiente e modo ≠ "ignorar") + `vezes_juntos` + (∞ se "nunca juntos").
      - Se só sobrar par proibido → `ErroEscala` amigável.
   7. `registrar_plantao` nos contadores e seguir.
3. A escala nasce como **rascunho** (`confirmada=False`). Gerar de novo substitui o rascunho e não afeta a justiça.

> Evolução futura (exercício de faculdade, fora do escopo): comparar com *backtracking* ou OR-Tools.

---

## 9. Assinaturas (contrato da camada de lógica)

### `versao.py`
```python
VERSAO: str = "0.1.0"                 # MAIOR.MENOR.CORREÇÃO
REPOSITORIO_GITHUB: str = ""          # "usuario/repositorio" — preencher quando o repo existir
```

### `datas.py`
```python
DIAS_DA_SEMANA: list[str] = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

def inicio_da_semana(dia: date) -> date:
    """Retorna a segunda-feira da semana de `dia`."""

def chave_da_semana(dia: date) -> tuple[int, int]:
    """Identifica a semana: (ano ISO, nº da semana ISO)."""

def dias_do_periodo(inicio: date, qtd_semanas: int) -> list[date]:
    """Todos os dias de `qtd_semanas` semanas a partir da segunda-feira de `inicio`."""

def formatar_data(dia: date) -> str:
    """Ex.: date(2026, 11, 7) -> '07/11'."""

def formatar_dia_completo(dia: date) -> str:
    """Ex.: date(2026, 11, 7) -> 'Sábado, 07/11'."""

def ler_data(texto: str) -> date:
    """Converte 'dd/mm/aaaa' em date. Levanta ErroEscala('Data inválida: use o formato 25/12/2026.')."""
```

### `armazenamento.py`
```python
VERSAO_DADOS: int = 1
QTD_BACKUPS: int = 10

def pasta_de_dados() -> Path:
    """Pasta dos dados (%APPDATA%/PlanejadorEscala ou PLANEJADOR_PASTA_DADOS). Cria se não existir."""

def carregar(pasta: Path | None = None) -> tuple[DadosDoPrograma, str | None]:
    """Lê os dados. Retorna (dados, aviso). Arquivo inexistente -> dados padrão.
    Arquivo corrompido -> restaura o backup válido mais recente e devolve um aviso amigável."""

def salvar(dados: DadosDoPrograma, pasta: Path | None = None) -> None:
    """Faz backup do arquivo atual, grava de forma atômica e limpa backups antigos."""

def dados_para_dict(dados: DadosDoPrograma) -> dict:
    """Converte os objetos em dicionário pronto para JSON (serialização)."""

def dados_de_dict(bruto: dict) -> DadosDoPrograma:
    """Converte o dicionário lido do JSON em objetos (desserialização). Aplica `migrar` antes."""

def migrar(bruto: dict) -> dict:
    """Atualiza dados de versões antigas para VERSAO_DADOS (hoje não faz nada além de validar)."""

def exportar_copia(dados: DadosDoPrograma, destino: Path) -> None:
    """Backup manual: grava todos os dados no arquivo escolhido pelo usuário."""

def importar_copia(origem: Path) -> DadosDoPrograma:
    """Lê uma cópia manual. Levanta ErroEscala se o arquivo não for uma cópia válida."""
```

### `historico.py`
```python
@dataclass
class Contadores:
    """Números usados para decidir quem trabalha. Sempre derivados das escalas confirmadas."""
    carga: dict[int, int]
    feriados: dict[int, int]
    ultimo_plantao: dict[int, date]
    vezes_juntos: dict[frozenset[int], int]
    vezes_no_turno: dict[tuple[int, int, str], int]      # (id, dia_da_semana, periodo)
    semanas_trabalhadas: dict[int, set[tuple[int, int]]] # id -> chaves de semana

@dataclass
class ResumoJustica:
    """Linha do quadro de justiça para mostrar ao usuário."""
    posicao: int                 # 1 = primeiro da fila (maior prioridade)
    pessoa: Pessoa
    plantoes_reais: int          # quantos plantões realmente fez nas escalas confirmadas
    carga_justica: int           # contador usado pelo algoritmo (inclui o piso de entrada/férias)
    feriados_trabalhados: int    # quantos feriados realmente trabalhou
    ultimo_plantao: date | None  # data do último plantão confirmado (ou None)

def calcular_contadores(dados: DadosDoPrograma) -> Contadores:
    """Reprocessa as escalas confirmadas em ordem e aplica o piso de ausências (seção 8.3)."""

def quadro_de_justica(dados: DadosDoPrograma) -> list[ResumoJustica]:
    """Retorna as pessoas ativas ordenadas por prioridade (quem está na frente da fila vem primeiro)."""

def registrar_plantao(contadores: Contadores, plantao: Plantao) -> None:
    """Soma um plantão aos contadores (usado no histórico e durante a geração)."""

def esta_presente(pessoa: Pessoa, dias_com_plantao: list[date], config: Configuracao) -> bool:
    """Diz se a pessoa conta como presente na semana (regra da seção 8.1/8.3)."""
```

### `gerador.py`
```python
def montar_plantoes_vazios(inicio: date, qtd_semanas: int, config: Configuracao,
                           feriados: list[Feriado]) -> list[Plantao]:
    """Cria os plantões (sem duplas) do período, já com feriados aplicados e em ordem."""

def gerar_escala(dados: DadosDoPrograma, inicio: date, qtd_semanas: int,
                 semente: int | None = None) -> Escala:
    """Gera um rascunho de escala para o período. Levanta ErroEscala com mensagem amigável."""

def listar_candidatos(plantao: Plantao, pessoas: list[Pessoa], escalados_no_dia: set[int]) -> list[Pessoa]:
    """Pessoas ativas, disponíveis na data e ainda não escaladas nesse dia."""

def chave_de_prioridade(pessoa: Pessoa, plantao: Plantao, contadores: Contadores,
                        config: Configuracao, sorteio: random.Random) -> tuple:
    """Tupla de ordenação da seção 8.4 (menor = escolhido primeiro)."""

def escolher_pessoas(candidatos: list[Pessoa], plantao: Plantao, contadores: Contadores,
                     config: Configuracao, sorteio: random.Random) -> list[Pessoa]:
    """Escolhe 2 × qtd_duplas pessoas (prioridade, duplas fixas, modo de experiência)."""

def formar_duplas(escolhidas: list[Pessoa], contadores: Contadores, config: Configuracao) -> list[Dupla]:
    """Forma as duplas minimizando o custo (seção 8.4, passo 6)."""

def custo_do_par(a: Pessoa, b: Pessoa, contadores: Contadores, config: Configuracao) -> float:
    """Quanto pior a dupla, maior o custo. 'Nunca juntos' = infinito."""

def descrever_plantao(plantao: Plantao) -> str:
    """Texto para mensagens. Ex.: 'sábado 07/11 (manhã)'."""
```

### `edicao.py`
```python
def trocar_pessoa(escala: Escala, indice_plantao: int, id_sai: int, id_entra: int,
                  dados: DadosDoPrograma) -> list[str]:
    """Troca uma pessoa num plantão. Levanta ErroEscala se quebrar a regra 2 (mesmo dia).
    Retorna avisos (ex.: 'Ana marcou folga neste dia') sem bloquear — o usuário decide."""

def validar_escala(escala: Escala, dados: DadosDoPrograma) -> list[str]:
    """Lista em português todas as regras quebradas na escala (vazia = tudo certo)."""

def pessoas_para_troca(escala: Escala, indice_plantao: int, dados: DadosDoPrograma) -> list[tuple[Pessoa, str]]:
    """Opções para o menu de troca: (pessoa, observação), ex.: (Bruno, 'já trabalha domingo')."""

def escalas_sobrepostas(dados: DadosDoPrograma, escala: Escala) -> list[int]:
    """Índices das escalas confirmadas com datas em comum com `escala`."""

def confirmar_rascunho(dados: DadosDoPrograma) -> None:
    """Move o rascunho para o histórico (substituindo sobrepostas — a interface pergunta antes)."""

def excluir_escala(dados: DadosDoPrograma, indice: int) -> None:
    """Remove uma escala confirmada do histórico (a interface pede confirmação antes)."""
```

### `exportar.py`
```python
def gerar_texto_whatsapp(escala: Escala, dados: DadosDoPrograma) -> str:
    """Monta o texto da seção 10.6 para colar no WhatsApp."""
```

### `textos_ajuda.py`
```python
@dataclass
class TextoAjuda:
    """Explicação de uma configuração para o usuário leigo."""
    titulo: str
    explicacao: str
    exemplo: str

AJUDA: dict[str, TextoAjuda]   # chave = nome do campo em Configuracao (+ "backup_manual"); conteúdo na seção 11

def obter_ajuda(chave: str) -> TextoAjuda:
    """Retorna o texto de ajuda. Levanta KeyError se a chave não existir (erro de programação)."""
```

### `atualizador.py`
```python
NOME_DO_EXE: str = "PlanejadorEscala.exe"

class ErroAtualizacao(Exception):
    """Falha ao baixar ou verificar a atualização (nunca mostrada como traceback)."""

@dataclass
class InfoAtualizacao:
    versao: str
    url_exe: str
    url_hash: str
    notas: str

def comparar_versoes(a: str, b: str) -> int:
    """-1 se a < b, 0 se iguais, 1 se a > b. Aceita prefixo 'v' ('v1.2.0')."""

def programa_esta_empacotado() -> bool:
    """True se rodando como .exe (sys.frozen). Rodando do código-fonte, não atualiza."""

def buscar_atualizacao(versao_atual: str = VERSAO, tempo_limite: float = 5.0) -> InfoAtualizacao | None:
    """Consulta a última Release. Sem internet, sem repositório configurado ou qualquer erro -> None (silencioso)."""

def calcular_sha256(caminho: Path) -> str:
    """Hash SHA-256 do arquivo em hexadecimal (lendo em blocos)."""

def baixar_e_verificar(info: InfoAtualizacao, pasta_destino: Path) -> Path:
    """Baixa o .exe e o .sha256; compara os hashes. Diferente -> apaga o arquivo e levanta ErroAtualizacao."""

def instalar_e_reiniciar(novo_exe: Path) -> None:
    """Cria um .bat que espera o programa fechar, substitui o .exe, reabre e se apaga; executa e encerra."""

def verificar_em_segundo_plano(ao_encontrar: Callable[[InfoAtualizacao], None]) -> None:
    """Roda buscar_atualizacao numa thread daemon e chama `ao_encontrar` se houver versão nova.
    ATENÇÃO: a interface deve repassar o callback para a thread principal com `janela.after(0, ...)`."""
```

---

## 10. Arquitetura de Frontend e Guia de UI/UX

### 10.1 Padrão arquitetural (Fluxo Unidirecional de Estado)
A interface segue uma separação rigorosa entre **estado** e **visualização** (inspirada em MVC / Flux):

```
[DadosDoPrograma] ──lê──► [Tela: atualizar_tela()] ──clique──► [Camada de Lógica]
        ▲                                                              │
        └────────── salva (armazenamento.py) ◄── ao_mudar() ◄──────────┘
```

1. **Fonte única de estado**: `JanelaPrincipal` guarda a única instância de `DadosDoPrograma` e a passa para as telas.
2. **Proibido guardar estado duplicado na tela**: widgets não são fonte de verdade. Toda tela tem um método `atualizar_tela() -> None` que reconstrói/atualiza os elementos visuais a partir de `self.dados`.
3. **Fluxo de toda ação do usuário**:
   - O botão chama um método da tela.
   - O método chama a função da **camada de lógica** dentro de `try ... except ErroEscala as erro:`.
   - Se levantar `ErroEscala`, chama `mostrar_erro(str(erro))` e **interrompe** (nada é salvo).
   - Se der certo, chama `self.ao_mudar()`, que executa `armazenamento.salvar(self.dados)` e chama `atualizar_tela()` nas abas.
4. **Proibido na interface**: fazer contas de justiça, sortear pessoas, editar listas de duplas diretamente sem `edicao.py`, ou ler/gravar arquivos JSON sem `armazenamento.py`.

### 10.2 Design System e Tokens Visuais (`componentes.py`)
Para a interface parecer limpa, profissional e fácil para uma pessoa leiga, **todas** as telas devem usar as constantes abaixo (proibido espalhar cores ou tamanhos mágicos pelas telas):

- **Modo de aparência fixo**: `ctk.set_appearance_mode("light")` (modo claro). É mais legível em ambientes iluminados e familiar para quem usa papel, WhatsApp Web e Word.
- **Paleta semântica** (cada cor tem um significado único):
  | Token | Cor (Hex) | Uso obrigatório |
  |---|---|---|
  | `COR_FUNDO` | `#F8FAFC` | Fundo geral da janela |
  | `COR_CARTAO` | `#FFFFFF` | Fundo dos cartões e painéis (borda `#E2E8F0`, `corner_radius=10`) |
  | `COR_PRIMARIA` | `#1D4ED8` (hover `#1E40AF`) | **Apenas** a ação principal da tela ("Gerar escala", "+ Adicionar pessoa", "Salvar") |
  | `COR_SUCESSO` | `#15803D` (hover `#166534`) | Conclusão positiva ("✅ Confirmar escala", "📋 Copiar para WhatsApp") |
  | `COR_SECUNDARIA` | `#E2E8F0` (texto `#1E293B`, hover `#CBD5E1`) | Ações auxiliares ("Editar", "📊 Quadro de justiça", "📜 Escalas anteriores") |
  | `COR_PERIGO` | `#B91C1C` (hover `#991B1B`) | Ações destrutivas ("Desativar", "Excluir", "Restaurar padrão") |
  | `COR_AVISO_FUNDO` / `COR_AVISO_TEXTO` | `#FEF3C7` / `#92400E` | Faixas de aviso (rascunho não confirmado, troca com observação) |
  | `COR_TEXTO` / `COR_TEXTO_SUAVE` | `#0F172A` / `#475569` | Texto principal / textos de ajuda, exemplos e inativos |
- **Tipografia** (`Segoe UI`):
  - `FONTE_TITULO = ("Segoe UI", 20, "bold")` — título da aba/janela.
  - `FONTE_SUBTITULO = ("Segoe UI", 16, "bold")` — título de cartão (ex.: "Sábado, 07/11 — Manhã").
  - `FONTE_CORPO = ("Segoe UI", 15)` — listas, nomes, campos e botões secundários (nunca menor que 14).
  - `FONTE_BOTAO = ("Segoe UI", 16, "bold")` — botões principais.
  - `FONTE_AJUDA = ("Segoe UI", 13)` — explicações e exemplos abaixo dos campos.
- **Espaçamento e Lei de Fitts**:
  - Margem externa de cada aba: `padx=20, pady=20`.
  - Espaço entre cartões: `pady=8` a `12`; preenchimento interno do cartão: `padx=16, pady=16`.
  - Áreas clicáveis grandes: botões principais com `height=44`, secundários e linhas clicáveis com `height=36`.
  - No máximo **1 botão azul (`COR_PRIMARIA`)** ou verde (`COR_SUCESSO`) em destaque por grupo, para o olho do usuário saber imediatamente onde clicar.

### 10.3 Regras de UX e Usabilidade (Heurísticas de Nielsen)
1. **Estados vazios orientativos (*Empty States*)**: nunca mostrar um quadro em branco sem explicação.
   - Equipe sem ninguém: *"Nenhuma pessoa cadastrada ainda. Clique em '+ Adicionar pessoa' para começar."*
   - Escala vazia: *"Escolha o período acima e clique em 'Gerar escala'."*
   - Histórico vazio: *"Nenhuma escala foi confirmada ainda."*
2. **Visibilidade do status do sistema**:
   - Escala em **rascunho**: faixa amarela no topo da escala: *"⚠️ Rascunho — esta escala ainda não está valendo. Clique em 'Confirmar escala' para salvar no histórico."*
   - Escala **confirmada**: faixa verde discreta: *"✅ Escala confirmada e salva no histórico."*
   - Botão **Copiar para WhatsApp**: ao clicar, muda o próprio texto para *"✅ Copiado!"* por 2 segundos (`after(2000, ...)`) — feedback imediato sem abrir pop-up desnecessário.
3. **Layout responsivo e janelas modais**:
   - Usar `grid` com `grid_columnconfigure` / `grid_rowconfigure(..., weight=1)` para a área principal crescer quando o usuário maximizar a janela.
   - Listas que podem crescer (equipe, plantões, configurações, quadro de justiça) ficam sempre dentro de `ctk.CTkScrollableFrame`.
   - Toda janela secundária (`CTkToplevel`) deve ser **modal** (`transient(pai)`, `grab_set()`, `focus()`), abrir centralizada sobre a janela principal e fechar com a tecla `Esc`.

### 10.4 `componentes.py`
- Constantes de cores e fontes da seção 10.2.
- `BotaoGrande(master, texto, comando, variante="primaria")` — variantes `"primaria"`, `"sucesso"`, `"secundaria"`, `"perigo"`.
- `CartaoFrame(master)` — `CTkFrame` branco com borda e cantos arredondados.
- `CampoComAjuda(master, chave_ajuda, widget)` — título + controle + explicação + exemplo em `COR_TEXTO_SUAVE` (de `textos_ajuda`).
- `CalendarioMensal(master, datas_marcadas: set[date], ao_clicar: Callable[[date], None])` — grade 7×6 de botões, setas ◀ ▶ de mês, dias marcados em vermelho.
- `configurar_janela_modal(janela: ctk.CTkToplevel, pai: ctk.CTk, titulo: str, largura: int, altura: int) -> None`.
- `perguntar_sim_nao(titulo, texto) -> bool`, `mostrar_erro(texto)`, `mostrar_info(texto)`.

### 10.5 Telas
1. **`JanelaPrincipal(ctk.CTk)`**: tamanho inicial 1080×720 (mínimo 960×640); cabeçalho com título e botão **⚙️ Configurações**; 3 abas grandes (**👥 Equipe**, **📅 Folgas**, **📋 Escala**); rodapé com versão e aviso de atualização. Ao abrir: se `carregar()` devolver aviso (dados recuperados), mostrá-lo.
2. **👥 Equipe** (`tela_equipe.py`): contador no topo (*"28 pessoas ativas (10 experientes)"*); lista em cartões/linhas claras (nome, selo `⭐ Experiente`, "inativo" em cinza no fim). Botões: **+ Adicionar pessoa** (primário), **Editar** (nome/experiente), **Desativar/Reativar** (reativar ajusta `data_entrada` para hoje). Remover definitivamente só em "Editar", com confirmação, e só se a pessoa não estiver em escalas confirmadas.
3. **📅 Folgas** (`tela_folgas.py`): lista de pessoas ativas à esquerda (mostrando quantas folgas futuras cada uma tem); `CalendarioMensal` à direita (clicar no dia marca/desmarca) + lista das datas marcadas com botão "Remover". Botão **"Marcar período (férias)"**: de/até.
4. **📋 Escala** (`tela_escala.py`):
   - Topo (barra de controle em um `CartaoFrame`): período (**"Esta semana"** / **"Próxima semana"** / **"Escolher data…"**), nº de semanas, feriados do período + **"+ Adicionar feriado"** (`janela_feriado.py`), e botão **"Gerar escala"** (primário).
   - Barra de status da escala (faixa de rascunho ou confirmada) + avisos de validação em amarelo.
   - Área central rolável: cartões por plantão (*"📅 Sábado, 07/11 — Manhã"*), cada dupla numerada com dois menus (`CTkOptionMenu` ou diálogo de troca usando `pessoas_para_troca`).
   - Rodapé da aba: à esquerda, **"📊 Quadro de justiça"** e **"📜 Escalas anteriores"** (secundários); à direita, **"✅ Confirmar escala"** e **"📋 Copiar para WhatsApp"** (sucesso).
5. **📊 Quadro de justiça** (`janela_justica.py`):
   - Explicação curta no topo: *"As pessoas no topo da lista têm prioridade para entrar na próxima escala (contando apenas escalas já confirmadas)."*
   - Tabela rolável gerada por `quadro_de_justica(dados)` com colunas: **Ordem na fila** (`1º`, `2º`…), **Nome** (com ⭐), **Plantões feitos** (`plantoes_reais`), **Em feriados** (`feriados_trabalhados`), **Último plantão** (`07/11` ou `"Nunca"`), **Observação** (mostra *"Entrou/voltou empatado"* quando `carga_justica > plantoes_reais`).
6. **📜 Escalas anteriores** (`janela_historico.py`): listar escalas confirmadas por período, abrir para visualizar/trocar pessoas, copiar para WhatsApp ou excluir (com confirmação).
7. **⚙️ Configurações** (`janela_configuracoes.py`): seções **Turnos**, **Feriados**, **Duplas**, **Escala**, **Mensagem** e **Opções avançadas** (recolhida por padrão). Todo campo usa `CampoComAjuda`. Botões **Salvar** (primário), **Cancelar** (secundário), **Restaurar padrão** (perigo). Validar (nº de duplas ≥ 1; avisar se 2 × duplas de um dia > pessoas ativas).

### 10.6 Texto para WhatsApp (formato exato)
```
📋 *ESCALA DE PLANTÃO*

📅 *Sábado, 07/11 — Manhã*
1. Ana e Bruno
2. Carla e Diego
3. Elisa e Fábio
4. Gabi e Hugo

📅 *Sexta, 20/11 — Manhã (Feriado: Consciência Negra)*
1. ...
```
Título = `titulo_mensagem`; `texto_final_mensagem`, se não vazio, vai ao fim após uma linha em branco. Período com inicial maiúscula.

---

## 11. Textos de ajuda das configurações (`textos_ajuda.py`)

Linguagem simples, sem termos técnicos. Conteúdo mínimo (a IA pode melhorar a redação, mantendo o sentido):

| Chave | Título | Explicação | Exemplo |
|---|---|---|---|
| `turnos` | Turnos da semana | Quais dias e períodos têm plantão toda semana, e quantas duplas em cada um. | "Sábado — manhã — 4 duplas" = 8 pessoas trabalhando no sábado de manhã. |
| `periodos` | Nomes dos períodos | Os nomes que aparecem na escala e na mensagem, na ordem do dia. | Adicione "noite" se houver plantão noturno. |
| `feriados_ativos` | Plantão em feriados | Ligado: os feriados cadastrados entram na escala. | Desligado: o Natal fica sem ninguém escalado. |
| `feriado_periodos_padrao` | Padrão para feriados | Como um feriado novo já vem preenchido (dá para mudar em cada feriado). | "Manhã — 4 duplas": ao adicionar Finados, já vem assim. |
| `modo_experiencia` | Experiência na dupla | **Preferência**: tenta colocar 1 experiente por dupla. **Obrigatória**: nunca monta dupla sem experiente. **Ignorar**: não leva em conta. | Com "Obrigatória", se faltar gente experiente no sábado, o programa avisa em vez de montar a escala. |
| `semanas_por_geracao` | Semanas por vez | Quantas semanas o botão "Gerar escala" monta de uma vez. | 2 = escala quinzenal. |
| `titulo_mensagem` | Título da mensagem | Primeira linha do texto do WhatsApp. Texto entre \*asteriscos\* fica em **negrito**. | \*ESCALA DE PLANTÃO — NOVEMBRO\* |
| `texto_final_mensagem` | Texto final | Aparece no fim da mensagem (opcional). | "Trocas: falar com a coordenação." |
| `evitar_semanas_seguidas` | Evitar semanas seguidas | Tenta dar folga a quem trabalhou na semana anterior. | Com 28 pessoas e 16 vagas, algumas repetições são inevitáveis; o programa escolhe quem descansou mais. |
| `compensar_ausencias` | Compensar ausências | **Desligado (recomendado)**: quem volta de férias entra empatado com quem menos trabalhou. **Ligado**: quem se ausentou "fica devendo" e trabalha mais até igualar. | Ana tirou 1 mês de férias. Ligado: ela será escalada quase toda semana ao voltar. |
| `nunca_juntos` | Nunca juntos | Pessoas que não devem formar dupla. Podem trabalhar no mesmo dia, em duplas diferentes. | Ana ✕ Bruno. |
| `sempre_juntos` | Duplas fixas | Pessoas que sempre trabalham juntas. Se uma estiver de folga, a outra trabalha com outra pessoa. | Carla + Diego. |
| `backup_manual` | Cópia de segurança | "Salvar cópia" guarda todos os dados num arquivo (pendrive, e-mail). "Restaurar" troca os dados atuais pelos da cópia. | Útil ao trocar de computador. |

---

## 12. Atualização e publicação

### 12.1 Fluxo no programa
```
Abre o programa → (thread) GET https://api.github.com/repos/<REPOSITORIO_GITHUB>/releases/latest
  → tag_name > VERSAO?  não → nada
                         sim → "Nova versão X disponível! Deseja atualizar agora?"
                                 → baixa PlanejadorEscala.exe + PlanejadorEscala.exe.sha256 (%TEMP%)
                                 → SHA-256 confere? não → apaga, registra no log, não incomoda o usuário
                                                    sim → .bat substitui o .exe e reabre o programa
```
- Só atualiza se `programa_esta_empacotado()`. Sem internet → silencioso. HTTPS sempre. Nada de token.
- Sem permissão de escrita na pasta do `.exe` → mensagem: "Mova o programa para a pasta Documentos ou Área de Trabalho para receber atualizações."
- Dados ficam em `%APPDATA%` → atualizar nunca apaga dados.

### 12.2 Empacotamento
```powershell
pyinstaller --onefile --windowed --name PlanejadorEscala --collect-data customtkinter iniciar.py
```
`iniciar.py` (raiz) existe porque `main.py` usa imports `src.escala...`.

### 12.3 GitHub Actions
- `testes.yml`: em todo push/PR → Windows, Python 3.12, `pip install -r requirements-dev.txt`, `pytest`.
- `release.yml`: em tag `v*` → testes → conferir que a tag == `v` + `VERSAO` → PyInstaller → `Get-FileHash -Algorithm SHA256` → arquivo `PlanejadorEscala.exe.sha256` (só o hash, minúsculo) → publicar Release com os 2 arquivos (`softprops/action-gh-release`).

### 12.4 Como o desenvolvedor publica
1. Altera o código e `VERSAO` em `versao.py` (semântico: MAIOR.MENOR.CORREÇÃO).
2. `git commit` → `git push`.
3. `git tag v1.2.0` → `git push --tags`.
4. Actions testa, gera e publica. Usuários recebem o aviso ao abrir o programa.

> Segurança: o desenvolvedor deve ativar **verificação em duas etapas (2FA)** no GitHub.
> O Windows SmartScreen/antivírus pode alertar sobre `.exe` sem assinatura — documentar no manual ("Mais informações → Executar assim mesmo").

---

## 13. Fases (uma por vez) e critérios de "pronto"

| Fase | Entrega | Pronto quando | Conceitos a ensinar |
|---|---|---|---|
| 0 ✅ | Ambiente, Git, estrutura, janela de teste | Concluída | venv, pip, Git, pacotes |
| 1 ✅ | `modelos.py`, `datas.py`, `armazenamento.py` + testes | Concluída | dataclasses, type hints, JSON, serialização, pathlib, exceções |
| 2 ✅ | `historico.py`, `gerador.py`, `edicao.py` + testes | Concluída | algoritmo guloso, ordenação por tupla, conjuntos, dicionários, deepcopy, fonte única da verdade |
| 3 ✅ | `exportar.py`, `textos_ajuda.py` + testes | Concluída | f-strings, formatação |
| 4 ✅ | Interface base + Design System (`componentes.py`) + aba Equipe | Concluída | GUI, Design System, fluxo unidirecional, eventos, callbacks |
| 5 | Aba Folgas + `CalendarioMensal` | Folgas marcadas aparecem e são respeitadas na geração | layout em grade, responsividade, estados vazios |
| 6 | Aba Escala + feriado + quadro de justiça + histórico + copiar | Gerar → trocar → confirmar → copiar + quadro de justiça funcionando ponta a ponta | integração lógica ↔ interface, janelas modais, área de transferência |
| 7 | ⚙️ Configurações com ajuda | Todas as opções da seção 4.2 alteram o comportamento; "Restaurar padrão" funciona | parametrização, validação de entrada |
| 8 | `iniciar.py` + `.exe` manual | `.exe` abre num PC sem Python | empacotamento |
| 9 | `atualizador.py` + testes | Testes com monkeypatch verdes; atualização real testada com 2 versões | HTTP, API REST, threads, hash, versionamento semântico |
| 10 | GitHub Actions | Tag gera Release com `.exe` e `.sha256` | CI/CD |
| 11 | `MANUAL_DO_USUARIO.md` + polimento | Usuário leigo consegue usar só com o manual | documentação, UX |

---

## 14. Testes obrigatórios

`conftest.py`: fixture `equipe_28` (28 pessoas, 10 experientes, `data_entrada` antiga), `dados_padrao`, `pasta_temporaria` (via `tmp_path` + `PLANEJADOR_PASTA_DADOS`). Sempre usar `semente` fixa.

**datas / modelos**: `inicio_da_semana`, `formatar_dia_completo` ("Sábado, 07/11"), `ler_data` inválida → `ErroEscala`; `adicionar_pessoa` com nome repetido → `ErroEscala`.

**armazenamento**: ida e volta preserva tudo; arquivo inexistente → padrão; corrompido → recupera backup e retorna aviso; nunca mais de 10 backups; `importar_copia` inválida → `ErroEscala`.

**historico**: rascunho não conta; editar escala confirmada muda contadores; pessoa nova entra com a menor carga; volta de férias entra com a menor carga (padrão); com `compensar_ausencias=True` mantém a carga baixa; `quadro_de_justica` ordena corretamente quem trabalhou menos primeiro e distingue `plantoes_reais` de `carga_justica`.

**gerador**:
- Nº de duplas correto; ninguém 2× no mesmo dia; indisponíveis e inativos nunca escalados.
- 7 semanas no padrão → todos com exatamente 4 plantões (7 × 16 = 112 = 28 × 4).
- Semana com feriado (16 + 8 = 24 ≤ 28) → ninguém com 2 plantões na semana.
- Feriado num sábado substitui os turnos do sábado.
- "Preferência" com experientes suficientes entre os escolhidos → toda dupla tem experiente.
- "Obrigatória" garante; impossível → `ErroEscala`.
- "Nunca juntos" respeitado; duplas fixas juntas quando ambos disponíveis.
- Falta de gente → mensagem exata: "Não há pessoas suficientes no sábado 07/11 (manhã): precisa de 8, há 6."
- Mesma semente → mesma escala.

**edicao**: troca para alguém já escalado no dia → `ErroEscala`; troca para alguém de folga → aviso; `confirmar_rascunho` substitui sobrepostas.

**exportar**: texto exato da seção 10.6 (com e sem feriado e texto final).

**textos_ajuda**: todo campo de `Configuracao` tem ajuda com título, explicação e exemplo não vazios.

**atualizador**: `comparar_versoes` ("v1.10.0" > "1.9.9"); SHA-256 diferente → `ErroAtualizacao` e arquivo apagado; erro de rede → `None`; repositório vazio → `None`.

---

## 15. Comandos

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m src.escala.main          # rodar
pytest                             # testar
pyinstaller --onefile --windowed --name PlanejadorEscala --collect-data customtkinter iniciar.py
```

---

## 16. Status do projeto

| Item | Situação |
|---|---|
| Fase atual | **Fase 4 concluída** → próxima: **Fase 5** |
| Repositório GitHub | Ainda não criado (`REPOSITORIO_GITHUB` vazio) |
| Último commit relevante | Fase 4: interface base, design system e aba equipe |
