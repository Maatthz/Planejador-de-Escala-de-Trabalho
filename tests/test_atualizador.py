"""Testes do módulo de atualização automática (atualizador.py).

Todos os testes rodam 100% offline usando monkeypatch para simular respostas HTTP,
sistema de arquivos e execução em segundo plano.
"""

import hashlib
from pathlib import Path
import sys
import threading

import pytest
import requests

import src.escala.atualizador as atualizador
from src.escala.atualizador import (
    ErroAtualizacao,
    InfoAtualizacao,
    NOME_DO_EXE,
    baixar_e_verificar,
    buscar_atualizacao,
    calcular_sha256,
    comparar_versoes,
    instalar_e_reiniciar,
    programa_esta_empacotado,
    verificar_em_segundo_plano,
)


class _RespostaFalsa:
    """Simula um objeto Response da biblioteca requests."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: dict | None = None,
        text: str = "",
        content: bytes = b"",
    ) -> None:
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
        self.content = content

    def json(self) -> dict:
        return self._json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def test_comparar_versoes() -> None:
    """Compara versões semânticas com e sem prefixo 'v', incluindo números de 2 dígitos."""
    assert comparar_versoes("v1.10.0", "1.9.9") == 1
    assert comparar_versoes("1.9.9", "v1.10.0") == -1
    assert comparar_versoes("v0.1.0", "0.1.0") == 0
    assert comparar_versoes("2.0.0", "1.99.99") == 1
    assert comparar_versoes("0.1.1", "0.1.0") == 1


def test_programa_esta_empacotado(monkeypatch: pytest.MonkeyPatch) -> None:
    """Detecta corretamente a flag sys.frozen definida pelo PyInstaller."""
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert programa_esta_empacotado() is False

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert programa_esta_empacotado() is True


def test_buscar_atualizacao_repositorio_vazio(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sem repositório configurado, deve retornar None sem fazer requisição de rede."""
    monkeypatch.setattr(atualizador, "REPOSITORIO_GITHUB", "")
    monkeypatch.setattr(atualizador._modulo_versao, "REPOSITORIO_GITHUB", "")

    chamou_rede = False

    def _get_proibido(*args, **kwargs):
        nonlocal chamou_rede
        chamou_rede = True
        raise AssertionError("Não deveria chamar requests.get com repositório vazio")

    monkeypatch.setattr(requests, "get", _get_proibido)
    assert buscar_atualizacao("0.1.0") is None
    assert chamou_rede is False


def test_buscar_atualizacao_erro_rede(monkeypatch: pytest.MonkeyPatch) -> None:
    """Qualquer falha de conexão ou timeout deve retornar None silenciosamente."""
    monkeypatch.setattr(atualizador, "REPOSITORIO_GITHUB", "usuario/planejador")

    def _get_falha(*args, **kwargs):
        raise requests.ConnectionError("Sem conexão com a internet")

    monkeypatch.setattr(requests, "get", _get_falha)
    assert buscar_atualizacao("0.1.0") is None


def test_buscar_atualizacao_encontra_nova_versao(monkeypatch: pytest.MonkeyPatch) -> None:
    """Retorna InfoAtualizacao quando a tag da Release é maior que a versão atual."""
    monkeypatch.setattr(atualizador, "REPOSITORIO_GITHUB", "usuario/planejador")

    payload = {
        "tag_name": "v0.2.0",
        "body": "Correções e melhorias.",
        "assets": [
            {
                "name": NOME_DO_EXE,
                "browser_download_url": "https://github.com/usuario/planejador/releases/download/v0.2.0/PlanejadorEscala.exe",
            },
            {
                "name": f"{NOME_DO_EXE}.sha256",
                "browser_download_url": "https://github.com/usuario/planejador/releases/download/v0.2.0/PlanejadorEscala.exe.sha256",
            },
        ],
    }
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _RespostaFalsa(200, json_data=payload))

    info = buscar_atualizacao(versao_atual="0.1.0")
    assert info is not None
    assert info.versao == "0.2.0"
    assert info.url_exe.endswith("PlanejadorEscala.exe")
    assert info.url_hash.endswith("PlanejadorEscala.exe.sha256")
    assert info.notas == "Correções e melhorias."

    # Se a versão atual já for igual ou superior, retorna None
    assert buscar_atualizacao(versao_atual="0.2.0") is None
    assert buscar_atualizacao(versao_atual="0.3.0") is None


def test_baixar_e_verificar_sucesso(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Baixa o .exe, confere o SHA-256 correto e mantém o arquivo na pasta de destino."""
    conteudo_exe = b"MZ-binario-simulado-do-planejador-de-escala"
    hash_correto = hashlib.sha256(conteudo_exe).hexdigest()

    info = InfoAtualizacao(
        versao="0.2.0",
        url_exe="https://exemplo.com/PlanejadorEscala.exe",
        url_hash="https://exemplo.com/PlanejadorEscala.exe.sha256",
        notas="",
    )

    def _get_simulado(url: str, **kwargs):
        if url.endswith(".sha256"):
            return _RespostaFalsa(200, text=f"{hash_correto}\n")
        return _RespostaFalsa(200, content=conteudo_exe)

    monkeypatch.setattr(requests, "get", _get_simulado)

    caminho = baixar_e_verificar(info, tmp_path)
    assert caminho.exists()
    assert caminho.read_bytes() == conteudo_exe
    assert calcular_sha256(caminho) == hash_correto


def test_baixar_e_verificar_sha256_diferente_apaga_arquivo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Se o SHA-256 não bater, deve apagar imediatamente o .exe baixado e levantar ErroAtualizacao."""
    conteudo_adulterado = b"binario-corrompido-ou-adulterado"
    hash_esperado = "a" * 64

    info = InfoAtualizacao(
        versao="0.2.0",
        url_exe="https://exemplo.com/PlanejadorEscala.exe",
        url_hash="https://exemplo.com/PlanejadorEscala.exe.sha256",
        notas="",
    )

    def _get_simulado(url: str, **kwargs):
        if url.endswith(".sha256"):
            return _RespostaFalsa(200, text=hash_esperado)
        return _RespostaFalsa(200, content=conteudo_adulterado)

    monkeypatch.setattr(requests, "get", _get_simulado)

    with pytest.raises(ErroAtualizacao):
        baixar_e_verificar(info, tmp_path)

    assert not (tmp_path / NOME_DO_EXE).exists()


def test_instalar_e_reiniciar_cria_script_e_checa_permissao(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verifica criação do script .bat de substituição e mensagem amigável sem permissão."""
    exe_atual_falso = tmp_path / "instalado" / NOME_DO_EXE
    exe_atual_falso.parent.mkdir(parents=True)
    exe_atual_falso.write_bytes(b"versao_antiga")

    novo_exe = tmp_path / "temp" / NOME_DO_EXE
    novo_exe.parent.mkdir(parents=True)
    novo_exe.write_bytes(b"versao_nova")

    monkeypatch.setattr(sys, "executable", str(exe_atual_falso))

    comandos_executados: list[list[str]] = []
    monkeypatch.setattr(
        atualizador.subprocess,
        "Popen",
        lambda cmd, **kw: comandos_executados.append(cmd),
    )
    monkeypatch.setattr(
        sys,
        "exit",
        lambda codigo=0: (_ for _ in ()).throw(SystemExit(codigo)),
    )

    with pytest.raises(SystemExit):
        instalar_e_reiniciar(novo_exe)

    bat_criado = novo_exe.parent / "atualizar_escala.bat"
    assert bat_criado.exists()
    assert str(exe_atual_falso) in bat_criado.read_text(encoding="utf-8")
    assert len(comandos_executados) == 1


def test_instalar_e_reiniciar_sem_permissao_escrita(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sem permissão de escrita na pasta do .exe, orienta mover para Documentos ou Área de Trabalho."""
    novo_exe = tmp_path / NOME_DO_EXE
    novo_exe.write_bytes(b"novo")

    def _negar_permissao(pasta: Path) -> None:
        raise ErroAtualizacao(
            "Mova o programa para a pasta Documentos ou Área de Trabalho para receber atualizações."
        )

    monkeypatch.setattr(atualizador, "_verificar_permissao_escrita", _negar_permissao)

    with pytest.raises(ErroAtualizacao, match="Documentos ou Área de Trabalho"):
        instalar_e_reiniciar(novo_exe)


def test_verificar_em_segundo_plano_chama_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A verificação roda em uma thread separada e aciona o callback quando encontra versão nova."""
    esperada = InfoAtualizacao(
        versao="1.0.0",
        url_exe="https://exemplo.com/PlanejadorEscala.exe",
        url_hash="https://exemplo.com/PlanejadorEscala.exe.sha256",
        notas="Lançamento 1.0",
    )
    monkeypatch.setattr(atualizador, "buscar_atualizacao", lambda: esperada)

    evento = threading.Event()
    recebido: list[InfoAtualizacao] = []

    def _ao_encontrar(info: InfoAtualizacao) -> None:
        recebido.append(info)
        evento.set()

    verificar_em_segundo_plano(_ao_encontrar)
    assert evento.wait(timeout=2.0) is True
    assert recebido == [esperada]
