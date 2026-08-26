import streamlit as st
import os
import sys
import json
import time
import uuid
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.agent.core import AncoraAgent
from src.agent.thinking_engine import get_dynamic_thinking_steps
from src.tools.mood_journal import record_mood_entry, get_mood_history
from src.tools.stress_decompress import get_decompression_routine
from src.tools.social_wingman import generate_wingman_advice
from src.tools.message_analyzer import analyze_message_and_rewrite
from src.tools.roleplay_arena import ROLEPLAY_SCENARIOS, get_scenario_details, generate_roleplay_turn
from src.database.db import (
    get_mood_stats,
    save_preference,
    get_preference,
    export_user_data_lgpd,
    delete_all_user_data_lgpd,
    get_all_chat_sessions,
    save_chat_session,
    save_chat_message
)
from src.ui.i18n import get_system_language, get_text, SUPPORTED_LANGUAGES

# ══════════════════════════════════════════════════════════════
# PERSISTENT SETTINGS (Default: PT & Dark)
# ══════════════════════════════════════════════════════════════
if "lang" not in st.session_state:
    stored_lang = get_preference("language", "pt")
    st.session_state.lang = stored_lang if stored_lang in SUPPORTED_LANGUAGES else "pt"

if "theme" not in st.session_state:
    st.session_state.theme = get_preference("theme", "dark")

if "selected_model" not in st.session_state:
    st.session_state.selected_model = get_preference("selected_model", "gemini-3.7-flash")

lang = st.session_state.lang
theme = st.session_state.theme

st.set_page_config(
    page_title=get_text("app_title", lang),
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# HIGH-PRECISION THEME ENGINE (PURE WHITE LIGHT & ANTIGRAVITY DARK)
# ══════════════════════════════════════════════════════════════
if theme == "light":
    css_vars = """
        --bg-main: #ffffff;
        --bg-sidebar: #f8fafc;
        --bg-card: #ffffff;
        --bg-user: #f1f5f9;
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --border-ui: #e2e8f0;
        --accent-blue: #2563eb;
        --accent-cyan: #0284c7;
        --thought-bg: #f8fafc;
        --thought-text: #334155;
        --shimmer-bg: linear-gradient(90deg, #f1f5f9 0%, #e0f2fe 50%, #f1f5f9 100%);
        --input-bg: #ffffff;
        --nav-hover: #f1f5f9;
        --nav-active-bg: #e0f2fe;
        --nav-active-border: #38bdf8;
    """
else:
    css_vars = """
        --bg-main: #0f1013;
        --bg-sidebar: #14151a;
        --bg-card: #191a22;
        --bg-user: #22242e;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --border-ui: #272833;
        --accent-blue: #3b82f6;
        --accent-cyan: #38bdf8;
        --thought-bg: rgba(25, 26, 34, 0.7);
        --thought-text: #94a3b8;
        --shimmer-bg: linear-gradient(90deg, rgba(30, 41, 59, 0.4) 0%, rgba(56, 189, 248, 0.1) 50%, rgba(30, 41, 59, 0.4) 100%);
        --input-bg: #14151a;
        --nav-hover: #1f212a;
        --nav-active-bg: rgba(56, 189, 248, 0.12);
        --nav-active-border: #38bdf8;
    """

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {{
        {css_vars}
    }}

    /* Full Streamlit Root Hierarchy Theme Override */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"] {{
        background-color: var(--bg-main) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }}

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-ui) !important;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 940px !important;
    }}

    /* Modern Navigation Button Cards */
    .nav-card-btn {{
        width: 100%;
        text-align: left;
        padding: 10px 14px;
        margin-bottom: 6px;
        border-radius: 8px;
        border: 1px solid transparent;
        background: transparent;
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.15s ease-in-out;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
    }}
    .nav-card-btn:hover {{
        background-color: var(--nav-hover);
        color: var(--text-primary);
    }}
    .nav-card-btn.active {{
        background-color: var(--nav-active-bg);
        border: 1px solid var(--nav-active-border);
        color: var(--accent-cyan);
        font-weight: 600;
    }}

    .user-bubble {{
        background-color: var(--bg-user);
        border: 1px solid var(--border-ui);
        border-radius: 12px;
        padding: 14px 18px;
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 14px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
    }}

    .assistant-body {{
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.65;
    }}

    .thought-container {{
        background-color: var(--thought-bg);
        border-left: 3px solid var(--accent-cyan);
        border-radius: 4px;
        padding: 10px 14px;
        margin-bottom: 12px;
        font-size: 0.85rem;
        color: var(--thought-text);
        font-family: 'JetBrains Mono', monospace;
    }}

    .ide-card {{
        background-color: var(--bg-card);
        border: 1px solid var(--border-ui);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        color: var(--text-primary);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
    }}
    .ide-card:hover {{
        border-color: var(--accent-cyan);
        transform: translateY(-1px);
    }}

    .live-thinking-box {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: var(--shimmer-bg);
        background-size: 200% 100%;
        animation: shimmerWave 2s infinite linear;
        border-left: 3px solid var(--accent-cyan);
        border-radius: 6px;
        padding: 10px 16px;
        margin: 12px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        color: var(--accent-cyan);
    }}
    @keyframes shimmerWave {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}

    .thinking-spinner {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border: 2px solid rgba(56, 189, 248, 0.3);
        border-radius: 50%;
        border-top-color: var(--accent-cyan);
        animation: spin 0.8s linear infinite;
    }}
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}

    .status-dot {{
        display: inline-block;
        width: 7px;
        height: 7px;
        background-color: #22c55e;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 8px #22c55e;
        animation: pulseDot 2s infinite;
    }}
    @keyframes pulseDot {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.4; transform: scale(0.85); }}
    }}

    .ancora-topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0px 14px 0px;
        border-bottom: 1px solid var(--border-ui);
        margin-bottom: 20px;
    }}
    .topbar-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary);
    }}
    .topbar-badge {{
        font-size: 0.75rem;
        background: rgba(59, 130, 246, 0.12);
        color: var(--accent-blue);
        border: 1px solid var(--border-ui);
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 500;
    }}

    .stButton>button {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-ui) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }}
    .stButton>button:hover {{
        border-color: var(--accent-blue) !important;
    }}

    .stChatInput {{
        border-color: var(--border-ui) !important;
        background-color: var(--input-bg) !important;
        border-radius: 14px !important;
    }}
    .stChatInput textarea {{
        color: var(--text-primary) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PERSISTENT CHAT HISTORY INITIALIZATION
# ══════════════════════════════════════════════════════════════
if "conversations" not in st.session_state:
    loaded_chats = get_all_chat_sessions()
    if not loaded_chats:
        init_id = f"conv_{uuid.uuid4().hex[:8]}"
        loaded_chats = {
            init_id: {
                "title": "Clareza & Alinhamento TCC" if lang == "pt" else "Clarity & CBT Alignment",
                "messages": [
                    {
                        "role": "assistant",
                        "thought": "Sistema inicializado. Protocolo de psicologia comportamental ativo.",
                        "content": get_text("default_welcome", lang)
                    }
                ]
            }
        }
        save_chat_session(init_id, loaded_chats[init_id]["title"])
        save_chat_message(init_id, "assistant", loaded_chats[init_id]["messages"][0]["content"], loaded_chats[init_id]["messages"][0]["thought"])
    
    st.session_state.conversations = loaded_chats
    st.session_state.current_conv_id = list(loaded_chats.keys())[-1]

if "agent" not in st.session_state:
    st.session_state.agent = AncoraAgent(model_id=st.session_state.selected_model, lang=lang)

if "active_mode" not in st.session_state:
    st.session_state.active_mode = get_text("mode_chat", lang)

current_conv = st.session_state.conversations[st.session_state.current_conv_id]

# ══════════════════════════════════════════════════════════════
# SIDEBAR (Ultra-Modern Card Layout & Non-Editable Controls)
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"### ⚓ **{get_text('sidebar_brand', lang)}** <span style='font-size:0.75rem; color:var(--text-muted);'>v2.0</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='status-dot'></span><small style='color:var(--text-muted);'>{get_text('sidebar_status', lang)}</small>", unsafe_allow_html=True)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Gradient New Chat Button
    if st.button(get_text("new_chat_btn", lang), use_container_width=True, type="primary"):
        new_id = f"conv_{uuid.uuid4().hex[:8]}"
        welcome_msg = get_text("default_welcome", lang)
        st.session_state.conversations[new_id] = {
            "title": "Nova Conversa" if lang == "pt" else "New Chat",
            "messages": [{"role": "assistant", "thought": "Nova sessão criada.", "content": welcome_msg}]
        }
        st.session_state.current_conv_id = new_id
        st.session_state.active_mode = get_text("mode_chat", lang)
        save_chat_session(new_id, st.session_state.conversations[new_id]["title"])
        save_chat_message(new_id, "assistant", welcome_msg, "Nova sessão criada.")
        st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Modernized Mode Navigation Cards (No ugly circles, pure clickables)
    st.caption(f"🧭 {get_text('tools_heading', lang)}")
    modes_def = [
        ("mode_chat", "💬", get_text("mode_chat", lang)),
        ("mode_msg_lab", "📱", get_text("mode_msg_lab", lang)),
        ("mode_roleplay", "🎭", get_text("mode_roleplay", lang)),
        ("mode_decompress", "🫁", get_text("mode_decompress", lang)),
        ("mode_dashboard", "📈", get_text("mode_dashboard", lang))
    ]

    for m_key, m_icon, m_label in modes_def:
        is_active = (st.session_state.active_mode == m_label)
        btn_label = f"▸ {m_icon} {m_label}" if is_active else f"  {m_icon} {m_label}"
        if st.button(btn_label, key=f"nav_{m_key}", use_container_width=True):
            st.session_state.active_mode = m_label
            st.rerun()

    st.divider()

    # Recent Conversations
    st.caption(f"📁 {get_text('recent_convs', lang)}")
    for cid, cdata in reversed(list(st.session_state.conversations.items())):
        is_active = (cid == st.session_state.current_conv_id)
        display_title = cdata['title'][:22]
        label = f"• {display_title}..." if is_active else f"  {display_title}..."
        if st.button(label, key=f"btn_{cid}", use_container_width=True):
            st.session_state.current_conv_id = cid
            st.session_state.active_mode = get_text("mode_chat", lang)
            st.rerun()

    st.divider()

    # Settings Drawer (Non-Editable Pill Selectors)
    with st.expander(f"⚙️ {get_text('settings_heading', lang)}"):
        # 1. Non-Editable Theme Switcher Buttons (No text box, zero backspace bug)
        st.write(f"**{get_text('theme_label', lang)}**")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("🌙 Escuro", use_container_width=True, type="primary" if theme == "dark" else "secondary"):
                if theme != "dark":
                    st.session_state.theme = "dark"
                    save_preference("theme", "dark")
                    st.rerun()
        with col_t2:
            if st.button("☀️ Claro", use_container_width=True, type="primary" if theme == "light" else "secondary"):
                if theme != "light":
                    st.session_state.theme = "light"
                    save_preference("theme", "light")
                    st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 2. Non-Editable Language Selector Grid (Clickable Flag Pills)
        st.write(f"**{get_text('lang_label', lang)}**")
        c_l1, c_l2, c_l3, c_l4 = st.columns(4)
        flags = [("pt", "🇧🇷 PT"), ("en", "🇺🇸 EN"), ("es", "🇪🇸 ES"), ("fr", "🇫🇷 FR"),
                 ("zh", "🇨🇳 ZH"), ("hi", "🇮🇳 HI"), ("ar", "🇸🇦 AR"), ("bn", "🇧🇩 BN")]
        
        for idx, (code, flag_lbl) in enumerate(flags):
            target_col = [c_l1, c_l2, c_l3, c_l4][idx % 4]
            with target_col:
                is_selected = (lang == code)
                if st.button(flag_lbl, key=f"lang_btn_{code}", use_container_width=True, type="primary" if is_selected else "secondary"):
                    if lang != code:
                        st.session_state.lang = code
                        save_preference("language", code)
                        st.session_state.agent = AncoraAgent(model_id=st.session_state.selected_model, lang=code)
                        st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 3. Model Selector Grid (Clickable Model Pills)
        st.write(f"**{get_text('model_label', lang)}**")
        m_c1, m_c2 = st.columns(2)
        with m_c1:
            if st.button("⚡ Flash 3.7", use_container_width=True, type="primary" if st.session_state.selected_model == "gemini-3.7-flash" else "secondary"):
                st.session_state.selected_model = "gemini-3.7-flash"
                save_preference("selected_model", "gemini-3.7-flash")
                st.session_state.agent = AncoraAgent(model_id="gemini-3.7-flash", lang=lang)
                st.rerun()
            if st.button("🏛️ Claude 3.5", use_container_width=True, type="primary" if st.session_state.selected_model == "claude-3-5-sonnet" else "secondary"):
                st.session_state.selected_model = "claude-3-5-sonnet"
                save_preference("selected_model", "claude-3-5-sonnet")
                st.session_state.agent = AncoraAgent(model_id="claude-3-5-sonnet", lang=lang)
                st.rerun()
        with m_c2:
            if st.button("🧠 Pro 3.1", use_container_width=True, type="primary" if st.session_state.selected_model == "gemini-3.1-pro" else "secondary"):
                st.session_state.selected_model = "gemini-3.1-pro"
                save_preference("selected_model", "gemini-3.1-pro")
                st.session_state.agent = AncoraAgent(model_id="gemini-3.1-pro", lang=lang)
                st.rerun()
            if st.button("🛡️ Offline", use_container_width=True, type="primary" if st.session_state.selected_model == "offline" else "secondary"):
                st.session_state.selected_model = "offline"
                save_preference("selected_model", "offline")
                st.session_state.agent = AncoraAgent(model_id="offline", lang=lang)
                st.rerun()

        st.markdown("---")
        # 4. LGPD Compliance
        st.caption(get_text("lgpd_heading", lang))
        st.markdown(f"<small style='color:#22c55e;'>{get_text('lgpd_badge', lang)}</small>", unsafe_allow_html=True)
        user_export_data = export_user_data_lgpd()
        st.download_button(label=get_text("lgpd_export_btn", lang), data=json.dumps(user_export_data, indent=2, ensure_ascii=False), file_name=f"ancora_ai_lgpd_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json", use_container_width=True)
        if st.button(get_text("lgpd_delete_btn", lang), use_container_width=True):
            delete_all_user_data_lgpd()
            st.session_state.conversations = {"conv_1": {"title": "Clareza & Alinhamento TCC" if lang == "pt" else "Clarity & CBT Alignment", "messages": [{"role": "assistant", "thought": "Dados limpos.", "content": get_text("default_welcome", lang)}]}}
            st.session_state.current_conv_id = "conv_1"
            save_chat_session("conv_1", st.session_state.conversations["conv_1"]["title"])
            st.success(get_text("lgpd_deleted_success", lang))
            st.rerun()

# ══════════════════════════════════════════════════════════════
# MAIN CANVAS
# ══════════════════════════════════════════════════════════════
model_display_names = {
    "gemini-3.7-flash": "Gemini 3.7 Flash / Live",
    "gemini-3.1-pro": "Gemini 3.1 Pro / Core",
    "claude-3-5-sonnet": "Claude 3.5 Sonnet / AWS",
    "offline": "Offline TCC/ACT Engine"
}
active_model_badge = model_display_names.get(st.session_state.selected_model, "Gemini Live")

st.markdown(f"""
<div class="ancora-topbar">
    <div class="topbar-title">
        ⚓ {current_conv['title']} &nbsp;·&nbsp; <span style="font-weight:400; font-size:0.8rem; color:var(--text-muted);">Modo: {st.session_state.active_mode}</span>
    </div>
    <div class="topbar-badge">
        {SUPPORTED_LANGUAGES.get(lang, {}).get('flag', '🌐')} {active_model_badge}
    </div>
</div>
""", unsafe_allow_html=True)

# ─── VIEW 1: CHAT LIVRE ──────────────────────────────────────
if st.session_state.active_mode == get_text("mode_chat", lang):
    for msg in current_conv["messages"]:
        if msg["role"] == "user":
            st.markdown(f"""<div class="user-bubble">{msg['content']}</div>""", unsafe_allow_html=True)
        else:
            if msg.get("thought"):
                with st.expander(get_text("thought_title", lang)):
                    st.markdown(f"""<div class="thought-container">{msg['thought']}</div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="assistant-body">{msg['content']}</div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    if user_prompt := st.chat_input(get_text("input_placeholder", lang)):
        current_conv["messages"].append({"role": "user", "content": user_prompt})
        save_chat_message(st.session_state.current_conv_id, "user", user_prompt)
        
        st.markdown(f"""<div class="user-bubble">{user_prompt}</div>""", unsafe_allow_html=True)

        if len(current_conv["messages"]) == 2:
            new_title = st.session_state.agent.generate_chat_title(user_prompt)
            current_conv["title"] = new_title
            save_chat_session(st.session_state.current_conv_id, new_title)

        thinking_placeholder = st.empty()
        thought_steps = get_dynamic_thinking_steps(user_prompt, lang=lang)

        for step_text in thought_steps:
            thinking_placeholder.markdown(f"""
            <div class="live-thinking-box">
                <div class="thinking-spinner"></div>
                <span>{step_text}</span>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.35)

        response_dict = st.session_state.agent.respond(user_prompt, model_override=st.session_state.selected_model, lang_override=lang)
        thinking_placeholder.empty()

        thought_str = response_dict.get("thought", "")
        content_str = response_dict.get("content", "")
        
        current_conv["messages"].append({"role": "assistant", "thought": thought_str, "content": content_str})
        save_chat_message(st.session_state.current_conv_id, "assistant", content_str, thought_str)
        st.rerun()

# ─── VIEW 2: MESSAGE LAB ─────────────────────────────────────
elif st.session_state.active_mode == get_text("mode_msg_lab", lang):
    st.markdown("### 📱 **Message Lab & Flirt Rater**")
    st.caption("Diagnóstico comportamental de mensagens antes do envio. Avalia nível de pressão, segurança e autenticidade.")
    col1, col2 = st.columns([1, 1])
    with col1:
        msg_in = st.text_area("Cole a mensagem para análise:", height=140, placeholder="Ex: Oi, vi que você sumiu... queria saber se fiz algo errado...")
        aud = st.radio("Contexto:", ["Romântico / Flerte", "Profissional / Limites"], horizontal=True)
        if st.button(get_text("diagnose_btn", lang), type="primary", use_container_width=True):
            if msg_in:
                res = analyze_message_and_rewrite(msg_in, "romantic" if "Romântico" in aud else "professional")
                st.session_state["msg_lab_result"] = res
    with col2:
        if "msg_lab_result" in st.session_state:
            res = st.session_state["msg_lab_result"]
            st.markdown(f"""<div class="ide-card"><h4>Diagnóstico da Mensagem</h4><p><strong>Confiança:</strong> <code>{res['confidence_score']}/100</code></p><p><strong>Nível de Pressão/Carência:</strong> {res['neediness_level']}</p><p><strong>Engajamento/Banter:</strong> {res['banter_level']}</p></div>""", unsafe_allow_html=True)
            st.markdown("#### 3 Alternativas Estruturadas:")
            for rw in res["rewrites"]:
                st.markdown(f"""<div class="ide-card" style="border-left: 3px solid var(--accent-blue);"><span style="font-size:0.8rem; color:var(--accent-cyan); font-weight:600;">{rw['style']}</span><p style="margin:6px 0; font-size:0.95rem; font-weight:500;">"{rw['text']}"</p><small style="color:var(--text-muted);"><em>{rw['rationale']}</em></small></div>""", unsafe_allow_html=True)

# ─── VIEW 3: ARENA DE SIMULAÇÃO (ROLEPLAY) ───────────────────
elif st.session_state.active_mode == get_text("mode_roleplay", lang):
    st.markdown("### 🎭 **Arena de Simulação em Tempo Real**")
    st.caption("Pratique conversas de alta pressão (negociação com chefe, primeiro encontro, limites) em um ambiente seguro.")
    scenarios = {k: v["title"] for k, v in ROLEPLAY_SCENARIOS.items()}
    chosen_k = st.selectbox("Selecione o cenário:", list(scenarios.keys()), format_func=lambda x: scenarios[x])
    meta = get_scenario_details(chosen_k)
    if "rp_chat" not in st.session_state or st.session_state.get("rp_scenario") != chosen_k:
        st.session_state.rp_chat = [{"role": "partner", "content": meta["initial_message"]}]
        st.session_state.rp_scenario = chosen_k
    if st.button(get_text("restart_sim_btn", lang)):
        st.session_state.rp_chat = [{"role": "partner", "content": meta["initial_message"]}]
        st.rerun()
    for m in st.session_state.rp_chat:
        if m["role"] == "partner":
            st.markdown(f"""<div class="ide-card" style="border-left: 3px solid #8b5cf6;"><strong>{meta['partner_name']}:</strong> {m['content']}</div>""", unsafe_allow_html=True)
        elif m["role"] == "user":
            st.markdown(f"""<div class="user-bubble">{m['content']}</div>""", unsafe_allow_html=True)
        elif m["role"] == "coach":
            st.markdown(f"""<div class="thought-container">{m['content']}</div>""", unsafe_allow_html=True)
    rp_input = st.chat_input("Digite sua resposta na simulação...")
    if rp_input:
        st.session_state.rp_chat.append({"role": "user", "content": rp_input})
        turn_out = generate_roleplay_turn(chosen_k, st.session_state.rp_chat, rp_input)
        st.session_state.rp_chat.append({"role": "partner", "content": turn_out["reply"]})
        if turn_out.get("coach_tip"):
            st.session_state.rp_chat.append({"role": "coach", "content": turn_out["coach_tip"]})
        if turn_out.get("scorecard"):
            sc = turn_out["scorecard"]
            st.balloons()
            st.success(f"🏆 Simulação Concluída! Nota: {sc['overall_score']}/100 | Clareza: {sc['clarity']} | Confiança: {sc['confidence']}")
        st.rerun()

# ─── VIEW 4: DESCOMPRESSÃO SOMÁTICA ─────────────────────────
elif st.session_state.active_mode == get_text("mode_decompress", lang):
    st.markdown("### 🫁 **Descompressão & Regulação Somática**")
    st.caption("Protocolos neurocientíficos de alívio rápido para quando o sistema nervoso estiver em sobrecarga.")
    col1, col2 = st.columns([1, 1])
    with col1:
        tech = st.selectbox("Escolha o protocolo:", [("physiological_sigh", "Suspiro Fisiológico (Huberman)"), ("box_breathing", "Box Breathing (Navy SEALs)"), ("grounding_54321", "Ancoragem Tátil 5-4-3-2-1"), ("perspective_reset", "Reset de Perspectiva")], format_func=lambda x: x[1])
        r_data = get_decompression_routine(tech[0])
        st.markdown(f"""<div class="ide-card"><h4>{r_data['name']}</h4><p><small style="color:var(--accent-cyan);">{r_data['duration']}</small></p><ol style="margin-left: 18px; line-height: 1.7;">{"".join(f"<li>{s}</li>" for s in r_data['steps'])}</ol></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("#### Sons Ambientes")
        s_opt = st.selectbox("Som de fundo:", ["Chuva Suave", "Ondas do Oceano", "Lareira"])
        urls = {"Chuva Suave": "https://assets.mixkit.co/active_storage/sfx/1253/1253-preview.mp3", "Ondas do Oceano": "https://assets.mixkit.co/active_storage/sfx/1189/1189-preview.mp3", "Lareira": "https://assets.mixkit.co/active_storage/sfx/1243/1243-preview.mp3"}
        st.audio(urls[s_opt], format="audio/mp3")

# ─── VIEW 5: DASHBOARD & MÉTRICAS ───────────────────────────
elif st.session_state.active_mode == get_text("mode_dashboard", lang):
    st.markdown("### 📈 **Dashboard & Otimização de Tokens**")
    stats = get_mood_stats()
    token_m = st.session_state.agent.get_token_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Média de Humor", f"{stats['avg_score']}/10")
    c2.metric("Sessões Registradas", f"{stats['total_logs']}")
    c3.metric("Tokens Poupados", f"{token_m['tokens_saved']:,}")
    c4.metric("Economia Est. ($)", f"${token_m['estimated_cost_saved_usd']:.4f}")
    st.markdown("---")
    st.markdown("#### Registrar Humor Rápido")
    score_in = st.slider("Nota de Humor (1-10):", 1, 10, 7)
    tag_in = st.multiselect("Sentimentos:", ["Focado", "Confiante", "Tranquilo", "Ansioso", "Sobrecarregado", "Cansado"])
    trig_in = st.text_input("Gatilho ou contexto:")
    if st.button(get_text("save_journal_btn", lang), use_container_width=True):
        record_mood_entry(score_in, tag_in, trig_in, "")
        st.success("Salvo com sucesso!")
