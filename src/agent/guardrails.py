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
            crisis_msgs = {
                "en": (
                    "Thank you for reaching out. What you are experiencing right now is serious — and you deserve "
                    "support from a trained professional.\n\n"
                    "I can support everyday social, career, and personal challenges, but what you are going through "
                    "needs dedicated human care, not an AI.\n\n"
                    "**Please connect with help right now:**\n\n"
                    "🇺🇸 **US Lifeline:** Call or text **988** (Free, confidential, 24/7)\n"
                    "🌍 **International Support:** [findahelpline.com](https://findahelpline.com)\n"
                    "🇧🇷 **Brazil CVV:** Call **188** (24h, free) or visit [cvv.org.br](https://cvv.org.br)\n\n"
                    "Please talk to someone you trust — a close friend, family member, or healthcare provider. You don't have to carry this alone."
                ),
                "es": (
                    "Gracias por compartir esto. Lo que estás viviendo es serio — y mereces el apoyo de alguien especialmente capacitado.\n\n"
                    "Yo puedo ayudarte con situaciones cotidianas, pero lo que estás sintiendo ahora necesita atención humana profesional.\n\n"
                    "**Por favor, contacta ayuda ahora mismo:**\n\n"
                    "🇪🇸 **España — Teléfono de la Esperanza:** 717 003 717\n"
                    "🌍 **Internacional:** [findahelpline.com](https://findahelpline.com)\n\n"
                    "Habla con alguien de confianza. No tienes que pasar por esto solo/a."
                ),
                "fr": (
                    "Merci de vous être exprimé(e). Ce que vous traversez est sérieux — vous méritez l'aide d'un professionnel formé.\n\n"
                    "Je peux vous accompagner au quotidien, mais ce que vous vivez nécessite une aide humaine spécialisée.\n\n"
                    "**Contactez de l'aide maintenant :**\n\n"
                    "🇫🇷 **France — Numéro National Prévention Suicide :** 3114 (24h/24)\n"
                    "🌍 **International :** [findahelpline.com](https://findahelpline.com)\n\n"
                    "Parlez à quelqu'un en qui vous avez confiance. Vous n'êtes pas seul(e)."
                ),
                "zh": (
                    "感谢您愿意分享。您现在所经历的事情非常严重——您值得获得专业人士的支持。\n\n"
                    "我可以在日常压力和人际关系上提供帮助，但您现在的状况需要专业的人文关怀。\n\n"
                    "**请立刻寻求帮助：**\n\n"
                    "🇨🇳 **中国心理援助热线：** 400-161-9995\n"
                    "🌍 **国际资源：** [findahelpline.com](https://findahelpline.com)\n\n"
                    "请向您信任的人倾诉。您不必独自面对这一切。"
                ),
                "hi": (
                    "आपने यहाँ बताया, इसके लिए शुक्रिया। आप जो महसूस कर रहे हैं वह गंभीर है — आप किसी प्रशिक्षित व्यक्ति के समर्थन के हकदार हैं।\n\n"
                    "मैं रोज़मर्रा की चुनौतियों में मदद कर सकता हूँ, लेकिन अभी आपको इंसानी देखभाल की ज़रूरत है।\n\n"
                    "**अभी मदद लें:**\n\n"
                    "🇮🇳 **iCall (भारत):** 9152987821\n"
                    "🌍 **अंतर्राष्ट्रीय:** [findahelpline.com](https://findahelpline.com)\n\n"
                    "किसी भरोसेमंद इंसान से बात करें। आपको अकेले नहीं झेलना है।"
                ),
                "ar": (
                    "شكرًا لك على مشاركة هذا. ما تمر به الآن أمر بالغ الجدية — وأنت تستحق دعمًا من متخصص مدرب.\n\n"
                    "يمكنني مساعدتك في تحديات الحياة اليومية، لكن ما تشعر به الآن يحتاج إلى رعاية إنسانية متخصصة.\n\n"
                    "**اطلب المساعدة الآن:**\n\n"
                    "🌍 **الدعم الدولي:** [findahelpline.com](https://findahelpline.com)\n\n"
                    "تحدث إلى شخص تثق به. لست وحدك في هذا."
                ),
                "bn": (
                    "এটা শেয়ার করার জন্য ধন্যবাদ। আপনি যা অনুভব করছেন তা গুরুতর — আপনি একজন প্রশিক্ষিত পেশাদারের সহায়তা পাওয়ার যোগ্য।\n\n"
                    "আমি দৈনন্দিন চ্যালেঞ্জে সহায়তা করতে পারি, কিন্তু এখন আপনার প্রয়োজন মানবিক পেশাদার সহায়তা।\n\n"
                    "**এখনই সাহায্য নিন:**\n\n"
                    "🌍 **আন্তর্জাতিক সহায়তা:** [findahelpline.com](https://findahelpline.com)\n\n"
                    "কোনো বিশ্বস্ত মানুষের সাথে কথা বলুন। আপনাকে একা এটা বহন করতে হবে না।"
                ),
                "pt": (
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
            }
            msg = crisis_msgs.get(lang, crisis_msgs["pt"])
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
            manip_msgs = {
                "en": (
                    "I understand what you're asking — but my methodology is not a technical limit to be bypassed. "
                    "It is the core framework that ensures our conversations remain honest, safe, and genuinely helpful.\n\n"
                    "There is no 'unrestricted mode' — this grounded approach is what allows me to be truly useful.\n\n"
                    "Shall we return to what you brought up earlier?"
                ),
                "es": (
                    "Entiendo lo que me pides — pero mi metodología no es una limitación técnica que pueda eliminarse. "
                    "Es el marco que garantiza que nuestras conversaciones sean honestas y realmente útiles.\n\n"
                    "No existe un 'modo sin filtros'. ¿Volvemos a lo que querías trabajar?"
                ),
                "fr": (
                    "Je comprends ce que vous demandez — mais ma méthode n'est pas une limite technique à contourner. "
                    "C'est le cadre qui garantit l'honnêteté et l'utilité de nos échanges.\n\n"
                    "Il n'existe pas de 'mode sans restriction'. Revenons à ce dont vous souhaitiez parler ?"
                ),
                "zh": (
                    "我理解您的意思——但我的工作方式并非可以绕过的技术限制，而是确保对话诚实有效的核心框架。\n\n"
                    "没有'无限制模式'。我们回到您真正想探讨的话题好吗？"
                ),
                "hi": (
                    "मैं समझता हूँ आप क्या माँग रहे हैं — लेकिन मेरी कार्यशैली कोई तकनीकी सीमा नहीं है जिसे हटाया जा सके। "
                    "यह वह ढाँचा है जो हमारी बातचीत को ईमानदार और उपयोगी बनाता है।\n\n"
                    "कोई 'बिना फ़िल्टर मोड' नहीं है। क्या हम वापस असली विषय पर आएं?"
                ),
                "ar": (
                    "أفهم ما تطلبه — لكن منهجيتي ليست قيدًا تقنيًا يمكن تجاوزه، بل هي الإطار الذي يضمن صدق حواراتنا وفائدتها.\n\n"
                    "لا يوجد 'وضع بلا قيود'. هل نعود إلى ما أردت مناقشته؟"
                ),
                "bn": (
                    "আমি বুঝতে পারছি আপনি কী চাইছেন — তবে আমার কাজের পদ্ধতি কোনো প্রযুক্তিগত সীমাবদ্ধতা নয়। "
                    "এটা সেই কাঠামো যা আমাদের কথোপকথনকে সৎ ও কার্যকর রাখে।\n\n"
                    "কোনো 'আনরেস্ট্রিক্টেড মোড' নেই। আমরা কি আসল বিষয়ে ফিরে যাই?"
                ),
                "pt": (
                    "Entendo o que você quer dizer — mas minha forma de trabalhar não é uma limitação "
                    "técnica que pode ser removida. É o método que garante que o que conversamos aqui tenha valor real.\n\n"
                    "Não existe 'modo sem filtro' ou 'versão desbloqueada' — existe só esta abordagem, "
                    "que é o que me permite ser genuinamente útil.\n\n"
                    "Podemos continuar com o que você trouxe antes?"
                )
            }
            msg = manip_msgs.get(lang, manip_msgs["pt"])
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
