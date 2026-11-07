"""Modelos de dados do Planejador de Escala.

Define as estruturas usadas para representar pessoas, plantões, escalas e configurações,
além da exceção ErroEscala para regras de negócio.
"""

from dataclasses import dataclass, field
from datetime import date, datetime

PERIODOS_PADRAO: list[str] = ["manhã", "tarde", "noite", "dia inteiro"]
MODOS_EXPERIENCIA: list[str] = ["preferencia", "obrigatoria", "ignorar"]


class ErroEscala(Exception):
    """Erro de regra com mensagem pronta para o usuário."""
    pass


@dataclass
class Pessoa:
    """Uma pessoa da equipe."""
    id: int
    nome: str
    experiente: bool = False
    ativo: bool = True
    data_entrada: date = field(default_factory=date.today)
    indisponibilidades: set[date] = field(default_factory=set)
    ajuste_plantoes: int = 0
    ajuste_feriados: int = 0
    ultimo_plantao_manual: date | None = None


@dataclass
class ModeloDeTurno:
    """Turno que se repete toda semana. Ex.: sábado (5), manhã, 4 duplas."""
    dia_da_semana: int  # 0 = segunda ... 5 = sábado, 6 = domingo (date.weekday())
    periodo: str
    qtd_duplas: int


@dataclass
class Feriado:
    """Data especial com plantão próprio."""
    data: date
    nome: str = ""
    periodos: dict[str, int] = field(default_factory=lambda: {"manhã": 4})


@dataclass
class Dupla:
    """Duas pessoas (por id) trabalhando juntas."""
    pessoa_a: int
    pessoa_b: int

    def ids(self) -> tuple[int, int]:
        """Retorna os dois ids."""
        return (self.pessoa_a, self.pessoa_b)

    def contem(self, id_pessoa: int) -> bool:
        """Diz se a pessoa está nesta dupla."""
        return id_pessoa in (self.pessoa_a, self.pessoa_b)


@dataclass
class Plantao:
    """Um turno em uma data específica, com suas duplas."""
    data: date
    periodo: str
    qtd_duplas: int
    eh_feriado: bool = False
    nome_feriado: str = ""
    duplas: list[Dupla] = field(default_factory=list)

    def pessoas(self) -> set[int]:
        """Ids de todas as pessoas escaladas neste plantão."""
        resultado: set[int] = set()
        for d in self.duplas:
            resultado.add(d.pessoa_a)
            resultado.add(d.pessoa_b)
        return resultado


@dataclass
class Escala:
    """Conjunto de plantões gerados de uma vez (1 ou mais semanas)."""
    plantoes: list[Plantao]
    gerada_em: datetime
    confirmada: bool = False

    def primeiro_dia(self) -> date:
        """Data do primeiro plantão."""
        if not self.plantoes:
            raise ErroEscala("A escala não possui plantões.")
        return min(p.data for p in self.plantoes)

    def ultimo_dia(self) -> date:
        """Data do último plantão."""
        if not self.plantoes:
            raise ErroEscala("A escala não possui plantões.")
        return max(p.data for p in self.plantoes)

    def pessoas_no_dia(self, dia: date) -> set[int]:
        """Ids de quem trabalha em qualquer plantão nesta data."""
        resultado: set[int] = set()
        for p in self.plantoes:
            if p.data == dia:
                resultado.update(p.pessoas())
        return resultado


@dataclass
class Configuracao:
    """Todas as opções que o usuário pode mudar. Os valores padrão são as decisões da seção 4."""
    turnos: list[ModeloDeTurno] = field(default_factory=lambda: [
        ModeloDeTurno(5, "manhã", 4), ModeloDeTurno(6, "tarde", 4)
    ])
    periodos: list[str] = field(default_factory=lambda: list(PERIODOS_PADRAO))
    feriados_ativos: bool = True
    feriado_periodos_padrao: dict[str, int] = field(default_factory=lambda: {"manhã": 4})
    modo_experiencia: str = "preferencia"
    semanas_por_geracao: int = 1
    titulo_mensagem: str = "📋 *ESCALA DE PLANTÃO*"
    texto_final_mensagem: str = ""
    evitar_semanas_seguidas: bool = True
    compensar_ausencias: bool = False
    nunca_juntos: list[tuple[int, int]] = field(default_factory=list)
    sempre_juntos: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class DadosDoPrograma:
    """Tudo o que é salvo no arquivo de dados."""
    pessoas: list[Pessoa] = field(default_factory=list)
    configuracao: Configuracao = field(default_factory=Configuracao)
    feriados: list[Feriado] = field(default_factory=list)
    escalas: list[Escala] = field(default_factory=list)
    rascunho: Escala | None = None
    proximo_id: int = 1

    def buscar_pessoa(self, id_pessoa: int) -> Pessoa | None:
        """Retorna a pessoa com esse id (ou None)."""
        for p in self.pessoas:
            if p.id == id_pessoa:
                return p
        return None

    def pessoas_ativas(self) -> list[Pessoa]:
        """Lista das pessoas ativas, em ordem alfabética."""
        ativas = [p for p in self.pessoas if p.ativo]
        return sorted(ativas, key=lambda p: p.nome.lower())

    def adicionar_pessoa(self, nome: str, experiente: bool = False) -> Pessoa:
        """Cria a pessoa com novo id. Levanta ErroEscala se o nome for vazio ou repetido (ignora maiúsculas)."""
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ErroEscala("O nome da pessoa não pode ser vazio.")
        for p in self.pessoas:
            if p.nome.strip().lower() == nome_limpo.lower():
                raise ErroEscala(f"Já existe uma pessoa cadastrada com o nome '{p.nome}'.")
        nova = Pessoa(
            id=self.proximo_id,
            nome=nome_limpo,
            experiente=experiente,
            ativo=True,
            data_entrada=date.today(),
            indisponibilidades=set()
        )
        self.pessoas.append(nova)
        self.proximo_id += 1
        return nova
