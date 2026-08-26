from typing import Dict, Any, List
from src.database.db import log_roleplay_session

ROLEPLAY_SCENARIOS = {
    "boss_negotiation": {
        "title": "💼 Negociação de Aumento ou Alinhamento com Chefe Exigente",
        "partner_name": "Carlos (Gerente Sênior)",
        "partner_role": "Gerente focado em números, direto e com pouco tempo.",
        "initial_message": "Bom dia. Vi que você pediu uma conversa rápida de alinhamento. Como sabe, o trimestre está apertado. O que você gostaria de colocar na mesa?",
        "evaluation_criteria": ["Clareza de Proposta", "Postura Segura", "Foco em Valor/Impacto", "Controle Emocional"]
    },
    "first_date_silence": {
        "title": "🍷 Primeiro Encontro: Quebrando o Silêncio Constrangedor",
        "partner_name": "Mariana (Encontro no Lounge)",
        "partner_role": "Interessada mas um pouco tímida, esperando que você lidere a dinâmica da conversa.",
        "initial_message": "*Mariana dá um gole no drink, olha ao redor e solta um sorriso tímido:* 'O ambiente aqui é bem legal né... mas fiquei curiosa, o que você mais gosta de fazer quando não está trabalhando?'",
        "evaluation_criteria": ["Carisma & Humor", "Escuta Ativa", "Vulnerabilidade Positiva", "Liderança de Conversa"]
    },
    "social_event_approach": {
        "title": "🤝 Festa / Networking: Chegando em um Grupo Desconhecido",
        "partner_name": "Grupo no Coffee Break / Evento",
        "partner_role": "Duas pessoas conversando sobre novidades e carreira.",
        "initial_message": "'...pois é, a palestra foi muito boa!' *Eles percebem sua aproximação e olham com simpatia, abrindo espaço na roda.*",
        "evaluation_criteria": ["Entrada Natural", "Linguagem Corporal/Tom", "Curiosidade Genuína", "Descontração"]
    }
}

def get_scenario_details(scenario_key: str) -> Dict[str, Any]:
    """Retrieves metadata and opening line for a given roleplay scenario."""
    return ROLEPLAY_SCENARIOS.get(scenario_key, ROLEPLAY_SCENARIOS["boss_negotiation"])

def generate_roleplay_turn(scenario_key: str, conversation_history: List[Dict[str, str]], user_input: str) -> Dict[str, Any]:
    """
    Generates simulated character response and real-time coaching tips during roleplay.
    """
    scenario = get_scenario_details(scenario_key)
    turn_index = len(conversation_history) // 2 + 1

    # Heuristic response templates based on turn
    if scenario_key == "boss_negotiation":
        if turn_index == 1:
            reply = "Entendo seu ponto sobre dedicação. Mas me mostre dados concretos: quais projetos liderados por você trouxeram maior retorno ou economia recentemente?"
            coach_tip = "💡 **Dica do Copiloto:** Não fale de necessidades pessoais ('contas/inflação'). Fale de métricas, economia de tempo e projetos entregues."
        elif turn_index == 2:
            reply = "Esses números de fato são sólidos. Se ajustarmos seu escopo para liderar essa nova frente no próximo ciclo, podemos revisar essa faixa. O que acha dessa estrutura?"
            coach_tip = "💡 **Dica do Copiloto:** Excelente! Aceite o escopo e amarre uma data ou critério claro de avaliação por escrito."
        else:
            reply = "Perfeito, combinamos assim. Vou alinhar com o RH para o fechamento do mês. Bom trabalho!"
            coach_tip = "🎉 **Rodada Finalizada:** Você manteve a postura firme, sem desculpas e com foco no valor gerado."
    
    elif scenario_key == "first_date_silence":
        if turn_index == 1:
            reply = "Nossa, adorei isso! Sério que você curte isso? Eu achava que quase ninguém tinha paciência pra isso hoje em dia haha. Me conta mais sobre isso!"
            coach_tip = "💡 **Dica do Wingman:** Use essa abertura para contar uma história curta e divertida com paixão, depois devolva a bola pra ela."
        elif turn_index == 2:
            reply = "Haha você é engraçado! Tava um pouco tensa antes de chegar aqui, mas você tem uma energia super leve. E você tem cara de quem é fã de viagens espontâneas..."
            coach_tip = "💡 **Dica do Wingman:** A conexão foi estabelecida. Agora é o momento de criar cumplicidade e provocar de leve."
        else:
            reply = "Adorei a nossa noite! A hora voou... a gente definitivamente precisa repetir isso logo!"
            coach_tip = "🎉 **Rodada Finalizada:** Você quebrou o gelo com naturalidade e manteve o fluxo leve e envolvente."

    else: # Social approach
        if turn_index == 1:
            reply = "Opa, tudo bem! Estávamos comentando sobre as novidades do setor. Você atua nessa área também ou veio só conferir as palestras?"
            coach_tip = "💡 **Dica do Copiloto:** Responda de forma sucinta com um gancho interessante sobre o que te trouxe ao evento."
        else:
            reply = "Muito bom te conhecer! Vamos trocar contato no LinkedIn / Insta pra mantermos o networking ativo?"
            coach_tip = "🎉 **Rodada Finalizada:** Entrada suave no grupo e encerramento de alto valor."

    # Generate scorecard if reached 3 turns
    scorecard = None
    if turn_index >= 3:
        scorecard = {
            "overall_score": 92,
            "clarity": "Excelente (94%)",
            "confidence": "Firme & Calma (90%)",
            "emotional_intelligence": "Alta (92%)",
            "summary": "Você demonstrou excelente controle situacional, sem agressividade ou submissão."
        }
        log_roleplay_session(scenario_key=scenario_key, turns_count=turn_index, scorecard=scorecard)

    return {
        "reply": reply,
        "coach_tip": coach_tip,
        "is_completed": turn_index >= 3,
        "scorecard": scorecard
    }
