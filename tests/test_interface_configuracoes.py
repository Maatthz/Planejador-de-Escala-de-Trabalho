"""Testes de interface para a janela modal de Configurações (Fase 7)."""

from pathlib import Path
import pytest

from src.escala.armazenamento import carregar
from src.escala.interface.janela_configuracoes import JanelaConfiguracoes
from src.escala.interface.janela_principal import JanelaPrincipal
from src.escala.modelos import Configuracao, DadosDoPrograma, ModeloDeTurno


@pytest.fixture
def app_janela_config(app_janela_compartilhada: JanelaPrincipal) -> JanelaPrincipal:
    """Usa a janela compartilhada da sessão para testes de interface."""
    return app_janela_compartilhada


def test_janela_configuracoes_inicializacao(
    app_janela_config: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """JanelaConfiguracoes deve abrir com todas as seções renderizadas e campos preenchidos."""
    app_janela_config.dados = dados_padrao
    janela = JanelaConfiguracoes(pai=app_janela_config, dados=dados_padrao, ao_mudar=app_janela_config.ao_mudar)
    app_janela_config.update_idletasks()

    assert janela.config_temp.titulo_mensagem == dados_padrao.configuracao.titulo_mensagem
    assert janela.entry_titulo_msg.get() == dados_padrao.configuracao.titulo_mensagem
    assert len(janela.config_temp.turnos) == 2
    janela.destroy()


def test_janela_configuracoes_adicionar_e_remover_turno(
    app_janela_config: JanelaPrincipal, dados_padrao: DadosDoPrograma
) -> None:
    """Deve permitir adicionar novos turnos e remover existentes (respeitando o mínimo de 1)."""
    app_janela_config.dados = dados_padrao
    janela = JanelaConfiguracoes(pai=app_janela_config, dados=dados_padrao, ao_mudar=app_janela_config.ao_mudar)
    app_janela_config.update_idletasks()

    # Adiciona Domingo manhã
    janela.combo_novo_dia.set("Domingo")
    janela.combo_novo_periodo.set("manhã")
    janela.combo_nova_qtd.set("2")
    janela._adicionar_turno()

    assert len(janela.config_temp.turnos) == 3
    assert janela.config_temp.turnos[-1].dia_da_semana == 6
    assert janela.config_temp.turnos[-1].periodo == "manhã"
    assert janela.config_temp.turnos[-1].qtd_duplas == 2

    # Remove o primeiro turno
    janela._remover_turno(0)
    assert len(janela.config_temp.turnos) == 2

    # Remove outro turno
    janela._remover_turno(0)
    assert len(janela.config_temp.turnos) == 1

    # Tentar remover o último turno deve ser impedido
    janela._remover_turno(0)
    assert len(janela.config_temp.turnos) == 1
    janela.destroy()


def test_janela_configuracoes_salvar_alteracoes(
    app_janela_config: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma
) -> None:
    """Ao salvar alterações válidas, os dados devem ser atualizados e persistidos."""
    app_janela_config.dados = dados_padrao
    janela = JanelaConfiguracoes(pai=app_janela_config, dados=dados_padrao, ao_mudar=app_janela_config.ao_mudar)
    app_janela_config.update_idletasks()

    # Altera título da mensagem
    janela.entry_titulo_msg.delete(0, "end")
    janela.entry_titulo_msg.insert(0, "📋 *NOVA ESCALA DEZEMBRO*")

    # Altera períodos
    janela.entry_periodos.delete(0, "end")
    janela.entry_periodos.insert(0, "manhã, tarde, noite")

    # Altera modo de experiência
    janela.seg_experiencia.set("Obrigatória")

    # Altera semanas por geração
    janela.seg_semanas.set("2 semanas (quinzenal)")

    # Salva
    janela._salvar()
    app_janela_config.update_idletasks()

    assert dados_padrao.configuracao.titulo_mensagem == "📋 *NOVA ESCALA DEZEMBRO*"
    assert dados_padrao.configuracao.periodos == ["manhã", "tarde", "noite"]
    assert dados_padrao.configuracao.modo_experiencia == "obrigatoria"
    assert dados_padrao.configuracao.semanas_por_geracao == 2

    # Confere persistência no disco
    carregados, _ = carregar(pasta_temporaria)
    assert carregados.configuracao.titulo_mensagem == "📋 *NOVA ESCALA DEZEMBRO*"
    assert carregados.configuracao.modo_experiencia == "obrigatoria"


def test_janela_configuracoes_validacao_campos_invalidos(
    app_janela_config: JanelaPrincipal, dados_padrao: DadosDoPrograma, monkeypatch
) -> None:
    """Erros de validação (título vazio, períodos vazios) devem exibir alerta sem fechar."""
    erros = []
    monkeypatch.setattr("src.escala.interface.janela_configuracoes.mostrar_erro", lambda pai, txt: erros.append(txt))

    app_janela_config.dados = dados_padrao
    janela = JanelaConfiguracoes(pai=app_janela_config, dados=dados_padrao, ao_mudar=app_janela_config.ao_mudar)
    app_janela_config.update_idletasks()

    # Título vazio
    janela.entry_titulo_msg.delete(0, "end")
    janela._salvar()
    assert len(erros) == 1
    assert "título" in erros[0].lower()

    # Períodos vazios
    janela.entry_titulo_msg.insert(0, "Título Válido")
    janela.entry_periodos.delete(0, "end")
    janela._salvar()
    assert len(erros) == 2
    assert "período" in erros[1].lower()

    janela.destroy()


def test_janela_configuracoes_restaurar_padrao(
    app_janela_config: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma, monkeypatch
) -> None:
    """Botão 'Restaurar padrão' redefine as configurações originais após confirmação."""
    dados_padrao.configuracao.titulo_mensagem = "Título Customizado"
    dados_padrao.configuracao.semanas_por_geracao = 3
    dados_padrao.configuracao.modo_experiencia = "obrigatoria"

    # Confirmação 'Sim' exigindo os 3 argumentos (pai, titulo, texto)
    monkeypatch.setattr(
        "src.escala.interface.janela_configuracoes.perguntar_sim_nao",
        lambda pai, titulo, texto: True,
    )

    app_janela_config.dados = dados_padrao
    janela = JanelaConfiguracoes(pai=app_janela_config, dados=dados_padrao, ao_mudar=app_janela_config.ao_mudar)
    app_janela_config.update_idletasks()

    janela._restaurar_padrao()
    app_janela_config.update_idletasks()

    assert dados_padrao.configuracao.titulo_mensagem == "📋 *ESCALA DE PLANTÃO*"
    assert dados_padrao.configuracao.semanas_por_geracao == 1
    assert dados_padrao.configuracao.modo_experiencia == "preferencia"

    carregados, _ = carregar(pasta_temporaria)
    assert carregados.configuracao.titulo_mensagem == "📋 *ESCALA DE PLANTÃO*"


def test_janela_configuracoes_avancadas_regras_pares(
    app_janela_config: JanelaPrincipal, dados_padrao: DadosDoPrograma, monkeypatch
) -> None:
    """Configuração de pares 'nunca juntos' e 'sempre juntos' valida duplicidade e conflitos."""
    erros = []
    monkeypatch.setattr("src.escala.interface.janela_configuracoes.mostrar_erro", lambda pai, txt: erros.append(txt))

    app_janela_config.dados = dados_padrao
    janela = JanelaConfiguracoes(pai=app_janela_config, dados=dados_padrao, ao_mudar=app_janela_config.ao_mudar)
    app_janela_config.update_idletasks()

    janela._alternar_avancadas()
    assert janela.avancadas_expandidas is True

    # Adiciona os dois primeiros nomes em nunca juntos
    nomes, mapa = janela._obter_nomes_pessoas()
    janela.combo_nunca_a.set(nomes[0])
    janela.combo_nunca_b.set(nomes[1])
    janela._adicionar_nunca_juntos()

    id_0 = mapa[nomes[0]]
    id_1 = mapa[nomes[1]]
    assert (min(id_0, id_1), max(id_0, id_1)) in janela.config_temp.nunca_juntos

    # Tenta adicionar o mesmo par em duplas fixas (conflito)
    janela.combo_sempre_a.set(nomes[0])
    janela.combo_sempre_b.set(nomes[1])
    janela._adicionar_sempre_juntos()
    assert len(erros) > 0

    # Adiciona os nomes 2 e 3 em duplas fixas
    janela.combo_sempre_a.set(nomes[2])
    janela.combo_sempre_b.set(nomes[3])
    janela._adicionar_sempre_juntos()
    id_2 = mapa[nomes[2]]
    id_3 = mapa[nomes[3]]
    assert (min(id_2, id_3), max(id_2, id_3)) in janela.config_temp.sempre_juntos

    # Tenta adicionar uma pessoa que já está em dupla fixa com outra pessoa
    janela.combo_sempre_a.set(nomes[2])
    janela.combo_sempre_b.set(nomes[4])
    janela._adicionar_sempre_juntos()
    assert "mais de uma dupla fixa" in erros[-1]

    janela.destroy()


def test_janela_configuracoes_backup_manual(
    app_janela_config: JanelaPrincipal, pasta_temporaria: Path, dados_padrao: DadosDoPrograma, monkeypatch
) -> None:
    """Exportar e restaurar cópia de segurança manual via interface."""
    caminho_backup = pasta_temporaria / "backup_teste.json"
    infos = []
    monkeypatch.setattr("src.escala.interface.janela_configuracoes.mostrar_info", lambda pai, txt: infos.append(txt))
    monkeypatch.setattr("tkinter.filedialog.asksaveasfilename", lambda **kwargs: str(caminho_backup))
    monkeypatch.setattr("tkinter.filedialog.askopenfilename", lambda **kwargs: str(caminho_backup))
    monkeypatch.setattr(
        "src.escala.interface.janela_configuracoes.perguntar_sim_nao",
        lambda pai, titulo, texto: True,
    )

    app_janela_config.dados = dados_padrao
    janela = JanelaConfiguracoes(pai=app_janela_config, dados=dados_padrao, ao_mudar=app_janela_config.ao_mudar)
    app_janela_config.update_idletasks()

    # Salva cópia
    janela._salvar_copia_manual()
    assert caminho_backup.exists()

    # Modifica algo em dados_padrao
    dados_padrao.adicionar_pessoa("Membro Temporario")
    assert len(dados_padrao.pessoas) == 29

    # Restaura cópia
    janela._restaurar_copia_manual()
    assert len(app_janela_config.dados.pessoas) == 28


def test_janela_configuracoes_salvar_com_equipe_pequena(
    app_janela_config: JanelaPrincipal, pasta_temporaria: Path, monkeypatch
) -> None:
    """Salvar configurações quando há menos pessoas que o turno pede deve exibir aviso de capacidade sem erro."""
    dados_vazios = DadosDoPrograma()
    perguntas: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "src.escala.interface.janela_configuracoes.perguntar_sim_nao",
        lambda pai, titulo, texto: (perguntas.append((titulo, texto)), True)[1],
    )
    monkeypatch.setattr(
        "src.escala.interface.janela_configuracoes.mostrar_info",
        lambda pai, txt: None,
    )

    app_janela_config.dados = dados_vazios
    janela = JanelaConfiguracoes(
        pai=app_janela_config,
        dados=dados_vazios,
        ao_mudar=app_janela_config.ao_mudar,
    )
    app_janela_config.update_idletasks()

    janela._salvar()
    assert len(perguntas) == 1
    assert perguntas[0][0] == "Aviso de capacidade"
