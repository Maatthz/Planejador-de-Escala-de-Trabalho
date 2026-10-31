# AGENTS.md — Planejador de Escala de Plantão

> Este arquivo é o guia oficial do projeto para qualquer agente de IA (ou pessoa) que for trabalhar no código.
> **Leia tudo antes de fazer qualquer alteração.**

---

## 1. Visão geral

Programa de desktop para **montar a escala de plantão de fim de semana** de uma equipe.

| Item | Valor |
|---|---|
| Pessoas na equipe | 28 (deve ser configurável) |
| Formato do plantão | Duplas |
| Duplas por fim de semana | 8 (= 16 pessoas trabalhando, 12 de folga) — configurável |
| Usuário final | Pouca experiência com computador |
| Distribuição | Um único `.exe` que a pessoa baixa e abre (sem instalar Python) |
| Atualizações | Automáticas via GitHub Releases |

### Objetivos principais
1. **Simplicidade extrema para o usuário final**: poucos botões, textos claros em português, sem termos técnicos.
2. **Escala justa**: todos trabalham aproximadamente a mesma quantidade de vezes.
3. **Atualização fácil**: o desenvolvedor publica uma versão nova no GitHub e o programa avisa e se atualiza.
4. **Didático**: o projeto também é material de estudo do desenvolvedor (iniciante, estudante de Ciência da Computação).

---

## 2. Regras para o agente (OBRIGATÓRIO)

### 2.1 Modo professor
O desenvolvedor está aprendendo. **Toda alteração deve vir acompanhada de uma explicação**, contendo:

1. **O que foi feito** — resumo em 1–3 frases.
2. **Por que foi feito** — qual problema resolve.
3. **Como funciona** — explicação passo a passo do código novo, citando arquivos e funções.
4. **Conceitos envolvidos** — nomeie e explique brevemente os conceitos de programação usados
   (ex.: "dicionário", "classe", "requisição HTTP", "algoritmo guloso", "serialização JSON").
5. **Para aprender mais** (opcional) — 1 ou 2 sugestões do que pesquisar.

Além disso, registre cada mudança relevante em `docs/DIARIO_DE_APRENDIZADO.md` (data, o que mudou, conceitos aprendidos).

### 2.2 Estilo de código
- Linguagem: **Python 3.12+**.
- Nomes de variáveis, funções e comentários **em português** (facilita o aprendizado). Ex.: `gerar_escala()`, `lista_de_pessoas`.
- Código simples e legível > código "esperto". Evite abstrações desnecessárias.
- Toda função deve ter uma *docstring* curta explicando o que faz.
- Comentários explicando o **porquê**, não só o **o quê**.
- Use *type hints* (`def somar(a: int, b: int) -> int:`), explicando o conceito na primeira vez.
- Mudanças pequenas e incrementais. Uma funcionalidade por vez.

### 2.3 Limites
- Não adicionar dependências sem justificar (e explicar ao desenvolvedor).
- Nunca apagar dados do usuário sem confirmação e backup.
- Não alterar a estrutura de pastas sem atualizar este arquivo.

---

## 3. Stack tecnológica (e por quê)

| Tecnologia | Uso | Por que essa escolha |
|---|---|---|
| **Python** | Linguagem principal | Fácil de aprender, muito usada na faculdade |
| **CustomTkinter** | Interface gráfica | Baseado no Tkinter (que já vem com o Python), mas com visual moderno. Simples de aprender |
| **JSON** | Armazenamento de dados | Arquivo de texto legível; ótimo para aprender. (Futuro opcional: SQLite) |
| **openpyxl** | Exportar escala para Excel | O usuário final provavelmente usa Excel/WhatsApp para divulgar a escala |
| **requests** | Verificar atualizações no GitHub | Biblioteca padrão de mercado para HTTP |
| **PyInstaller** | Gerar o `.exe` | Empacota Python + bibliotecas em um único arquivo executável |
| **pytest** | Testes automatizados | Garante que o algoritmo da escala continua correto após mudanças |
| **GitHub Actions** | Build automático do `.exe` | Ao criar uma *tag* de versão, o GitHub gera o `.exe` e publica a Release sozinho |

---

## 4. Estrutura de pastas

```
Planejador de Escala de Trabalho/
├── AGENTS.md                  # Este arquivo
├── README.md                  # Como rodar, como gerar o .exe (para o desenvolvedor)
├── requirements.txt           # Dependências do PROGRAMA (vão para o .exe)
├── requirements-dev.txt       # Dependências de desenvolvimento (pytest, pyinstaller)
├── pytest.ini                 # Configuração do pytest
├── .gitignore
├── src/
│   └── escala/
│       ├── __init__.py
│       ├── main.py            # Ponto de entrada: abre a janela
│       ├── versao.py          # VERSAO = "1.0.0" (única fonte da versão)
│       ├── modelos.py         # Classes de dados: Pessoa, Dupla, FimDeSemana, Escala
│       ├── armazenamento.py   # Ler/salvar JSON, backups
│       ├── gerador.py         # ALGORITMO que monta a escala (coração do projeto)
│       ├── exportar.py        # Exportar para Excel / texto para WhatsApp
│       ├── atualizador.py     # Verifica e baixa atualizações do GitHub
│       └── interface/
│           ├── __init__.py
│           ├── janela_principal.py
│           ├── tela_pessoas.py      # Cadastro da equipe
│           ├── tela_folgas.py       # Indisponibilidades (férias, etc.)
│           ├── tela_escala.py       # Gerar / visualizar / editar escala
│           └── componentes.py       # Botões e widgets reutilizáveis
├── tests/
│   ├── test_versao.py
│   ├── test_gerador.py
│   └── test_armazenamento.py
├── docs/
│   ├── DIARIO_DE_APRENDIZADO.md
│   └── MANUAL_DO_USUARIO.md   # Manual simples, com prints, para o usuário final
└── .github/
    └── workflows/
        └── release.yml        # Build do .exe e publicação da Release
```

**Separação importante (conceito: separação de responsabilidades):**
`gerador.py`, `modelos.py` e `armazenamento.py` **não podem importar nada da interface**. Assim a lógica pode ser testada sem abrir janelas.

---

## 5. Modelo de dados

```python
Pessoa:
    id: int
    nome: str
    ativo: bool                  # permite "desligar" alguém sem apagar o histórico
    indisponibilidades: list[date]   # datas (sábados) em que não pode trabalhar
    restricoes_dupla: list[int]  # ids de pessoas com quem NÃO deve fazer dupla (opcional)

Dupla:
    pessoa_a: int
    pessoa_b: int

FimDeSemana:
    data_sabado: date
    duplas: list[Dupla]          # 8 duplas

Escala:
    fins_de_semana: list[FimDeSemana]
    gerada_em: datetime
```

### Arquivo de dados
- Local: `%APPDATA%/PlanejadorEscala/dados.json` (NÃO salvar ao lado do `.exe`, pois a atualização substitui o `.exe`).
- Backup automático a cada salvamento em `%APPDATA%/PlanejadorEscala/backups/` (manter os últimos 10).
- Incluir campo `"versao_dados": 1` no JSON para permitir migrações futuras.

---

## 6. Algoritmo de geração da escala (`gerador.py`)

### Regras
**Obrigatórias (nunca violar):**
1. Cada fim de semana tem exatamente N duplas (padrão 8 = 16 pessoas).
2. Ninguém aparece duas vezes no mesmo fim de semana.
3. Ninguém é escalado em data marcada como indisponível.
4. Restrições de dupla são respeitadas.

**Desejáveis (otimizar):**
5. **Equilíbrio**: diferença de plantões entre quem mais e quem menos trabalhou ≤ 1.
6. **Descanso**: evitar a mesma pessoa em fins de semana seguidos (com 16 de 28 trabalhando, isso nem sempre será possível — minimizar).
7. **Variedade**: evitar repetir a mesma dupla com frequência.

### Abordagem: algoritmo guloso com pontuação (greedy)
Para cada fim de semana, em ordem:
1. Liste pessoas disponíveis.
2. Ordene por prioridade: **menos plantões feitos** primeiro; desempate por **mais tempo desde o último plantão**; desempate final aleatório.
3. Escolha as 16 primeiras.
4. Forme as duplas minimizando repetições: para cada par possível, custo = nº de vezes que já trabalharam juntos; escolha os pares de menor custo (respeitando restrições).
5. Atualize os contadores e siga para o próximo fim de semana.

Considerar o **histórico** (escalas anteriores salvas) ao gerar novas, para a justiça continuar ao longo dos meses.

Usar `random.seed` configurável nos testes para resultados reproduzíveis.

> Evolução futura (bom exercício de faculdade): comparar com *backtracking* ou com a biblioteca OR-Tools (programação por restrições).

### Testes mínimos (`tests/test_gerador.py`)
- Cada fim de semana tem 8 duplas e 16 pessoas distintas.
- Indisponibilidades respeitadas.
- Após 7 fins de semana (7 × 16 = 112 = 28 × 4), todos trabalharam exatamente 4 vezes.
- Erro amigável quando houver menos de 16 pessoas disponíveis.

---

## 7. Interface (UX para usuário leigo)

Princípios:
- Janela única com **3 abas grandes**: **👥 Equipe**, **📅 Folgas**, **📋 Escala**.
- Botões grandes, fonte ≥ 14, textos em português simples ("Gerar escala", não "Executar algoritmo").
- Toda ação destrutiva pede confirmação ("Tem certeza que deseja remover Fulano?").
- Mensagens de erro humanas: ❌ `KeyError: 12` → ✅ "Não há pessoas suficientes disponíveis no dia 14/11."
- Salvamento **automático** (o usuário não precisa lembrar de salvar).

Telas:
1. **Equipe**: lista de nomes, botões "Adicionar", "Editar", "Remover/Desativar".
2. **Folgas**: escolher pessoa → marcar datas em que não pode.
3. **Escala**: escolher mês (ou data inicial + quantidade de fins de semana) → botão **"Gerar escala"** → tabela com o resultado → permitir trocar pessoas manualmente → botões **"Exportar para Excel"** e **"Copiar para WhatsApp"**.
4. Rodapé: versão do programa e aviso de atualização quando houver.

---

## 8. Sistema de atualização (`atualizador.py`)

Fluxo usando **GitHub Releases**:

```
Programa abre
   └─> (em segundo plano) GET https://api.github.com/repos/<usuario>/<repo>/releases/latest
         └─> compara tag_name (ex.: "v1.2.0") com VERSAO local
               ├─ igual/menor → nada acontece
               └─ maior → mostra: "Nova versão disponível! Deseja atualizar agora?"
                     └─ Sim → baixa o .exe da Release para pasta temporária
                             → cria um pequeno script .bat que:
                                  1. espera o programa fechar
                                  2. substitui o .exe antigo pelo novo
                                  3. abre o programa novamente
                             → fecha o programa
```

Detalhes:
- Repositório **público** (a API funciona sem token). Nunca colocar tokens no código.
- Sem internet → falhar silenciosamente (não incomodar o usuário).
- Verificação em *thread* separada para não travar a janela (explicar o conceito de *threads* ao implementar).
- Versionamento semântico: `MAIOR.MENOR.CORREÇÃO` (explicar ao implementar).
- O arquivo de dados fica em `%APPDATA%`, então atualizar **não apaga** os dados.

### Como o desenvolvedor publica uma atualização
1. Altera o código e muda `VERSAO` em `versao.py`.
2. `git commit` e `git push`.
3. `git tag v1.2.0` e `git push --tags`.
4. O GitHub Actions (`release.yml`) roda os testes, gera o `.exe` com PyInstaller e cria a Release com o `.exe` anexado.
5. Os usuários recebem o aviso na próxima vez que abrirem o programa.

> Aviso: o Windows SmartScreen pode alertar "aplicativo não reconhecido" em `.exe` sem assinatura digital. Documentar no manual do usuário: "Mais informações → Executar assim mesmo".

---

## 9. Roteiro de desenvolvimento (fases)

Implementar **uma fase por vez**, com explicação didática ao final de cada uma.

| Fase | Entrega | Conceitos que o desenvolvedor aprende |
|---|---|---|
| 0 | Ambiente: Python, venv, Git, estrutura de pastas, `requirements.txt` | Ambientes virtuais, gerenciador de pacotes, controle de versão |
| 1 | `modelos.py` + `armazenamento.py` + testes | Classes, `dataclasses`, JSON, leitura/escrita de arquivos |
| 2 | `gerador.py` + testes (sem interface) | Algoritmos gulosos, ordenação, conjuntos, testes automatizados |
| 3 | Interface: aba Equipe | GUI, eventos, *callbacks* |
| 4 | Interface: abas Folgas e Escala | Componentes, integração lógica ↔ interface |
| 5 | Exportar Excel e texto para WhatsApp | Bibliotecas externas, formatação de strings |
| 6 | Gerar `.exe` com PyInstaller (manual) | Empacotamento, distribuição |
| 7 | `atualizador.py` | HTTP, APIs REST, *threads*, versionamento |
| 8 | GitHub Actions para Releases automáticas | CI/CD |
| 9 | Manual do usuário + polimento | Documentação, UX |

---

## 10. Comandos úteis (referência)

```powershell
# Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instalar dependências (desenvolvimento inclui as do programa)
pip install -r requirements-dev.txt

# Rodar o programa
python -m src.escala.main

# Rodar testes
pytest

# Gerar o .exe
pyinstaller --onefile --windowed --name "PlanejadorEscala" src/escala/main.py
```

---

## 11. Perguntas em aberto (confirmar com o desenvolvedor antes de implementar)

1. As 8 duplas têm funções/postos diferentes (ex.: sábado manhã, sábado noite, domingo...) ou são todas equivalentes?
2. A dupla trabalha o fim de semana inteiro ou só um dia?
3. Existem pessoas que **sempre** devem ou **nunca** podem trabalhar juntas?
4. Existe alguma regra de experiência (ex.: cada dupla precisa de pelo menos 1 pessoa experiente)?
5. Feriados devem entrar na escala?
6. Qual o período típico gerado de uma vez: um mês, um trimestre?
7. Como a escala é divulgada hoje (Excel, PDF, WhatsApp, impresso)?
