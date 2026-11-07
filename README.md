# 📋 Planejador de Escala de Plantão

Aplicação desktop para Windows (Python 3.12+ e CustomTkinter) que monta, valida e exporta para o WhatsApp a escala de plantão de fim de semana e feriados de uma equipe em duplas, com equilíbrio automático de carga, controle de folgas/férias e atualização automática via GitHub Releases.

- 📖 **Para quem vai usar o programa:** leia o [Manual do Usuário](docs/MANUAL_DO_USUARIO.md).
- 📓 **Histórico técnico e decisões do projeto:** veja o [Diário de Aprendizado](docs/DIARIO_DE_APRENDIZADO.md).

---

## 🛠️ Como rodar em desenvolvimento

No PowerShell, na pasta raiz do projeto:

```powershell
# 1. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Instalar dependências de execução e desenvolvimento
pip install -r requirements-dev.txt

# 3. Abrir o programa
python -m src.escala.main

# 4. Rodar a suíte de testes automatizados
pytest
```

> **Dica:** se o PowerShell bloquear o `Activate.ps1`, execute uma única vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## 📦 Como gerar o executável (`.exe`) manualmente

Para empacotar o programa em um único arquivo `dist\PlanejadorEscala.exe` (que roda em qualquer Windows 10/11 sem precisar de Python instalado):

```powershell
pyinstaller --noconfirm --onefile --windowed --name PlanejadorEscala --collect-data customtkinter iniciar.py
```

---

## 🚀 Como publicar uma nova versão (GitHub Releases + Auto-Update)

O repositório conta com integração e entrega contínuas (`.github/workflows/testes.yml` e `.github/workflows/release.yml`):

1. Altere o número da versão em [`src/escala/versao.py`](src/escala/versao.py) seguindo o formato `MAIOR.MENOR.CORREÇÃO` (ex.: `VERSAO: str = "0.2.0"`).
2. Faça o commit e envie para a branch `main` (pelo GitHub Desktop ou terminal).
3. Crie e envie uma *tag* com o prefixo `v` idêntico à `VERSAO`:
   ```powershell
   git tag v0.2.0
   git push --tags
   ```
4. O **GitHub Actions** rodará todos os testes, compilará o `PlanejadorEscala.exe`, gerará o arquivo de verificação `PlanejadorEscala.exe.sha256` e publicará a Release automaticamente. Na próxima vez que o usuário abrir o programa, ele receberá o aviso de atualização.

---

## 📂 Estrutura do projeto

```text
Planejador de Escala de Trabalho/
├── iniciar.py                   # Lançador usado pelo PyInstaller
├── requirements.txt             # Dependências de produção (customtkinter, requests)
├── requirements-dev.txt         # Dependências de dev (pytest, pyinstaller)
├── src/escala/
│   ├── main.py                  # Configuração de logging e inicialização da janela
│   ├── versao.py                # VERSAO e REPOSITORIO_GITHUB
│   ├── modelos.py               # Entidades de domínio (Pessoa, Plantao, Escala, Configuracao)
│   ├── datas.py                 # Utilitários de calendário e formatação em português
│   ├── armazenamento.py         # Persistência JSON atômica + rotação de 10 backups
│   ├── historico.py             # Cálculo de contadores e Quadro de Justiça
│   ├── gerador.py               # Algoritmo guloso de montagem da escala e duplas
│   ├── edicao.py                # Trocas manuais, validação de regras e confirmação
│   ├── exportar.py              # Formatação de mensagem para WhatsApp
│   ├── textos_ajuda.py          # Explicações e exemplos didáticos das configurações
│   ├── atualizador.py           # Atualização via GitHub Releases com validação SHA-256
│   └── interface/               # Camada visual em CustomTkinter (Design System Grafite)
├── tests/                       # Suíte de testes automatizados (pytest)
└── docs/
    ├── MANUAL_DO_USUARIO.md     # Guia passo a passo para o usuário final leigo
    └── DIARIO_DE_APRENDIZADO.md # Registro de decisões e conceitos de Ciência da Computação
```
