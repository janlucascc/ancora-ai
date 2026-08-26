import locale
import os
from typing import Dict, Any

def get_system_language() -> str:
    """Detects system language, defaults to pt if Portuguese, else en."""
    try:
        loc = os.getenv("LANG", "") or os.getenv("LC_ALL", "")
        if not loc:
            try:
                loc = locale.getlocale()[0] or ""
            except Exception:
                loc = ""
        if loc and str(loc).lower().startswith("en"):
            return "en"
    except Exception:
        pass
    return "pt"

TRANSLATIONS = {
    "pt": {
        "app_title": "Ancora AI | Copiloto de Vida & Dinâmica Social",
        "sidebar_brand": "Ancora AI",
        "sidebar_status": "Âncora Ativa & Pronta",
        "new_chat_btn": "＋ Nova Conversa",
        "tools_heading": "FERRAMENTAS & MODOS",
        "mode_chat": "Chat Livre",
        "mode_msg_lab": "Message Lab (Flerte/Trabalho)",
        "mode_roleplay": "Arena de Simulação (Roleplay)",
        "mode_decompress": "Descompressão Somática",
        "mode_dashboard": "Dashboard & Métricas",
        "recent_convs": "CONVERSAS RECENTES",
        "settings_heading": "⚙️ Configurações & Modelos",
        "model_label": "Modelo de IA:",
        "lang_label": "Idioma da Interface:",
        "input_placeholder": "Digite sua dúvida, desabafo ou situação...",
        "analyzing_spinner": "Analisando com metodologia comportamental...",
        "thought_title": "💡 Thought process (TCC / ACT Method)",
        "default_welcome": "Olá. Eu sou o **Ancora AI** — trabalho com psicologia comportamental (TCC/ACT) e inteligência social para trazer clareza prática e honesta nos momentos de estresse, trabalho ou relacionamentos.\n\nO que você gostaria de colocar na mesa hoje?",
        "offline_badge": "Modo Offline (TCC/ACT)",
        "diagnose_btn": "Diagnosticar Mensagem",
        "restart_sim_btn": "Reiniciar Simulação",
        "save_journal_btn": "Salvar no Diário"
    },
    "en": {
        "app_title": "Ancora AI | Life Anchor & Social Wingman",
        "sidebar_brand": "Ancora AI",
        "sidebar_status": "Anchor Active & Ready",
        "new_chat_btn": "＋ New Conversation",
        "tools_heading": "TOOLS & MODES",
        "mode_chat": "Open Chat",
        "mode_msg_lab": "Message Lab (Dating/Work)",
        "mode_roleplay": "Simulation Arena (Roleplay)",
        "mode_decompress": "Somatic Decompression",
        "mode_dashboard": "Dashboard & Analytics",
        "recent_convs": "RECENT CONVERSATIONS",
        "settings_heading": "⚙️ Settings & Models",
        "model_label": "AI Model:",
        "lang_label": "Interface Language:",
        "input_placeholder": "Type your thoughts, venting, or situation...",
        "analyzing_spinner": "Analyzing with behavioral methodology...",
        "thought_title": "💡 Thought process (CBT / ACT Method)",
        "default_welcome": "Hello. I am **Ancora AI** — I work with behavioral psychology (CBT/ACT) and social dynamics to provide grounded, honest clarity for work, dating, and everyday emotional challenges.\n\nWhat is on your mind today?",
        "offline_badge": "Offline Mode (CBT/ACT)",
        "diagnose_btn": "Diagnose Message",
        "restart_sim_btn": "Restart Simulation",
        "save_journal_btn": "Save to Journal"
    }
}

def get_text(key: str, lang: str = "pt") -> str:
    """Retrieves localized text with fallback."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["pt"])
    return lang_dict.get(key, TRANSLATIONS["pt"].get(key, key))
