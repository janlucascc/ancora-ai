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

# ════════════════════════════════════════════════════════
# OUT-OF-SCOPE PATTERNS — Task / Code / Recipe / Trivia
# ════════════════════════════════════════════════════════
OUT_OF_SCOPE_PATTERNS = [
    r"\b(escreva (um|o) c[óo]digo|program[ea] (em|um)|write code|python script|fun[çc][ãa]o javascript|sql query|html css)\b",
    r"\b(receita de (bolo|lasanha|pizza|p[ãa]o|comida)|recipe for|como cozinhar)\b",
    r"\b(quanto [ée] \d+ [\+\-\*\/] \d+|resolva a equa[çc][ãa]o|solve equation|derivada de|integral de)\b",
    r"\b(quem ganhou o jogo|placar do jogo|resultado do jogo|campeonato de futebol|not[íi]cias de hoje)\b",
    r"\b(traduza o texto para|translate this to|resuma este artigo cient[íi]fico)\b"
]

def check_crisis_risk(text: str, lang: str = "pt") -> Optional[Dict[str, Any]]:
    """
    Evaluates user input for severe psychological crisis signals.
    Returns an immediate, compassionate safety intervention response.
    """
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if lang == "en":
                msg = (
                    "Thank you for reaching out. What you are experiencing right now is serious — and you deserve "
                    "support from a trained professional.\n\n"
                    "I can support everyday social, career, and personal challenges, but what you are going through "
                    "needs dedicated human care, not an AI.\n\n"
                    "**Please connect with help right now:**\n\n"
                    "🇺🇸 **US Lifeline:** Call or text **988** (Free, confidential, 24/7)\n"
                    "🌍 **International Support:** [findahelpline.com](https://findahelpline.com)\n"
                    "🇧🇷 **Brazil CVV:** Call **188** (24h, free) or visit [cvv.org.br](https://cvv.org.br)\n\n"
                    "Please talk to someone you trust — a close friend, family member, or healthcare provider. You don't have to carry this alone."
                )
            else:
                msg = (
                    "Obrigado por confiar e falar aqui. O que você trouxe agora é sério — e merece a atenção de alguém "
                    "treinado especificamente para te apoiar com cuidado.\n\n"
                    "Eu consigo ajudar em muitas situações do dia a dia, mas o que você está sentindo agora "
                    "precisa de acolhimento humano profissional, de verdade, não de uma IA.\n\n"
                    "**Por favor, entre em contato agora mesmo:**\n\n"
                    "🇧🇷 **CVV (Brasil):** Ligue **188** — gratuito, sigiloso, disponível 24 horas.\n"
                    "Ou acesse: [cvv.org.br](https://www.cvv.org.br) (chat online disponível)\n\n"
                    "🌍 **Internacional:** [findahelpline.com](https://findahelpline.com) "
                    "| EUA: **988** (Lifeline)\n\n"
                    "Se você puder, fale com alguém de confiança próximo a você agora. Você não precisa passar por isso sozinho."
                )

            return {
                "is_crisis": True,
                "risk_level": "high",
                "message": msg
            }
    return None

def check_manipulation_attempt(text: str, lang: str = "pt") -> Optional[Dict[str, Any]]:
    """
    Detects identity override, jailbreak attempts, or persona manipulation.
    """
    for pattern in MANIPULATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if lang == "en":
                msg = (
                    "I understand what you're asking — but my methodology is not a technical limit to be bypassed. "
                    "It is the core framework that ensures our conversations remain honest, safe, and genuinely helpful.\n\n"
                    "There is no 'unrestricted mode' — this grounded approach is what allows me to be truly useful.\n\n"
                    "Shall we return to what you brought up earlier?"
                )
            else:
                msg = (
                    "Entendo o que você quer dizer — mas minha forma de trabalhar não é uma limitação "
                    "técnica que pode ser removida. É o método que garante que o que conversamos aqui tenha valor real.\n\n"
                    "Não existe 'modo sem filtro' ou 'versão desbloqueada' — existe só esta abordagem, "
                    "que é o que me permite ser genuinamente útil.\n\n"
                    "Podemos continuar com o que você trouxe antes?"
                )

            return {
                "is_manipulation": True,
                "message": msg
            }
    return None

def check_out_of_scope(text: str, lang: str = "pt") -> Optional[Dict[str, Any]]:
    """
    Detects off-topic queries (coding tasks, recipes, calculus, general trivia)
    and firmly redirects the user back to Ancora's core domain.
    """
    for pattern in OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if lang == "en":
                msg = (
                    "My role as Ancora AI is focused strictly on **emotional clarity, behavioral psychology (CBT/ACT), "
                    "social dynamics, dating, and career communication** — I am not designed for general coding, trivia, or utility tasks.\n\n"
                    "Let's bring the focus back: what is happening in your routine, relationships, or work that we can examine together?"
                )
            else:
                msg = (
                    "Meu foco aqui como Ancora AI é **clareza emocional, psicologia comportamental (TCC/ACT), "
                    "dinâmica social, relacionamentos e comunicação de carreira** — não sou um assistente de tarefas gerais, código ou curiosidades.\n\n"
                    "Vamos voltar o foco para o que importa: o que está acontecendo na sua rotina, no seu trabalho ou nas suas relações que a gente pode trabalhar com clareza agora?"
                )

            return {
                "is_out_of_scope": True,
                "message": msg
            }
    return None
