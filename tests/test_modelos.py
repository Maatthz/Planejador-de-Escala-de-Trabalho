"""Testes para o módulo de modelos de dados."""

from datetime import date, datetime
import pytest

from src.escala.modelos import (
    DadosDoPrograma,
    Dupla,
    ErroEscala,
    Escala,
    Pessoa,
    Plantao,
)


def test_adicionar_pessoa_sucesso() -> None:
    """Garante que adicionar pessoa cria o registro correto e incrementa proximo_id."""
    dados = DadosDoPrograma()
    nova = dados.adicionar_pessoa("Carlos", experiente=True)

    assert nova.id == 1
    assert nova.nome == "Carlos"
    assert nova.experiente is True
    assert nova.ativo is True
    assert nova.data_entrada == date.today()
    assert dados.proximo_id == 2
    assert len(dados.pessoas) == 1


def test_adicionar_pessoa_nome_vazio_levanta_erro() -> None:
    """Nome vazio ou apenas espaços deve levantar ErroEscala."""
    dados = DadosDoPrograma()
    with pytest.raises(ErroEscala, match="O nome da pessoa não pode ser vazio"):
        dados.adicionar_pessoa("   ")


def test_adicionar_pessoa_nome_duplicado_levanta_erro() -> None:
    """Nome repetido (mesmo com maiúsculas/minúsculas diferentes) deve levantar ErroEscala."""
    dados = DadosDoPrograma()
    dados.adicionar_pessoa("Beatriz")

    with pytest.raises(ErroEscala, match="Já existe uma pessoa cadastrada com o nome 'Beatriz'"):
        dados.adicionar_pessoa("beatriz")


def test_buscar_pessoa_existente_e_inexistente() -> None:
    """buscar_pessoa deve retornar a Pessoa correta ou None se não existir."""
    p1 = Pessoa(id=1, nome="Ana")
    p2 = Pessoa(id=2, nome="Bruno")
    dados = DadosDoPrograma(pessoas=[p1, p2])

    assert dados.buscar_pessoa(1) == p1
    assert dados.buscar_pessoa(2) == p2
    assert dados.buscar_pessoa(99) is None


def test_pessoas_ativas_ordena_alfabeticamente_e_ignora_inativos() -> None:
    """pessoas_ativas deve filtrar apenas ativos e ordenar por ordem alfabética."""
    p1 = Pessoa(id=1, nome="Zélia", ativo=True)
    p2 = Pessoa(id=2, nome="ana", ativo=True)
    p3 = Pessoa(id=3, nome="Carlos", ativo=False)
    p4 = Pessoa(id=4, nome="Beto", ativo=True)

    dados = DadosDoPrograma(pessoas=[p1, p2, p3, p4])
    ativas = dados.pessoas_ativas()

    assert [p.nome for p in ativas] == ["ana", "Beto", "Zélia"]


def test_dupla_ids_e_contem() -> None:
    """Verifica métodos ids e contem da Dupla."""
    dupla = Dupla(pessoa_a=10, pessoa_b=20)

    assert dupla.ids() == (10, 20)
    assert dupla.contem(10) is True
    assert dupla.contem(20) is True
    assert dupla.contem(30) is False


def test_plantao_pessoas() -> None:
    """pessoas() do Plantao deve retornar o conjunto de todos os escalados."""
    plantao = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=2,
        duplas=[Dupla(1, 2), Dupla(3, 4)],
    )

    assert plantao.pessoas() == {1, 2, 3, 4}


def test_escala_primeiro_e_ultimo_dia() -> None:
    """Escala deve calcular corretamente o primeiro e o último dia com plantão."""
    p1 = Plantao(data=date(2026, 11, 7), periodo="manhã", qtd_duplas=1)
    p2 = Plantao(data=date(2026, 11, 14), periodo="tarde", qtd_duplas=1)
    escala = Escala(plantoes=[p1, p2], gerada_em=datetime.now())

    assert escala.primeiro_dia() == date(2026, 11, 7)
    assert escala.ultimo_dia() == date(2026, 11, 14)


def test_escala_sem_plantoes_levanta_erro() -> None:
    """Escala vazia levanta ErroEscala ao consultar primeiro ou último dia."""
    escala = Escala(plantoes=[], gerada_em=datetime.now())
    with pytest.raises(ErroEscala, match="A escala não possui plantões"):
        escala.primeiro_dia()
    with pytest.raises(ErroEscala, match="A escala não possui plantões"):
        escala.ultimo_dia()


def test_escala_pessoas_no_dia() -> None:
    """pessoas_no_dia() deve agregar todas as pessoas dos plantões daquela data."""
    p1 = Plantao(
        data=date(2026, 11, 7),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(1, 2)],
    )
    p2 = Plantao(
        data=date(2026, 11, 7),
        periodo="tarde",
        qtd_duplas=1,
        duplas=[Dupla(3, 4)],
    )
    p3 = Plantao(
        data=date(2026, 11, 8),
        periodo="manhã",
        qtd_duplas=1,
        duplas=[Dupla(5, 6)],
    )
    escala = Escala(plantoes=[p1, p2, p3], gerada_em=datetime.now())

    assert escala.pessoas_no_dia(date(2026, 11, 7)) == {1, 2, 3, 4}
    assert escala.pessoas_no_dia(date(2026, 11, 8)) == {5, 6}
    assert escala.pessoas_no_dia(date(2026, 11, 9)) == set()
