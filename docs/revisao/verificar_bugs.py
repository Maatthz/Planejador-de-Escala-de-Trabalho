"""Verificação empírica dos bugs de lógica encontrados na revisão (ver REVISAO_TECH_LEAD.md).

Rodar na raiz do projeto:  python docs/revisao/verificar_bugs.py
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.escala.modelos import DadosDoPrograma, Pessoa
from src.escala.gerador import gerar_escala
from src.escala.edicao import confirmar_rascunho, excluir_escala
from src.escala.historico import calcular_contadores, ajustar_contadores_pessoa, quadro_de_justica

INICIO = date(2026, 1, 5)  # segunda-feira


def equipe(n=28, exp=10):
    d = DadosDoPrograma()
    for i in range(1, n + 1):
        d.pessoas.append(Pessoa(id=i, nome=f"P{i:02d}", experiente=i <= exp,
                                data_entrada=date(2025, 1, 1)))
    d.proximo_id = n + 1
    return d


def confirmar_semanas(d, inicio, qtd, semente=1):
    for s in range(qtd):
        gerar_escala(d, inicio + timedelta(weeks=s), 1, semente=semente + s)
        confirmar_rascunho(d)


# ---------------------------------------------------------------- 1
print("=== 1. Pessoa INATIVA rebaixa o piso de quem volta de férias ===")
for com_inativo in (False, True):
    d = equipe()
    confirmar_semanas(d, INICIO, 2)
    if com_inativo:
        d.pessoas[27].ativo = False           # P28 sai da equipe
    ferias = d.pessoas[0]                      # P01 sai de férias por 6 semanas
    for i in range(14, 14 + 42):
        ferias.indisponibilidades.add(INICIO + timedelta(days=i))
    confirmar_semanas(d, INICIO + timedelta(weeks=2), 6, semente=50)
    c = calcular_contadores(d)
    ativos = [p.id for p in d.pessoas if p.ativo and p.id != 1]
    print(f"  inativo={com_inativo}: carga P01 (voltou)={c.carga[1]}, "
          f"menor carga entre ativos={min(c.carga[i] for i in ativos)}, "
          f"carga P28={c.carga[28]}")

# ---------------------------------------------------------------- 2
print("\n=== 2. Regerar uma semana JÁ confirmada escolhe outras pessoas ===")
d = equipe()
confirmar_semanas(d, INICIO, 3)
semana = INICIO + timedelta(weeks=3)
gerar_escala(d, semana, 1, semente=7)
confirmar_rascunho(d)
originais = set().union(*(p.pessoas() for p in d.escalas[-1].plantoes))
gerar_escala(d, semana, 1, semente=7)     # usuário quer só "refazer" a semana
novos = set().union(*(p.pessoas() for p in d.rascunho.plantoes))
print(f"  pessoas em comum entre original e regerada: {len(originais & novos)} de 16")
confirmar_rascunho(d)
c = calcular_contadores(d)
print(f"  cargas após confirmar: min={min(c.carga.values())} max={max(c.carga.values())}")

# ---------------------------------------------------------------- 3
print("\n=== 3. Modo 'obrigatoria' violado por dupla fixa de 2 experientes ===")
d = equipe(n=8, exp=4)                     # exatamente 4 experientes para 4 duplas
d.configuracao.turnos = d.configuracao.turnos[:1]
d.configuracao.modo_experiencia = "obrigatoria"
d.configuracao.sempre_juntos = [(1, 2)]    # dois experientes fixos
esc = gerar_escala(d, INICIO, 1, semente=1)
for dupla in esc.plantoes[0].duplas:
    a, b = d.buscar_pessoa(dupla.pessoa_a), d.buscar_pessoa(dupla.pessoa_b)
    flag = "" if (a.experiente or b.experiente) else "   <-- SEM EXPERIENTE"
    print(f"  {a.nome}{'*' if a.experiente else ''} + {b.nome}{'*' if b.experiente else ''}{flag}")

# ---------------------------------------------------------------- 4
print("\n=== 4. Salvar o Quadro de Justiça 'congela' o último plantão ===")
d = equipe()
confirmar_semanas(d, INICIO, 2)
# Usuário abre "Editar manualmente" e clica Salvar SEM mudar nada (o que a tela faz):
for linha in quadro_de_justica(d):
    ajustar_contadores_pessoa(d, linha.pessoa.id, linha.plantoes_reais,
                              linha.feriados_trabalhados, linha.ultimo_plantao)
quem_trabalhou = d.escalas[-1].plantoes[0].pessoas()
excluir_escala(d, len(d.escalas) - 1)      # escala da semana 2 estava errada
c = calcular_contadores(d)
pid = next(iter(quem_trabalhou))
print(f"  P{pid:02d}: ultimo_plantao={c.ultimo_plantao.get(pid)} (None = sem dado fantasma)")
gerar_escala(d, INICIO + timedelta(weeks=1), 1, semente=3)
novos = set().union(*(p.pessoas() for p in d.rascunho.plantoes))
print(f"  ao regerar a semana excluída, {len(quem_trabalhou & novos)} das 8 pessoas daquele "
      f"plantão voltaram (são tratadas como 'já trabalha nesta semana')")
