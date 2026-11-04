"""Textos de ajuda e explicações das configurações para o usuário.

Fornece títulos em português simples, explicações didáticas e exemplos práticos
para cada campo configurável do programa.
"""

from dataclasses import dataclass


@dataclass
class TextoAjuda:
    """Explicação de uma configuração para o usuário leigo."""

    titulo: str
    explicacao: str
    exemplo: str


AJUDA: dict[str, TextoAjuda] = {
    "turnos": TextoAjuda(
        titulo="Turnos da semana",
        explicacao="Quais dias e períodos têm plantão toda semana, e quantas duplas em cada um.",
        exemplo='"Sábado — manhã — 4 duplas" = 8 pessoas trabalhando no sábado de manhã.',
    ),
    "periodos": TextoAjuda(
        titulo="Nomes dos períodos",
        explicacao="Os nomes que aparecem na escala e na mensagem, na ordem em que acontecem no dia.",
        exemplo='Adicione "noite" se a sua equipe tiver plantão noturno.',
    ),
    "feriados_ativos": TextoAjuda(
        titulo="Plantão em feriados",
        explicacao="Ligado: os feriados cadastrados entram na escala gerada. Desligado: feriados não têm plantão.",
        exemplo="Desligado: o Natal fica sem ninguém escalado.",
    ),
    "feriado_periodos_padrao": TextoAjuda(
        titulo="Padrão para feriados",
        explicacao="Como um feriado novo já vem preenchido (você pode alterar ao adicionar cada feriado).",
        exemplo='"Manhã — 4 duplas": ao adicionar Finados, o formulário já vem sugerindo esse formato.',
    ),
    "modo_experiencia": TextoAjuda(
        titulo="Experiência na dupla",
        explicacao="Preferência: tenta colocar 1 experiente por dupla. Obrigatória: nunca monta dupla sem experiente. Ignorar: não leva em conta.",
        exemplo='Com "Obrigatória", se faltar gente experiente no sábado, o programa avisa em vez de gerar a escala.',
    ),
    "semanas_por_geracao": TextoAjuda(
        titulo="Semanas por vez",
        explicacao='Quantas semanas o botão "Gerar escala" monta de uma única vez.',
        exemplo="2 = gera escala quinzenal.",
    ),
    "titulo_mensagem": TextoAjuda(
        titulo="Título da mensagem",
        explicacao="Primeira linha do texto para WhatsApp. Texto colocado entre *asteriscos* fica em negrito no WhatsApp.",
        exemplo="*ESCALA DE PLANTÃO — NOVEMBRO*",
    ),
    "texto_final_mensagem": TextoAjuda(
        titulo="Texto final",
        explicacao="Mensagem de encerramento que aparece no fim do texto copiado (opcional).",
        exemplo='"Trocas de plantão: avisar com 48h de antecedência à coordenação."',
    ),
    "evitar_semanas_seguidas": TextoAjuda(
        titulo="Evitar semanas seguidas",
        explicacao="Prioriza dar descanso a quem trabalhou na semana anterior sempre que possível.",
        exemplo="Com 28 pessoas e 16 vagas, algumas repetições são necessárias; o programa prioriza quem descansou mais tempo.",
    ),
    "compensar_ausencias": TextoAjuda(
        titulo="Compensar ausências",
        explicacao="Desligado (recomendado): quem volta de férias entra empatado com quem menos trabalhou. Ligado: quem se ausentou 'fica devendo' plantões e trabalha com mais frequência até igualar.",
        exemplo="Ana tirou 1 mês de férias. Com a opção ligada, ela será escalada quase toda semana ao retornar.",
    ),
    "nunca_juntos": TextoAjuda(
        titulo="Nunca juntos",
        explicacao="Pares de pessoas que não devem formar dupla. Elas ainda podem trabalhar no mesmo dia, mas sempre em duplas separadas.",
        exemplo="Ana ✕ Bruno nunca serão colocados como parceiros de dupla.",
    ),
    "sempre_juntos": TextoAjuda(
        titulo="Duplas fixas",
        explicacao="Pessoas que sempre trabalham juntas na mesma dupla. Se uma estiver de folga, a outra é escalada normalmente com outra pessoa.",
        exemplo="Carla + Diego formam dupla fixa.",
    ),
    "backup_manual": TextoAjuda(
        titulo="Cópia de segurança",
        explicacao='"Salvar cópia" guarda todos os dados em um arquivo à sua escolha (para pendrive ou e-mail). "Restaurar" recupera os dados de uma cópia.',
        exemplo="Útil ao formatar o computador ou transferir o programa para outra máquina.",
    ),
}


def obter_ajuda(chave: str) -> TextoAjuda:
    """Retorna o texto de ajuda. Levanta KeyError se a chave não existir (erro de programação)."""
    return AJUDA[chave]
