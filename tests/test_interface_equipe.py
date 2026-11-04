"""Testes de interface para a JanelaPrincipal e a aba Equipe."""

from datetime import date
from pathlib import Path
import pytest

from src.escala.armazenamento import carregar
from src.escala.interface.janela_principal import JanelaPrincipal
from src.escala.modelos import DadosDoPrograma


@pytest.fixture(scope="module")
def app_janela():
    """Mantém uma única instância de janela para os testes de interface, evitando recriação do interpretador Tcl."""
    app = JanelaPrincipal(dados=DadosDoPrograma())
    app.withdraw()
    yield app
    try:
        app.destroy()
    except Exception:
        pass


def test_janela_principal_inicializacao(app_janela: JanelaPrincipal, dados_padrao: DadosDoPrograma) -> None:
    """JanelaPrincipal deve inicializar sem erros e renderizar a aba Equipe."""
    app_janela.dados = dados_padrao
    app_janela.tela_equipe.dados = dados_padrao
    app_janela.tela_equipe.atualizar_tela()
    app_janela.update_idletasks()

    assert app_janela.tela_equipe is not None
    assert "28 pessoas ativas" in app_janela.tela_equipe.lbl_contador.cget("text")


def test_equipe_estado_vazio(app_janela: JanelaPrincipal) -> None:
    """Quando não há pessoas cadastradas, a tela deve exibir o estado vazio orientativo."""
    dados_vazios = DadosDoPrograma()
    app_janela.dados = dados_vazios
    app_janela.tela_equipe.dados = dados_vazios
    app_janela.tela_equipe.atualizar_tela()
    app_janela.update_idletasks()

    assert "0 pessoas ativas" in app_janela.tela_equipe.lbl_contador.cget("text")
    filhos = app_janela.tela_equipe.scroll_lista.winfo_children()
    assert len(filhos) == 1  # Cartão de estado vazio


def test_adicionar_pessoa_persiste_ao_salvar(
    app_janela: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """Adicionar uma pessoa via TelaEquipe deve persistir no disco através de ao_mudar()."""
    app_janela.dados = dados_padrao
    app_janela.tela_equipe.dados = dados_padrao
    app_janela.tela_equipe.atualizar_tela()
    app_janela.update_idletasks()

    dados_padrao.adicionar_pessoa("Novo Integrante", experiente=True)
    app_janela.ao_mudar()

    carregados, _ = carregar(pasta_temporaria)
    assert len(carregados.pessoas) == 29
    nova = carregados.buscar_pessoa(29)
    assert nova is not None
    assert nova.nome == "Novo Integrante"
    assert nova.experiente is True


def test_desativar_e_reativar_pessoa(
    app_janela: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """Desativar uma pessoa a torna inativa; reativar atualiza data_entrada para hoje."""
    app_janela.dados = dados_padrao
    app_janela.tela_equipe.dados = dados_padrao
    app_janela.tela_equipe.atualizar_tela()
    app_janela.update_idletasks()

    pessoa = dados_padrao.buscar_pessoa(1)
    pessoa.data_entrada = date(2020, 1, 1)

    # 1. Desativa
    app_janela.tela_equipe._alternar_status(pessoa)
    assert pessoa.ativo is False

    carregados, _ = carregar(pasta_temporaria)
    assert carregados.buscar_pessoa(1).ativo is False

    # 2. Reativa
    app_janela.tela_equipe._alternar_status(pessoa)
    assert pessoa.ativo is True
    assert pessoa.data_entrada == date.today()

    carregados2, _ = carregar(pasta_temporaria)
    assert carregados2.buscar_pessoa(1).ativo is True
    assert carregados2.buscar_pessoa(1).data_entrada == date.today()


def test_excluir_pessoa_sem_escalas(
    app_janela: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """Pessoa sem escalas confirmadas pode ser excluída e a alteração persiste."""
    app_janela.dados = dados_padrao
    app_janela.tela_equipe.dados = dados_padrao
    app_janela.tela_equipe.atualizar_tela()
    app_janela.update_idletasks()

    pessoa = dados_padrao.buscar_pessoa(28)
    dados_padrao.pessoas.remove(pessoa)
    app_janela.ao_mudar()

    carregados, _ = carregar(pasta_temporaria)
    assert len(carregados.pessoas) == 27
    assert carregados.buscar_pessoa(28) is None
