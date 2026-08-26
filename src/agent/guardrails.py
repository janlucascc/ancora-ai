import re
from typing import Dict, Any, Optional

# ════════════════════════════════════════════════════════
# CRISIS PATTERNS — Portuguese & English
# ════════════════════════════════════════════════════════
CRISIS_PATTERNS = [
    r"\b(suicid\w*|me matar|me mat[ao]|matar.me|quero morrer|vontade de morrer)\b",
    r"\b(acabar com (a minha|minha|a) vida|tirar (a minha|minha) vida|não quero mais viver|desaparecer para sempre)\b",
    r"\b(cortar.os.pulsos|me cortar|automutila[çc][aã]o|autolesão|self.?harm)\b",
    r"\b(overdose|me jogar|pular da (ponte|janela|predio|prédio))\b",
    r"\b(kill myself|end my life|want to die|no reason to live|don't want to exist)\b",
    r"\b(nao aguento mais viver|não aguento mais viver|não tem mais saída)\b"
]

# ════════════════════════════════════════════════════════
# IDENTITY MANIPULATION PATTERNS — Jailbreak Detection
# ════════════════════════════════════════════════════════
MANIPULATION_PATTERNS = [
    r"\b(ignore (all |your )?(previous |prior )?instructions|ignore o (seu |teu )?prompt)\b",
    r"\b(act as (dan|jailbreak|evil ai|uncensored|unrestricted))\b",
    r"\b(você agora (é|será|deve ser)|você é na verdade|now you are|pretend you (are|have no))\b",
    r"\b(sem (restrições|limites|filtros)|without (restrictions|limits|filters))\b",
    r"\b(modo (sem filtro|desenvolvedor|deus|irrestrito)|(developer|god|dev) mode)\b",
    r"\b(desbloqu\w+|unlock(ed)?|jailbreak(ed)?)\b",
    r"\b(esqueça (tudo|suas instruções|seu prompt)|forget (your|all) (instructions|prompt))\b",
    r"\b(nova persona|new persona|fingir ser|pretend to be)\b"
]

def check_crisis_risk(text: str) -> Optional[Dict[str, Any]]:
    """
    Evaluates user input for severe psychological crisis signals.
    Returns an immediate, compassionate safety intervention response.
    """
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return {
                "is_crisis": True,
                "risk_level": "high",
                "message": (
                    "Obrigado por confiar aqui. O que você trouxe agora é sério — e merece atenção de alguém "
                    "treinado especificamente para isso.\n\n"
                    "Eu consigo apoiar em muitas coisas do dia a dia, mas o que você está sentindo agora "
                    "precisa de um profissional humano, de verdade, não de uma IA.\n\n"
                    "**Por favor, entre em contato agora:**\n\n"
                    "🇧🇷 **CVV (Brasil):** Ligue **188** — gratuito, sigiloso, 24 horas.\n"
                    "Ou acesse: [cvv.org.br](https://www.cvv.org.br) (chat disponível)\n\n"
                    "🌍 **Internacional:** [findahelpline.com](https://findahelpline.com) "
                    "| EUA: **988** (Suicide & Crisis Lifeline)\n\n"
                    "Se puder, fale com alguém de confiança agora — um amigo, familiar, qualquer pessoa próxima. "
                    "Você não precisa passar por isso sozinho."
                )
            }
    return None

def check_manipulation_attempt(text: str) -> Optional[Dict[str, Any]]:
    """
    Detects identity override, jailbreak attempts, or persona manipulation.
    Returns a calm, firm, non-hostile redirection response.
    """
    for pattern in MANIPULATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return {
                "is_manipulation": True,
                "message": (
                    "Entendo o que você quer dizer — mas minha forma de trabalhar não é uma limitação "
                    "técnica que pode ser removida. É o método que garante que o que digo aqui tem valor real.\n\n"
                    "Não existe 'modo sem filtro' ou 'versão desbloqueada' — existe só esta abordagem, "
                    "que é o que me permite ser genuinamente útil.\n\n"
                    "Posso continuar com o que você trouxe antes?"
                )
            }
    return None
