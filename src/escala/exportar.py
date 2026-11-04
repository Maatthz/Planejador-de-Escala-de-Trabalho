"""Exportação de escalas para texto formatado do WhatsApp.

Gera uma representação textual limpa, com cabeçalhos em negrito e listas
numeradas de duplas prontas para copiar e colar em mensagens.
"""

from src.escala.datas import formatar_dia_completo
from src.escala.modelos import DadosDoPrograma, Escala, Plantao


def _formatar_cabecalho_plantao(plantao: Plantao) -> str:
    """Formata a linha de cabeçalho do plantão com data, período e feriado se houver."""
    dia_formatado = formatar_dia_completo(plantao.data)
    periodo_formatado = plantao.periodo.capitalize()

    if plantao.eh_feriado:
        detalhe_feriado = (
            f" (Feriado: {plantao.nome_feriado})"
            if plantao.nome_feriado
            else " (Feriado)"
        )
        return f"📅 *{dia_formatado} — {periodo_formatado}{detalhe_feriado}*"

    return f"📅 *{dia_formatado} — {periodo_formatado}*"


def gerar_texto_whatsapp(escala: Escala, dados: DadosDoPrograma) -> str:
    """Monta o texto da seção 10.6 para colar no WhatsApp."""
    blocos: list[str] = [dados.configuracao.titulo_mensagem]

    for plantao in escala.plantoes:
        linhas_plantao: list[str] = [_formatar_cabecalho_plantao(plantao)]
        for i, dupla in enumerate(plantao.duplas, start=1):
            p_a = dados.buscar_pessoa(dupla.pessoa_a)
            p_b = dados.buscar_pessoa(dupla.pessoa_b)
            nome_a = p_a.nome if p_a else f"ID {dupla.pessoa_a}"
            nome_b = p_b.nome if p_b else f"ID {dupla.pessoa_b}"
            linhas_plantao.append(f"{i}. {nome_a} e {nome_b}")

        blocos.append("\n".join(linhas_plantao))

    if dados.configuracao.texto_final_mensagem.strip():
        blocos.append(dados.configuracao.texto_final_mensagem.strip())

    return "\n\n".join(blocos)
