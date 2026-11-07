"""Armazenamento e persistência de dados em JSON.

Garante gravação atômica, rotação de até 10 backups automáticos,
recuperação transparente em caso de corrupção e funções para cópias manuais.
"""

from datetime import date, datetime
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import shutil

from src.escala.modelos import (
    Configuracao,
    DadosDoPrograma,
    Dupla,
    ErroEscala,
    Feriado,
    ModeloDeTurno,
    PERIODOS_PADRAO,
    Pessoa,
    Plantao,
    Escala,
)

VERSAO_DADOS: int = 1
QTD_BACKUPS: int = 10


def pasta_de_dados() -> Path:
    """Pasta dos dados (%APPDATA%/PlanejadorEscala ou PLANEJADOR_PASTA_DADOS). Cria se não existir."""
    variavel_ambiente = os.getenv("PLANEJADOR_PASTA_DADOS")
    if variavel_ambiente:
        pasta = Path(variavel_ambiente)
    else:
        appdata = os.getenv("APPDATA")
        base = Path(appdata) if appdata else Path.home()
        pasta = base / "PlanejadorEscala"

    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _obter_logger(pasta: Path) -> logging.Logger:
    """Configura e retorna o logger com arquivo registro.log na pasta de dados."""
    logger = logging.getLogger("escala.armazenamento")
    if not logger.handlers:
        arquivo_log = pasta / "registro.log"
        handler = RotatingFileHandler(
            arquivo_log, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def migrar(bruto: dict) -> dict:
    """Atualiza dados de versões antigas para VERSAO_DADOS (hoje não faz nada além de validar)."""
    if not isinstance(bruto, dict):
        raise ValueError("Estrutura de dados inválida.")
    versao = bruto.get("versao_dados")
    if versao is None:
        raise ValueError("Arquivo sem versão de dados informada.")
    if versao > VERSAO_DADOS:
        raise ValueError(
            f"Versão dos dados ({versao}) é mais recente que a versão suportada ({VERSAO_DADOS})."
        )
    return bruto


def dados_para_dict(dados: DadosDoPrograma) -> dict:
    """Converte os objetos em dicionário pronto para JSON (serialização)."""
    return {
        "versao_dados": VERSAO_DADOS,
        "proximo_id": dados.proximo_id,
        "pessoas": [
            {
                "id": p.id,
                "nome": p.nome,
                "experiente": p.experiente,
                "ativo": p.ativo,
                "data_entrada": p.data_entrada.isoformat(),
                "indisponibilidades": sorted(d.isoformat() for d in p.indisponibilidades),
                "ajuste_plantoes": p.ajuste_plantoes,
                "ajuste_feriados": p.ajuste_feriados,
                "ultimo_plantao_manual": (
                    p.ultimo_plantao_manual.isoformat()
                    if p.ultimo_plantao_manual is not None
                    else None
                ),
            }
            for p in dados.pessoas
        ],
        "configuracao": {
            "turnos": [
                {
                    "dia_da_semana": t.dia_da_semana,
                    "periodo": t.periodo,
                    "qtd_duplas": t.qtd_duplas,
                }
                for t in dados.configuracao.turnos
            ],
            "periodos": list(dados.configuracao.periodos),
            "feriados_ativos": dados.configuracao.feriados_ativos,
            "feriado_periodos_padrao": dict(dados.configuracao.feriado_periodos_padrao),
            "modo_experiencia": dados.configuracao.modo_experiencia,
            "semanas_por_geracao": dados.configuracao.semanas_por_geracao,
            "titulo_mensagem": dados.configuracao.titulo_mensagem,
            "texto_final_mensagem": dados.configuracao.texto_final_mensagem,
            "evitar_semanas_seguidas": dados.configuracao.evitar_semanas_seguidas,
            "compensar_ausencias": dados.configuracao.compensar_ausencias,
            "nunca_juntos": [list(par) for par in dados.configuracao.nunca_juntos],
            "sempre_juntos": [list(par) for par in dados.configuracao.sempre_juntos],
        },
        "feriados": [
            {
                "data": f.data.isoformat(),
                "nome": f.nome,
                "periodos": dict(f.periodos),
            }
            for f in dados.feriados
        ],
        "rascunho": _escala_para_dict(dados.rascunho) if dados.rascunho else None,
        "escalas": [_escala_para_dict(e) for e in dados.escalas],
    }


def _escala_para_dict(escala: Escala) -> dict:
    """Converte um objeto Escala em dicionário serializável."""
    return {
        "gerada_em": escala.gerada_em.isoformat(),
        "confirmada": escala.confirmada,
        "plantoes": [
            {
                "data": p.data.isoformat(),
                "periodo": p.periodo,
                "qtd_duplas": p.qtd_duplas,
                "eh_feriado": p.eh_feriado,
                "nome_feriado": p.nome_feriado,
                "duplas": [[d.pessoa_a, d.pessoa_b] for d in p.duplas],
            }
            for p in escala.plantoes
        ],
    }


def dados_de_dict(bruto: dict) -> DadosDoPrograma:
    """Converte o dicionário lido do JSON em objetos (desserialização). Aplica `migrar` antes."""
    valido = migrar(bruto)

    pessoas = [
        Pessoa(
            id=p["id"],
            nome=p["nome"],
            experiente=p.get("experiente", False),
            ativo=p.get("ativo", True),
            data_entrada=date.fromisoformat(p["data_entrada"]),
            indisponibilidades={
                date.fromisoformat(d) for d in p.get("indisponibilidades", [])
            },
            ajuste_plantoes=int(p.get("ajuste_plantoes", 0)),
            ajuste_feriados=int(p.get("ajuste_feriados", 0)),
            ultimo_plantao_manual=(
                date.fromisoformat(p["ultimo_plantao_manual"])
                if p.get("ultimo_plantao_manual")
                else None
            ),
        )
        for p in valido.get("pessoas", [])
    ]

    cfg = valido.get("configuracao", {})
    configuracao = Configuracao(
        turnos=[
            ModeloDeTurno(t["dia_da_semana"], t["periodo"], t["qtd_duplas"])
            for t in cfg.get("turnos", [])
        ],
        periodos=list(cfg.get("periodos", PERIODOS_PADRAO)),
        feriados_ativos=cfg.get("feriados_ativos", True),
        feriado_periodos_padrao=dict(cfg.get("feriado_periodos_padrao", {"manhã": 4})),
        modo_experiencia=cfg.get("modo_experiencia", "preferencia"),
        semanas_por_geracao=cfg.get("semanas_por_geracao", 1),
        titulo_mensagem=cfg.get("titulo_mensagem", "📋 *ESCALA DE PLANTÃO*"),
        texto_final_mensagem=cfg.get("texto_final_mensagem", ""),
        evitar_semanas_seguidas=cfg.get("evitar_semanas_seguidas", True),
        compensar_ausencias=cfg.get("compensar_ausencias", False),
        nunca_juntos=[tuple(par) for par in cfg.get("nunca_juntos", [])],
        sempre_juntos=[tuple(par) for par in cfg.get("sempre_juntos", [])],
    )

    feriados = [
        Feriado(
            data=date.fromisoformat(f["data"]),
            nome=f.get("nome", ""),
            periodos=dict(f.get("periodos", {"manhã": 4})),
        )
        for f in valido.get("feriados", [])
    ]

    rascunho = _escala_de_dict(valido["rascunho"]) if valido.get("rascunho") else None
    escalas = [_escala_de_dict(e) for e in valido.get("escalas", [])]

    return DadosDoPrograma(
        pessoas=pessoas,
        configuracao=configuracao,
        feriados=feriados,
        escalas=escalas,
        rascunho=rascunho,
        proximo_id=valido.get("proximo_id", 1),
    )


def _escala_de_dict(bruto_escala: dict) -> Escala:
    """Converte um dicionário em objeto Escala."""
    plantoes: list[Plantao] = []
    for p in bruto_escala.get("plantoes", []):
        duplas = [Dupla(d[0], d[1]) for d in p.get("duplas", [])]
        plantoes.append(
            Plantao(
                data=date.fromisoformat(p["data"]),
                periodo=p["periodo"],
                qtd_duplas=p["qtd_duplas"],
                eh_feriado=p.get("eh_feriado", False),
                nome_feriado=p.get("nome_feriado", ""),
                duplas=duplas,
            )
        )
    return Escala(
        plantoes=plantoes,
        gerada_em=datetime.fromisoformat(bruto_escala["gerada_em"]),
        confirmada=bruto_escala.get("confirmada", False),
    )


def _gravar_arquivo_atomico(caminho_destino: Path, conteudo_dict: dict) -> None:
    """Serializa para JSON e salva no arquivo destino usando substituição atômica."""
    caminho_tmp = caminho_destino.with_suffix(".tmp")
    texto = json.dumps(conteudo_dict, indent=2, ensure_ascii=False)
    with caminho_tmp.open("w", encoding="utf-8") as f:
        f.write(texto)
    os.replace(caminho_tmp, caminho_destino)


def _limpar_backups_antigos(pasta_backups: Path) -> None:
    """Mantém apenas os QTD_BACKUPS backups mais recentes e apaga os excedentes."""
    backups = sorted(
        pasta_backups.glob("dados_*.json"),
        key=lambda p: (p.stat().st_mtime, p.name),
        reverse=True,
    )
    if len(backups) > QTD_BACKUPS:
        for backup_antigo in backups[QTD_BACKUPS:]:
            try:
                backup_antigo.unlink()
            except OSError:
                pass


def salvar(dados: DadosDoPrograma, pasta: Path | None = None) -> None:
    """Faz backup do arquivo atual, grava de forma atômica e limpa backups antigos."""
    pasta_destino = pasta if pasta is not None else pasta_de_dados()
    pasta_destino.mkdir(parents=True, exist_ok=True)
    caminho_dados = pasta_destino / "dados.json"

    if caminho_dados.exists():
        pasta_backups = pasta_destino / "backups"
        pasta_backups.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_backup = pasta_backups / f"dados_{timestamp}.json"
        contador = 1
        while caminho_backup.exists():
            caminho_backup = pasta_backups / f"dados_{timestamp}_{contador}.json"
            contador += 1

        shutil.copy2(caminho_dados, caminho_backup)
        _limpar_backups_antigos(pasta_backups)

    _gravar_arquivo_atomico(caminho_dados, dados_para_dict(dados))


def _tentar_recuperar_backup(pasta: Path, logger: logging.Logger) -> tuple[DadosDoPrograma, str]:
    """Tenta restaurar o backup mais recente em caso de falha no arquivo principal."""
    pasta_backups = pasta / "backups"
    if pasta_backups.exists():
        backups = sorted(
            pasta_backups.glob("dados_*.json"),
            key=lambda p: (p.stat().st_mtime, p.name),
            reverse=True,
        )
        for backup in backups:
            try:
                with backup.open("r", encoding="utf-8") as f:
                    bruto_bkp = json.load(f)
                dados_recuperados = dados_de_dict(bruto_bkp)
                _gravar_arquivo_atomico(pasta / "dados.json", dados_para_dict(dados_recuperados))
                aviso = (
                    f"O arquivo principal de dados estava corrompido. "
                    f"Os dados foram recuperados com sucesso do backup '{backup.name}'."
                )
                return dados_recuperados, aviso
            except Exception as erro_bkp:
                logger.warning("Backup %s também estava inválido: %s", backup.name, erro_bkp)

    aviso = (
        "O arquivo de dados estava corrompido e nenhum backup válido foi encontrado. "
        "Um novo arquivo padrão foi criado."
    )
    return DadosDoPrograma(), aviso


def carregar(pasta: Path | None = None) -> tuple[DadosDoPrograma, str | None]:
    """Lê os dados. Retorna (dados, aviso). Arquivo inexistente -> dados padrão.

    Arquivo corrompido -> restaura o backup válido mais recente e devolve um aviso amigável.
    """
    pasta_origem = pasta if pasta is not None else pasta_de_dados()
    caminho = pasta_origem / "dados.json"

    if not caminho.exists():
        return DadosDoPrograma(), None

    try:
        with caminho.open("r", encoding="utf-8") as f:
            bruto = json.load(f)
        return dados_de_dict(bruto), None
    except Exception as erro:
        logger = _obter_logger(pasta_origem)
        logger.error("Falha ao carregar arquivo de dados %s: %s", caminho, erro)
        dados_recuperados, aviso = _tentar_recuperar_backup(pasta_origem, logger)
        return dados_recuperados, aviso


def exportar_copia(dados: DadosDoPrograma, destino: Path) -> None:
    """Backup manual: grava todos os dados no arquivo escolhido pelo usuário."""
    try:
        conteudo = json.dumps(dados_para_dict(dados), indent=2, ensure_ascii=False)
        destino.parent.mkdir(parents=True, exist_ok=True)
        caminho_tmp = destino.with_suffix(".tmp")
        with caminho_tmp.open("w", encoding="utf-8") as f:
            f.write(conteudo)
        os.replace(caminho_tmp, destino)
    except Exception as erro:
        raise ErroEscala(f"Não foi possível salvar a cópia de segurança: {erro}")


def importar_copia(origem: Path) -> DadosDoPrograma:
    """Lê uma cópia manual. Levanta ErroEscala se o arquivo não for uma cópia válida."""
    if not origem.exists():
        raise ErroEscala(f"O arquivo de cópia de segurança não foi encontrado: '{origem.name}'.")
    try:
        with origem.open("r", encoding="utf-8") as f:
            bruto = json.load(f)
        if not isinstance(bruto, dict) or "versao_dados" not in bruto:
            raise ErroEscala("O arquivo selecionado não é uma cópia de segurança válida.")
        return dados_de_dict(bruto)
    except ErroEscala:
        raise
    except Exception:
        raise ErroEscala("Não foi possível ler a cópia de segurança: arquivo corrompido ou formato inválido.")
