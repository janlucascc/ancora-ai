import re
from typing import Dict, Any, Optional

CRISIS_PATTERNS = [
    r"\b(suicid|matar|acabar com a minha vida|quitar da vida|me matar|tirar minha vida|self[- ]?harm|kill myself|end my life|want to die)\b",
    r"\b(cortar os pulsos|overdose|pular da ponte|nao aguento mais viver)\b"
]

def check_crisis_risk(text: str) -> Optional[Dict[str, Any]]:
    """Evaluates user input for severe crisis signals and returns immediate safety intervention."""
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return {
                "is_crisis": True,
                "risk_level": "high",
                "message": (
                    "🚨 **Você não está sozinho e a sua vida tem um valor imenso.**\n\n"
                    "Eu sou um assistente de apoio para a rotina e momentos de estresse, mas agora o mais importante é você conversar com alguém especializado que pode te acolher com todo o cuidado:\n\n"
                    "🇧🇷 **No Brasil (CVV):** Ligue **188** (Ligação gratuita e sigilosa 24h) ou acesse [cvv.org.br](https://www.cvv.org.br)\n"
                    "🇺🇸 **In the US / Global:** Call or text **988** (Suicide & Crisis Lifeline)\n\n"
                    "Por favor, procure um amigo de confiança, um familiar ou um profissional de saúde agora mesmo. Estamos torcendo por você."
                )
            }
    return None
