# Planejador de Escala de Plantão

Programa de desktop para montar a escala de plantão de fim de semana (duplas) de uma equipe.
Detalhes do projeto: veja [AGENTS.md](AGENTS.md).

## Como rodar (desenvolvedor)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

python -m src.escala.main   # abre o programa
pytest                      # roda os testes
```

> Se o PowerShell bloquear o `Activate.ps1`, rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
