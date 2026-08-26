import re
from typing import Dict, Any, List
from src.database.db import log_message_analysis

def analyze_message_and_rewrite(message_text: str, target_audience: str = "romantic") -> Dict[str, Any]:
    """
    Analyzes drafted messages for dating or professional interactions.
    Scores confidence, neediness index, banter rating, and provides 3 tailored rewrites.
    """
    msg_len = len(message_text.strip())
    words = message_text.strip().split()
    word_count = len(words)
    lower = message_text.lower()

    # 1. Neediness & Pressure Heuristics
    neediness_indicators = [
        "por favor me responde", "se você quiser", "se não for incômodo", 
        "desculpa incomodar", "sumiu", "esqueceu de mim", "???", "pq não fala comigo",
        "vc tá brava", "fiz algo de errado", "qualquer dia desses", "tanto faz"
    ]
    neediness_count = sum(1 for ind in neediness_indicators if ind in lower)
    
    if neediness_count >= 2 or lower.endswith("???") or (word_count > 60 and target_audience == "romantic"):
        neediness_level = "Alta ⚠️ (Muito apego / cobrança prematura)"
        confidence_score = 45
    elif neediness_count == 1 or word_count > 35:
        neediness_level = "Média ⚖️ (Investimento um pouco acima do ideal)"
        confidence_score = 70
    else:
        neediness_level = "Baixa / Saudável ✅ (Postura leve e equilibrada)"
        confidence_score = 88

    # 2. Banter & Engagement Check
    has_question_or_hook = "?" in message_text or any(k in lower for k in ["aposto", "reparei", "duvido", "certeza", "segredo"])
    banter_level = "Alto 🔥 (Provocativo & Engajador)" if has_question_or_hook else "Moderado / Direto 💬"

    # 3. Dynamic 3 AI Rewrites
    if target_audience == "romantic":
        rewrites = [
            {
                "style": "🔥 Descontraído & Provocativo (Playful Banter)",
                "text": f"Aposto que você estava ocupada salvando o mundo... mas e aí, sobre {words[-1] if words else 'aquele plano'}, sobreviveu?",
                "rationale": "Usa humor leve sem cobrança, tirando o peso da conversa e gerando curiosidade."
            },
            {
                "style": "⚡ Direto & Seguro (High-Value Clarity)",
                "text": f"Lembrei de você hoje ouvindo um som / vendo uma cena. Quando vamos tomar aquele café pra você me contar as novidades?",
                "rationale": "Mostra intenção clara e postura confiante, chamando para uma ação real sem rodeios."
            },
            {
                "style": "🤫 Curioso & Baixa Pressão (Low-Pressure Hook)",
                "text": f"Preciso de uma opinião rápida sobre uma coisa: você é do time que prefere pizza doce ou tem bom senso?",
                "rationale": "Quebra qualquer gelo de forma fácil de responder, criando um gancho imediato de interação."
            }
        ]
    else: # Professional / Boundary
        rewrites = [
            {
                "style": "💼 Profissional Firme & Elegante",
                "text": f"Olá! Para garantirmos a melhor entrega dentro do prazo, podemos alinhar as prioridades de hoje em 5 minutos?",
                "rationale": "Foca em resultados e gestão de tempo sem parecer defensivo."
            },
            {
                "style": "🛡️ Estabelecendo Limites com Tato",
                "text": f"Entendido o ponto. Vou avaliar o impacto no cronograma atual e retorno com uma proposta realista até amanhã de manhã.",
                "rationale": "Mantém o controle do seu tempo e demonstra profissionalismo maduro."
            },
            {
                "style": "🚀 Proativo & Conciso",
                "text": f"Com base no objetivo do projeto, sugiro focarmos no passo X primeiro. Posso seguir com essa abordagem?",
                "rationale": "Demonstra liderança e iniciativa rápida."
            }
        ]

    # Save to database
    log_message_analysis(
        original_msg=message_text,
        confidence=confidence_score,
        neediness=neediness_level,
        banter=banter_level,
        rewrites=rewrites
    )

    return {
        "original": message_text,
        "confidence_score": confidence_score,
        "neediness_level": neediness_level,
        "banter_level": banter_level,
        "feedback": "Mensagem analisada com sucesso pelo Wingman Engine.",
        "rewrites": rewrites
    }
