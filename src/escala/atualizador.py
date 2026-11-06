"""Atualizador automático via GitHub Releases com verificação de integridade SHA-256.

Consulta silenciosamente se há uma versão mais nova publicada no GitHub,
baixa o novo executável, confere a assinatura SHA-256 e substitui o .exe via script .bat.
"""

from collections.abc import Callable
from dataclasses import dataclass
import hashlib
import logging
import os
from pathlib import Path
import subprocess
import sys
import threading

import requests

import src.escala.versao as _modulo_versao
from src.escala.versao import REPOSITORIO_GITHUB, VERSAO

NOME_DO_EXE: str = "PlanejadorEscala.exe"

logger = logging.getLogger("escala.atualizador")


class ErroAtualizacao(Exception):
    """Falha ao baixar ou verificar a atualização (nunca mostrada como traceback)."""


@dataclass
class InfoAtualizacao:
    """Metadados de uma nova versão disponível no GitHub Releases."""

    versao: str
    url_exe: str
    url_hash: str
    notas: str


def _converter_versao(texto: str) -> tuple[int, ...]:
    """Extrai a tupla numérica de uma string de versão (ex.: 'v1.10.0' -> (1, 10, 0))."""
    limpo = texto.strip().lstrip("vV")
    if not limpo:
        return (0,)
    partes: list[int] = []
    for trecho in limpo.split("."):
        apenas_digitos = "".join(c for c in trecho if c.isdigit())
        partes.append(int(apenas_digitos) if apenas_digitos else 0)
    return tuple(partes)


def comparar_versoes(a: str, b: str) -> int:
    """-1 se a < b, 0 se iguais, 1 se a > b. Aceita prefixo 'v' ('v1.2.0')."""
    tupla_a = _converter_versao(a)
    tupla_b = _converter_versao(b)
    tamanho = max(len(tupla_a), len(tupla_b))
    norm_a = tupla_a + (0,) * (tamanho - len(tupla_a))
    norm_b = tupla_b + (0,) * (tamanho - len(tupla_b))

    if norm_a < norm_b:
        return -1
    if norm_a > norm_b:
        return 1
    return 0


def programa_esta_empacotado() -> bool:
    """True se rodando como .exe (sys.frozen). Rodando do código-fonte, não atualiza."""
    return bool(getattr(sys, "frozen", False))


def _extrair_urls_assets(assets: list[dict]) -> tuple[str, str]:
    """Localiza as URLs do .exe e do arquivo .sha256 na lista de assets da Release."""
    url_exe = ""
    url_hash = ""
    nome_hash = f"{NOME_DO_EXE}.sha256"

    for item in assets:
        nome = str(item.get("name", ""))
        url = str(item.get("browser_download_url", ""))
        if nome == NOME_DO_EXE:
            url_exe = url
        elif nome == nome_hash:
            url_hash = url

    return url_exe, url_hash


def buscar_atualizacao(
    versao_atual: str = VERSAO,
    tempo_limite: float = 5.0,
) -> InfoAtualizacao | None:
    """Consulta a última Release. Sem internet, sem repositório configurado ou qualquer erro -> None (silencioso)."""
    repositorio = (REPOSITORIO_GITHUB or _modulo_versao.REPOSITORIO_GITHUB).strip()
    if not repositorio:
        return None

    url = f"https://api.github.com/repos/{repositorio}/releases/latest"
    try:
        resposta = requests.get(
            url,
            timeout=tempo_limite,
            headers={"Accept": "application/vnd.github+json"},
        )
        if resposta.status_code != 200:
            return None

        dados = resposta.json()
        tag = str(dados.get("tag_name", "")).strip()
        if not tag or comparar_versoes(tag, versao_atual) <= 0:
            return None

        url_exe, url_hash = _extrair_urls_assets(dados.get("assets", []))
        if not (url_exe.startswith("https://") and url_hash.startswith("https://")):
            return None

        return InfoAtualizacao(
            versao=tag.lstrip("vV"),
            url_exe=url_exe,
            url_hash=url_hash,
            notas=str(dados.get("body") or ""),
        )
    except Exception as erro:
        logger.debug("Não foi possível verificar atualizações: %s", erro)
        return None


def calcular_sha256(caminho: Path) -> str:
    """Hash SHA-256 do arquivo em hexadecimal (lendo em blocos)."""
    resumo = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(65536):
            resumo.update(bloco)
    return resumo.hexdigest().lower()


def baixar_e_verificar(info: InfoAtualizacao, pasta_destino: Path) -> Path:
    """Baixa o .exe e o .sha256; compara os hashes. Diferente -> apaga o arquivo e levanta ErroAtualizacao."""
    if not (info.url_exe.startswith("https://") and info.url_hash.startswith("https://")):
        raise ErroAtualizacao("Endereço de atualização inseguro (HTTPS obrigatório).")

    pasta_destino.mkdir(parents=True, exist_ok=True)
    caminho_exe = pasta_destino / NOME_DO_EXE

    try:
        resp_hash = requests.get(info.url_hash, timeout=15.0)
        resp_hash.raise_for_status()
        partes_hash = resp_hash.text.strip().split()
        if not partes_hash:
            raise ErroAtualizacao("Arquivo de verificação SHA-256 vazio.")
        hash_esperado = partes_hash[0].lower()

        resp_exe = requests.get(info.url_exe, timeout=60.0)
        resp_exe.raise_for_status()
        caminho_exe.write_bytes(resp_exe.content)
    except ErroAtualizacao:
        caminho_exe.unlink(missing_ok=True)
        raise
    except Exception as erro:
        caminho_exe.unlink(missing_ok=True)
        logger.warning("Falha no download da atualização: %s", erro)
        raise ErroAtualizacao(
            "Não foi possível baixar a atualização. Verifique sua conexão com a internet."
        ) from erro

    hash_real = calcular_sha256(caminho_exe)
    if hash_real != hash_esperado:
        caminho_exe.unlink(missing_ok=True)
        logger.error(
            "SHA-256 inválido para %s: esperado=%s, obtido=%s",
            caminho_exe,
            hash_esperado,
            hash_real,
        )
        raise ErroAtualizacao(
            "O arquivo baixado falhou na verificação de segurança (SHA-256 inválido) e foi descartado."
        )

    return caminho_exe


def _verificar_permissao_escrita(pasta: Path) -> None:
    """Garante que o programa tem permissão de escrita na pasta onde o .exe está."""
    arquivo_teste = pasta / f".teste_permissao_{os.getpid()}.tmp"
    try:
        arquivo_teste.write_text("ok", encoding="utf-8")
        arquivo_teste.unlink(missing_ok=True)
    except OSError as erro:
        raise ErroAtualizacao(
            "Mova o programa para a pasta Documentos ou Área de Trabalho para receber atualizações."
        ) from erro


def instalar_e_reiniciar(novo_exe: Path) -> None:
    """Cria um .bat que espera o programa fechar, substitui o .exe, reabre e se apaga; executa e encerra."""
    exe_atual = Path(sys.executable).resolve()
    _verificar_permissao_escrita(exe_atual.parent)

    caminho_bat = novo_exe.parent / "atualizar_escala.bat"
    conteudo_bat = (
        "@echo off\r\n"
        "chcp 65001 >nul\r\n"
        "timeout /t 2 /nobreak >nul\r\n"
        f'move /y "{novo_exe.resolve()}" "{exe_atual}" >nul\r\n'
        f'start "" "{exe_atual}"\r\n'
        'del "%~f0"\r\n'
    )
    caminho_bat.write_text(conteudo_bat, encoding="utf-8")

    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(["cmd.exe", "/c", str(caminho_bat)], creationflags=flags)
    sys.exit(0)


def verificar_em_segundo_plano(ao_encontrar: Callable[[InfoAtualizacao], None]) -> None:
    """Roda buscar_atualizacao numa thread daemon e chama `ao_encontrar` se houver versão nova."""
    def _tarefa() -> None:
        info = buscar_atualizacao()
        if info is not None:
            ao_encontrar(info)

    thread = threading.Thread(target=_tarefa, daemon=True)
    thread.start()
