import locale
import os
from typing import Dict, Any

SUPPORTED_LANGUAGES = {
    "pt": {"name": "Português", "flag": "🇧🇷", "label": "Português (Brasil)"},
    "en": {"name": "English", "flag": "🇺🇸", "label": "English (US)"},
    "es": {"name": "Español", "flag": "🇪🇸", "label": "Español"},
    "fr": {"name": "Français", "flag": "🇫🇷", "label": "Français"},
    "zh": {"name": "中文", "flag": "🇨🇳", "label": "中文 (Mandarim)"},
    "hi": {"name": "हिन्दी", "flag": "🇮🇳", "label": "हिन्दी (Hindi)"},
    "ar": {"name": "العربية", "flag": "🇸🇦", "label": "العربية (Árabe)"},
    "bn": {"name": "বাংলা", "flag": "🇧🇩", "label": "বাংলা (Bengali)"}
}

def get_system_language() -> str:
    """Detects system language, defaults to pt if Portuguese, else en or matching ISO."""
    try:
        loc = os.getenv("LANG", "") or os.getenv("LC_ALL", "")
        if not loc:
            try:
                loc = locale.getlocale()[0] or ""
            except Exception:
                loc = ""
        loc_str = str(loc).lower()
        for code in ["pt", "en", "es", "fr", "zh", "hi", "ar", "bn"]:
            if loc_str.startswith(code):
                return code
    except Exception:
        pass
    return "pt"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
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
        "settings_heading": "⚙️ Configurações & Idioma",
        "model_label": "Modelo de IA:",
        "lang_label": "Idioma da Interface (8 Idiomas):",
        "input_placeholder": "Digite sua dúvida, desabafo ou situação...",
        "analyzing_spinner": "Processando análise comportamental...",
        "thought_title": "💡 Raciocínio & Metodologia TCC / ACT",
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
        "settings_heading": "⚙️ Settings & Language",
        "model_label": "AI Model:",
        "lang_label": "Interface Language (8 Languages):",
        "input_placeholder": "Type your thoughts, venting, or situation...",
        "analyzing_spinner": "Processing behavioral analysis...",
        "thought_title": "💡 Reasoning & CBT / ACT Methodology",
        "default_welcome": "Hello. I am **Ancora AI** — I work with behavioral psychology (CBT/ACT) and social dynamics to provide grounded, honest clarity for work, dating, and everyday emotional challenges.\n\nWhat is on your mind today?",
        "offline_badge": "Offline Mode (CBT/ACT)",
        "diagnose_btn": "Diagnose Message",
        "restart_sim_btn": "Restart Simulation",
        "save_journal_btn": "Save to Journal"
    },
    "es": {
        "app_title": "Ancora AI | Copiloto de Vida y Dinámica Social",
        "sidebar_brand": "Ancora AI",
        "sidebar_status": "Ancla Activa y Lista",
        "new_chat_btn": "＋ Nueva Conversación",
        "tools_heading": "HERRAMIENTAS Y MODOS",
        "mode_chat": "Chat Libre",
        "mode_msg_lab": "Laboratorio de Mensajes",
        "mode_roleplay": "Arena de Simulación (Roleplay)",
        "mode_decompress": "Descompresión Somática",
        "mode_dashboard": "Panel y Métricas",
        "recent_convs": "CONVERSACIONES RECIENTES",
        "settings_heading": "⚙️ Configuración e Idioma",
        "model_label": "Modelo de IA:",
        "lang_label": "Idioma de la Interfaz:",
        "input_placeholder": "Escribe lo que tienes en mente...",
        "analyzing_spinner": "Procesando análisis conductual...",
        "thought_title": "💡 Razonamiento y Metodología TCC / ACT",
        "default_welcome": "Hola. Soy **Ancora AI** — trabajo con psicología conductual y dinámica social para brindarte claridad honesta en momentos de estrés, trabajo o relaciones.\n\n¿Qué te gustaría abordar hoy?",
        "offline_badge": "Modo Offline (TCC/ACT)",
        "diagnose_btn": "Diagnosticar Mensaje",
        "restart_sim_btn": "Reiniciar Simulación",
        "save_journal_btn": "Guardar en Diario"
    },
    "fr": {
        "app_title": "Ancora AI | Copilote de Vie & Dynamique Sociale",
        "sidebar_brand": "Ancora AI",
        "sidebar_status": "Ancre Active & Prête",
        "new_chat_btn": "＋ Nouvelle Conversation",
        "tools_heading": "OUTILS & MODES",
        "mode_chat": "Chat Libre",
        "mode_msg_lab": "Laboratoire de Messages",
        "mode_roleplay": "Arène de Simulation",
        "mode_decompress": "Décompression Somatique",
        "mode_dashboard": "Tableau de Bord & Métriques",
        "recent_convs": "CONVERSATIONS RÉCENTES",
        "settings_heading": "⚙️ Paramètres & Langue",
        "model_label": "Modèle d'IA :",
        "lang_label": "Langue de l'interface :",
        "input_placeholder": "Écrivez votre pensée ou situation...",
        "analyzing_spinner": "Analyse comportementale en cours...",
        "thought_title": "💡 Raisonnement & Méthodologie TCC / ACT",
        "default_welcome": "Bonjour. Je suis **Ancora AI** — j'utilise la psychologie comportementale (TCC/ACT) pour apporter clarté et honnêteté dans vos relations et votre travail.\n\nDe quoi souhaitez-vous parler aujourd'hui ?",
        "offline_badge": "Mode Hors Ligne",
        "diagnose_btn": "Diagnostiquer le Message",
        "restart_sim_btn": "Redémarrer la Simulation",
        "save_journal_btn": "Enregistrer"
    },
    "zh": {
        "app_title": "Ancora AI | 情绪锚点与社交助手",
        "sidebar_brand": "Ancora AI",
        "sidebar_status": "锚点已激活就绪",
        "new_chat_btn": "＋ 新建对话",
        "tools_heading": "工具与模式",
        "mode_chat": "自由对话",
        "mode_msg_lab": "信息实验室",
        "mode_roleplay": "场景模拟演练",
        "mode_decompress": "身心减压调节",
        "mode_dashboard": "仪表板与数据",
        "recent_convs": "最近对话",
        "settings_heading": "⚙️ 设置与语言",
        "model_label": "AI 模型:",
        "lang_label": "界面语言:",
        "input_placeholder": "输入您的想法或困扰...",
        "analyzing_spinner": "正在进行行为心理分析...",
        "thought_title": "💡 思考过程与认知行为方法 (CBT/ACT)",
        "default_welcome": "您好。我是 **Ancora AI** — 基于行为心理学（CBT/ACT）与社交洞察，为您提供真实坦诚的思维锚点与压力疏导。\n\n今天有什么需要探讨的吗？",
        "offline_badge": "离线模式 (CBT/ACT)",
        "diagnose_btn": "分析诊断信息",
        "restart_sim_btn": "重新开始模拟",
        "save_journal_btn": "保存记录"
    },
    "hi": {
        "app_title": "Ancora AI | जीवन सहारा और सामाजिक साथी",
        "sidebar_brand": "Ancora AI",
        "sidebar_status": "सक्रिय और तैयार",
        "new_chat_btn": "＋ नई बातचीत",
        "tools_heading": "उपकरण और मोड",
        "mode_chat": "खुली बातचीत",
        "mode_msg_lab": "मैसेज लैब",
        "mode_roleplay": "अभ्यास अखाड़ा (रोलप्ले)",
        "mode_decompress": "तनाव मुक्ति अभ्यास",
        "mode_dashboard": "डैशबोर्ड और मेट्रिक्स",
        "recent_convs": "हाल की बातचीत",
        "settings_heading": "⚙️ सेटिंग्स और भाषा",
        "model_label": "एआई मॉडल:",
        "lang_label": "इंटरफ़ेस भाषा:",
        "input_placeholder": "अपने विचार या स्थिति लिखें...",
        "analyzing_spinner": "व्यवहार विश्लेषण जारी है...",
        "thought_title": "💡 सोच प्रक्रिया और सीबीटी / एसीटी पद्धति",
        "default_welcome": "नमस्ते। मैं **Ancora AI** हूँ — मैं जीवन, काम और रिश्तों में स्पष्टता और मानसिक स्थिरता लाने के लिए व्यावहारिक मनोविज्ञान का उपयोग करता हूँ।\n\nआज आपके मन में क्या है?",
        "offline_badge": "ऑफ़लाइन मोड",
        "diagnose_btn": "मैसेज का विश्लेषण करें",
        "restart_sim_btn": "पुनः प्रारंभ करें",
        "save_journal_btn": "डायरी में सहेजें"
    },
    "ar": {
        "app_title": "Ancora AI | مرساة الحياة والذكاء الاجتماعي",
        "sidebar_brand": "Ancora AI",
        "sidebar_status": "المرساة نشطة وجاهزة",
        "new_chat_btn": "＋ محادثة جديدة",
        "tools_heading": "الأدوات والأنماط",
        "mode_chat": "محادثة مفتوحة",
        "mode_msg_lab": "مختبر الرسائل",
        "mode_roleplay": "محاكاة المواقف الصعبة",
        "mode_decompress": "تفريغ التوتر الجسدي",
        "mode_dashboard": "لوحة البيانات والمقاييس",
        "recent_convs": "المحادثات الأخيرة",
        "settings_heading": "⚙️ الإعدادات واللغة",
        "model_label": "نموذج الذكاء الاصطناعي:",
        "lang_label": "لغة الواجهة:",
        "input_placeholder": "اكتب ما يدور في ذهنك الآن...",
        "analyzing_spinner": "جاري التحليل السلوكي النفسي...",
        "thought_title": "💡 مسار التفكير ومنهجية التوجيه السلوكي",
        "default_welcome": "مرحبًا. أنا **Ancora AI** — أعمل بمنهجية علم النفس السلوكي والذكاء الاجتماعي لتوفير الوضوح والاستقرار النفسي في مواقف العمل والعلاقات.\n\nما الذي تود طرحه اليوم؟",
        "offline_badge": "الوضع المحلي بدون اتصال",
        "diagnose_btn": "تحليل الرسالة",
        "restart_sim_btn": "إعادة تشغيل المحاكاة",
        "save_journal_btn": "حفظ في اليوميات"
    },
    "bn": {
        "app_title": "Ancora AI | জীবন সহায়ক ও সামাজিক উইংম্যান",
        "sidebar_brand": "Ancora AI",
        "sidebar_status": "সক্রিয় এবং প্রস্তুত",
        "new_chat_btn": "＋ নতুন কথোপকথন",
        "tools_heading": "টুলস ও মোড",
        "mode_chat": "উন্মুক্ত চ্যাট",
        "mode_msg_lab": "মেসেজ ল্যাব",
        "mode_roleplay": "সিমুলেশন অঙ্গন",
        "mode_decompress": "মানসিক চাপ মুক্তি",
        "mode_dashboard": "ড্যাশবোর্ড ও পরিসংখ্যান",
        "recent_convs": "সাম্প্রতিক চ্যাট",
        "settings_heading": "⚙️ সেটিংস ও ভাষা",
        "model_label": "এআই মডেল:",
        "lang_label": "ইন্টারফেস ভাষা:",
        "input_placeholder": "আপনার অনুভূতি বা পরিস্থিতি লিখুন...",
        "analyzing_spinner": "আচরণগত বিশ্লেষণ চলছে...",
        "thought_title": "💡 চিন্তার গতিপথ ও মনস্তাত্ত্বিক পদ্ধতি",
        "default_welcome": "নমস্কার। আমি **Ancora AI** — বাস্তবসম্মত মানসিক স্বচ্ছতা এবং সম্পর্কের ভারসাম্য বজায় রাখতে আচরণগত মনস্তত্ত্ব নিয়ে কাজ করি।\n\nআজ আপনি কী নিয়ে কথা বলতে চান?",
        "offline_badge": "অফলাইন মোড",
        "diagnose_btn": "মেসেজ বিশ্লেষণ করুন",
        "restart_sim_btn": "পুনরায় শুরু করুন",
        "save_journal_btn": "সংরক্ষণ করুন"
    }
}

def get_text(key: str, lang: str = "pt") -> str:
    """Retrieves localized text with fallback to Portuguese/English."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["pt"])
    return lang_dict.get(key, TRANSLATIONS["pt"].get(key, key))
