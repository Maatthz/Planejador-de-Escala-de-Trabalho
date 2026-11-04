"""Testes para o módulo de armazenamento e persistência."""

from datetime import date, datetime
import json
from pathlib import Path
import pytest

from src.escala.armazenamento import (
    QTD_BACKUPS,
    VERSAO_DADOS,
    carregar,
    dados_de_dict,
    dados_para_dict,
    exportar_copia,
    importar_copia,
    pasta_de_dados,
    salvar,
)
from src.escala.modelos import (
    Configuracao,
    DadosDoPrograma,
    Dupla,
    ErroEscala,
    Escala,
    Feriado,
    ModeloDeTurno,
    Pessoa,
    Plantao,
)


def test_pasta_de_dados_respeita_variavel_ambiente(pasta_temporaria: Path) -> None:
    """A pasta de dados deve usar PLANEJADOR_PASTA_DADOS quando definida."""
    pasta = pasta_de_dados()
    assert pasta == pasta_temporaria
    assert pasta.exists()


def test_ida_e_volta_preserva_todos_os_dados(dados_padrao: DadosDoPrograma) -> None:
    """dados_para_dict seguido de dados_de_dict deve preservar tipos e dados idênticos."""
    # Adiciona dados complexos para testar todos os campos
    dados_padrao.pessoas[0].indisponibilidades = {date(2026, 11, 7), date(2026, 11, 14)}
    dados_padrao.configuracao.nunca_juntos = [(1, 2)]
    dados_padrao.configuracao.sempre_juntos = [(3, 4)]
    dados_padrao.feriados.append(
        Feriado(data=date(2026, 11, 20), nome="Consciência Negra", periodos={"manhã": 4})
    )

    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        eh_feriado=False,
        nome_feriado="",
        duplas=[Dupla(1, 2)],
    )
    escala = Escala(
        plantoes=[plantao],
        gerada_em=datetime(2026, 11, 4, 18, 0, 0),
        confirmada=True,
    )
    dados_padrao.escalas.append(escala)

    rascunho = Escala(
        plantoes=[plantao],
        gerada_em=datetime(2026, 11, 4, 19, 0, 0),
        confirmada=False,
    )
    dados_padrao.rascunho = rascunho

    dicionario = dados_para_dict(dados_padrao)
    assert dicionario["versao_dados"] == VERSAO_DADOS

    recuperado = dados_de_dict(dicionario)

    assert len(recuperado.pessoas) == len(dados_padrao.pessoas)
    assert recuperado.pessoas[0].indisponibilidades == {date(2026, 11, 7), date(2026, 11, 14)}
    assert recuperado.configuracao.nunca_juntos == [(1, 2)]
    assert recuperado.configuracao.sempre_juntos == [(3, 4)]
    assert len(recuperado.feriados) == 1
    assert recuperado.feriados[0].data == date(2026, 11, 20)
    assert len(recuperado.escalas) == 1
    assert recuperado.escalas[0].confirmada is True
    assert recuperado.rascunho is not None
    assert recuperado.rascunho.confirmada is False
    assert recuperado.proximo_id == dados_padrao.proximo_id


def test_carregar_arquivo_inexistente_retorna_padrao(pasta_temporaria: Path) -> None:
    """Quando dados.json não existe, retorna DadosDoPrograma inicial sem erros nem avisos."""
    dados, aviso = carregar(pasta_temporaria)
    assert isinstance(dados, DadosDoPrograma)
    assert len(dados.pessoas) == 0
    assert aviso is None


def test_salvar_e_carregar_persiste_no_disco(pasta_temporaria: Path, dados_padrao: DadosDoPrograma) -> None:
    """salvar() deve gravar no disco e carregar() deve recuperar exatamente o que foi salvo."""
    salvar(dados_padrao, pasta_temporaria)
    assert (pasta_temporaria / "dados.json").exists()

    carregados, aviso = carregar(pasta_temporaria)
    assert aviso is None
    assert len(carregados.pessoas) == 28
    assert carregados.proximo_id == 29


def test_recuperacao_de_arquivo_corrompido(pasta_temporaria: Path, dados_padrao: DadosDoPrograma) -> None:
    """Se dados.json estiver corrompido, carregar() deve restaurar o backup e emitir aviso."""
    # 1. Salva versão válida
    salvar(dados_padrao, pasta_temporaria)

    # 2. Modifica dados e salva novamente para gerar um backup válido
    dados_padrao.adicionar_pessoa("Nova Pessoa")
    salvar(dados_padrao, pasta_temporaria)

    # 3. Corrompe o arquivo principal dados.json
    arquivo_principal = pasta_temporaria / "dados.json"
    arquivo_principal.write_text("{conteúdo_invalido_de_json:::", encoding="utf-8")

    # 4. Tenta carregar
    recuperados, aviso = carregar(pasta_temporaria)

    assert aviso is not None
    assert "recuperados com sucesso do backup" in aviso
    assert len(recuperados.pessoas) == 28 or len(recuperados.pessoas) == 29


def test_rotacao_mantem_no_maximo_dez_backups(pasta_temporaria: Path, dados_padrao: DadosDoPrograma) -> None:
    """Garante que a pasta de backups nunca acumula mais do que QTD_BACKUPS arquivos."""
    pasta_backups = pasta_temporaria / "backups"

    # Salva 13 vezes seguidas
    for i in range(13):
        dados_padrao.proximo_id = i + 1
        salvar(dados_padrao, pasta_temporaria)

    backups = list(pasta_backups.glob("dados_*.json"))
    assert len(backups) <= QTD_BACKUPS


def test_salvamento_atomico_nao_deixa_tmp(pasta_temporaria: Path, dados_padrao: DadosDoPrograma) -> None:
    """O arquivo temporário .tmp usado para atomicidade não deve sobrar após o salvamento."""
    salvar(dados_padrao, pasta_temporaria)
    arquivo_tmp = pasta_temporaria / "dados.json.tmp"
    assert not arquivo_tmp.exists()
    assert (pasta_temporaria / "dados.json").exists()


def test_exportar_e_importar_copia(pasta_temporaria: Path, dados_padrao: DadosDoPrograma) -> None:
    """exportar_copia e importar_copia devem salvar e restaurar dados sem perdas."""
    destino = pasta_temporaria / "minha_copia.json"
    exportar_copia(dados_padrao, destino)
    assert destino.exists()

    recuperados = importar_copia(destino)
    assert len(recuperados.pessoas) == len(dados_padrao.pessoas)
    assert recuperados.proximo_id == dados_padrao.proximo_id


def test_importar_copia_inexistente_levanta_erro(pasta_temporaria: Path) -> None:
    """importar_copia com arquivo inexistente levanta ErroEscala amigável."""
    caminho_inexistente = pasta_temporaria / "inexistente.json"
    with pytest.raises(ErroEscala, match="não foi encontrado"):
        importar_copia(caminho_inexistente)


def test_importar_copia_invalida_levanta_erro(pasta_temporaria: Path) -> None:
    """importar_copia com conteúdo inválido levanta ErroEscala amigável."""
    arquivo_invalido = pasta_temporaria / "invalido.json"
    arquivo_invalido.write_text("{\"incompleto\": true}", encoding="utf-8")

    with pytest.raises(ErroEscala, match="não é uma cópia de segurança válida"):
        importar_copia(arquivo_invalido)
