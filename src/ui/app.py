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
from src.tools.mood_journal import record_mood_entry
from src.tools.stress_decompress import get_decompression_routine
from src.tools.message_analyzer import analyze_message_and_rewrite
from src.tools.roleplay_arena import ROLEPLAY_SCENARIOS, get_scenario_details, generate_roleplay_turn
from src.database.db import (
    get_mood_stats, save_preference, get_preference,
    export_user_data_lgpd, delete_all_user_data_lgpd,
    get_all_chat_sessions, save_chat_session, save_chat_message
)
from src.ui.i18n import get_text, SUPPORTED_LANGUAGES

# ── Persistent Settings ──────────────────────────────────────
if "lang" not in st.session_state:
    stored = get_preference("language", "pt")
    st.session_state.lang = stored if stored in SUPPORTED_LANGUAGES else "pt"
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
# COLOR PALETTE & DESIGN SYSTEM (CRISP CONTRAST & HARMONY)
# ══════════════════════════════════════════════════════════════
if theme == "dark":
    # Dark Palette: High Contrast Slate/Zinc + Electric Indigo
    P = {
        "bg_main": "#0b0c10",
        "bg_sidebar": "#10121a",
        "bg_card": "#161822",
        "bg_card_hover": "#1d202e",
        "bg_user_bubble": "#1e2130",
        "border": "#282c3f",
        "border_subtle": "#1f2233",
        "text_primary": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted": "#94a3b8",
        "accent": "#6366f1",
        "accent_hover": "#4f46e5",
        "accent_gradient": "linear-gradient(135deg, #6366f1 0%, #4338ca 100%)",
        "accent_bg": "rgba(99, 102, 241, 0.15)",
        "accent_border": "#6366f1",
        "btn_secondary_bg": "#1c1f2d",
        "btn_secondary_border": "#31364d",
        "btn_secondary_text": "#e2e8f0",
        "success": "#22c55e",
        "success_bg": "rgba(34, 197, 94, 0.12)",
        "shadow_card": "0 2px 8px rgba(0, 0, 0, 0.35)",
        "input_bg": "#13151f",
        "shimmer_bg": "linear-gradient(90deg, #161822 0%, rgba(99, 102, 241, 0.2) 50%, #161822 100%)",
    }
else:
    # Light Palette: Pure White + Crisp Slate + Deep Indigo Accent
    P = {
        "bg_main": "#ffffff",
        "bg_sidebar": "#f8fafc",
        "bg_card": "#ffffff",
        "bg_card_hover": "#f1f5f9",
        "bg_user_bubble": "#f1f5f9",
        "border": "#e2e8f0",
        "border_subtle": "#edf2f7",
        "text_primary": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "accent": "#4f46e5",
        "accent_hover": "#4338ca",
        "accent_gradient": "linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)",
        "accent_bg": "rgba(79, 70, 229, 0.08)",
        "accent_border": "#4f46e5",
        "btn_secondary_bg": "#f8fafc",
        "btn_secondary_border": "#cbd5e1",
        "btn_secondary_text": "#1e293b",
        "success": "#16a34a",
        "success_bg": "rgba(22, 163, 74, 0.08)",
        "shadow_card": "0 1px 4px rgba(0, 0, 0, 0.05), 0 2px 10px rgba(0, 0, 0, 0.02)",
        "input_bg": "#ffffff",
        "shimmer_bg": "linear-gradient(90deg, #f8fafc 0%, rgba(79, 70, 229, 0.1) 50%, #f8fafc 100%)",
    }

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {{
        --bg-main: {P['bg_main']};
        --bg-sidebar: {P['bg_sidebar']};
        --bg-card: {P['bg_card']};
        --bg-card-hover: {P['bg_card_hover']};
        --bg-user: {P['bg_user_bubble']};
        --border: {P['border']};
        --border-subtle: {P['border_subtle']};
        --text-primary: {P['text_primary']};
        --text-secondary: {P['text_secondary']};
        --text-muted: {P['text_muted']};
        --accent: {P['accent']};
        --accent-hover: {P['accent_hover']};
        --accent-gradient: {P['accent_gradient']};
        --accent-bg: {P['accent_bg']};
        --accent-border: {P['accent_border']};
        --btn-sec-bg: {P['btn_secondary_bg']};
        --btn-sec-border: {P['btn_secondary_border']};
        --btn-sec-text: {P['btn_secondary_text']};
        --success: {P['success']};
        --success-bg: {P['success_bg']};
        --shadow-card: {P['shadow_card']};
        --input-bg: {P['input_bg']};
        --shimmer-bg: {P['shimmer_bg']};
    }}

    /* ─ GLOBAL CONTAINER RESET ────────────────────────── */
    html, body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section[data-testid="stMain"],
    .main {{
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    .block-container {{
        padding: 2rem 2.5rem 5rem !important;
        max-width: 960px !important;
    }}

    /* ─ SIDEBAR STRUCTURE ─────────────────────────────── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border) !important;
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {{
        color: var(--text-secondary) !important;
        font-family: 'DM Sans', sans-serif !important;
    }}

    /* ─ GENERAL BUTTON ENGINE & PERFECT CENTERING ─────── */
    .stButton {{
        width: 100% !important;
    }}
    .stButton > button {{
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        transition: all 0.15s ease !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}

    /* Nav Buttons (Left-Aligned in Sidebar) */
    .sidebar-nav-btn .stButton > button,
    .chat-history-btn .stButton > button {{
        justify-content: flex-start !important;
        text-align: left !important;
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: 1px solid transparent !important;
    }}
    .sidebar-nav-btn .stButton > button:hover,
    .chat-history-btn .stButton > button:hover {{
        background: var(--bg-card-hover) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }}

    /* Active Nav State */
    .nav-btn-active .stButton > button {{
        background: var(--accent-bg) !important;
        border-color: var(--accent-border) !important;
        color: var(--accent) !important;
        font-weight: 600 !important;
    }}

    /* Primary Buttons (CTA / Active Pills / Submit) */
    .stButton > button[kind="primary"] {{
        background: var(--accent-gradient) !important;
        color: #ffffff !important;
        border: 1px solid var(--accent) !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(79, 70, 229, 0.25) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        filter: brightness(1.1) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35) !important;
    }}

    /* Secondary Buttons (Inactive Pills / Options) */
    .stButton > button[kind="secondary"] {{
        background: var(--btn-sec-bg) !important;
        color: var(--btn-sec-text) !important;
        border: 1px solid var(--btn-sec-border) !important;
        font-weight: 500 !important;
    }}
    .stButton > button[kind="secondary"]:hover {{
        border-color: var(--accent) !important;
        color: var(--text-primary) !important;
        background: var(--bg-card-hover) !important;
    }}

    /* ─ TOP BAR ───────────────────────────────────────── */
    .ancora-topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 16px;
        margin-bottom: 20px;
        border-bottom: 1px solid var(--border);
    }}
    .topbar-title {{
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }}
    .topbar-sub {{
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 2px;
    }}
    .topbar-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        padding: 4px 12px;
        background: var(--accent-bg);
        color: var(--accent);
        border: 1px solid var(--border);
        border-radius: 20px;
        font-weight: 600;
    }}

    /* ─ CHAT BUBBLES ──────────────────────────────────── */
    .user-bubble {{
        background: var(--bg-user);
        border: 1px solid var(--border);
        border-radius: 14px 14px 4px 14px;
        padding: 13px 18px;
        color: var(--text-primary);
        font-size: 0.93rem;
        line-height: 1.55;
        margin: 0 0 16px auto;
        max-width: 86%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}
    .assistant-wrap {{
        margin-bottom: 22px;
    }}
    .assistant-body {{
        color: var(--text-primary);
        font-size: 0.93rem;
        line-height: 1.7;
    }}
    .assistant-body strong {{
        color: var(--text-primary);
        font-weight: 600;
    }}
    .assistant-body code {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.83rem;
        background: var(--bg-card-hover);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 1px 5px;
        color: var(--accent);
    }}

    /* ─ THOUGHT CONTAINER ─────────────────────────────── */
    .thought-body {{
        background: var(--bg-sidebar);
        border-left: 3px solid var(--accent);
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.6;
    }}

    /* ─ LIVE THINKING SHIMMER ─────────────────────────── */
    .live-thinking-box {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 11px 16px;
        margin: 14px 0;
        border-left: 3px solid var(--accent);
        border-radius: 0 8px 8px 0;
        background: var(--shimmer-bg);
        background-size: 200% 100%;
        animation: shimmerWave 2s infinite linear;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: var(--accent);
    }}
    @keyframes shimmerWave {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    .thinking-spinner {{
        width: 13px;
        height: 13px;
        border: 2px solid var(--accent-bg);
        border-top-color: var(--accent);
        border-radius: 50%;
        animation: spin 0.75s linear infinite;
    }}
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}

    /* ─ CARDS ─────────────────────────────────────────── */
    .app-card {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 14px;
        color: var(--text-primary);
        box-shadow: var(--shadow-card);
        transition: border-color 0.15s, transform 0.15s;
    }}
    .app-card:hover {{
        border-color: var(--accent);
        transform: translateY(-1px);
    }}
    .app-card-accent {{
        border-left: 3px solid var(--accent) !important;
    }}
    .app-card h4 {{
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 6px;
        color: var(--text-primary);
    }}
    .app-card p, .app-card small {{
        color: var(--text-muted);
        font-size: 0.85rem;
    }}

    /* ─ STATUS INDICATOR ──────────────────────────────── */
    .status-dot {{
        display: inline-block;
        width: 7px;
        height: 7px;
        background-color: var(--success);
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 8px var(--success);
        animation: pulseDot 2.5s infinite;
    }}
    @keyframes pulseDot {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.4; transform: scale(0.8); }}
    }}

    /* ─ CHAT INPUT ────────────────────────────────────── */
    [data-testid="stChatInput"] {{
        border-radius: 14px !important;
        border-color: var(--border) !important;
        background-color: var(--input-bg) !important;
    }}
    [data-testid="stChatInput"]:focus-within {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-bg) !important;
    }}
    [data-testid="stChatInput"] textarea {{
        color: var(--text-primary) !important;
    }}

    /* ─ EXPANDER ──────────────────────────────────────── */
    [data-testid="stExpander"] {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }}

    /* ─ HIDE UNNECESSARY CHROME ───────────────────────── */
    header[data-testid="stHeader"], footer,
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], .stDeployButton {{
        display: none !important;
    }}

    /* ─ COLUMN GAP CLEANUP ────────────────────────────── */
    [data-testid="stHorizontalBlock"] {{
        gap: 0.75rem !important;
        align-items: center !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Chat History Init ────────────────────────────────────────
if "conversations" not in st.session_state:
    loaded = get_all_chat_sessions()
    if not loaded:
        init_id = f"conv_{uuid.uuid4().hex[:8]}"
        welcome = get_text("default_welcome", lang)
        loaded = {
            init_id: {
                "title": "Clareza & Alinhamento TCC" if lang == "pt" else "Clarity & CBT",
                "messages": [{"role": "assistant", "thought": "Sistema inicializado.", "content": welcome}]
            }
        }
        save_chat_session(init_id, loaded[init_id]["title"])
        save_chat_message(init_id, "assistant", welcome, "Sistema inicializado.")
    st.session_state.conversations = loaded
    st.session_state.current_conv_id = list(loaded.keys())[-1]

if "agent" not in st.session_state:
    st.session_state.agent = AncoraAgent(model_id=st.session_state.selected_model, lang=lang)
if "active_mode" not in st.session_state:
    st.session_state.active_mode = get_text("mode_chat", lang)

current_conv = st.session_state.conversations[st.session_state.current_conv_id]

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand Header
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; padding:4px 0 12px;">
      <div style="display:flex; align-items:center; gap:8px;">
        <span style="font-size:1.3rem;">⚓</span>
        <span style="font-size:1.05rem; font-weight:700; color:var(--text-primary); letter-spacing:-0.02em;">Ancora AI</span>
        <span style="font-size:0.68rem; color:var(--text-muted); border:1px solid var(--border); padding:1px 6px; border-radius:4px; font-family:'JetBrains Mono',monospace;">v2.0</span>
      </div>
    </div>
    <div style="margin-bottom:14px;">
      <span class="status-dot"></span>
      <small style="color:var(--text-muted); font-size:0.78rem;">{get_text('sidebar_status', lang)}</small>
    </div>
    """, unsafe_allow_html=True)

    # New Chat Primary CTA
    if st.button(f"＋  {get_text('new_chat_btn', lang)}", use_container_width=True, type="primary"):
        nid = f"conv_{uuid.uuid4().hex[:8]}"
        welcome = get_text("default_welcome", lang)
        st.session_state.conversations[nid] = {
            "title": "Nova Conversa" if lang == "pt" else "New Chat",
            "messages": [{"role": "assistant", "thought": "", "content": welcome}]
        }
        st.session_state.current_conv_id = nid
        st.session_state.active_mode = get_text("mode_chat", lang)
        save_chat_session(nid, st.session_state.conversations[nid]["title"])
        save_chat_message(nid, "assistant", welcome, "")
        st.rerun()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # Navigation Modes (Clean Left-Aligned with Active Highlight)
    st.markdown(f"<div style='font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); padding:6px 2px;'>{get_text('tools_heading', lang)}</div>", unsafe_allow_html=True)
    
    modes = [
        ("mode_chat",       "💬", get_text("mode_chat", lang)),
        ("mode_msg_lab",    "📱", get_text("mode_msg_lab", lang)),
        ("mode_roleplay",   "🎭", get_text("mode_roleplay", lang)),
        ("mode_decompress", "🫁", get_text("mode_decompress", lang)),
        ("mode_dashboard",  "📈", get_text("mode_dashboard", lang)),
    ]
    for m_key, m_icon, m_label in modes:
        is_act = (st.session_state.active_mode == m_label)
        prefix = "▸  " if is_act else "    "
        wrapper_class = "sidebar-nav-btn nav-btn-active" if is_act else "sidebar-nav-btn"
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.button(f"{prefix}{m_icon}  {m_label}", key=f"nav_{m_key}", use_container_width=True):
            st.session_state.active_mode = m_label
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Recent Conversations (Clean list with active mark)
    st.markdown(f"<div style='font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); padding:4px 2px;'>{get_text('recent_convs', lang)}</div>", unsafe_allow_html=True)
    for cid, cdata in reversed(list(st.session_state.conversations.items())):
        act = (cid == st.session_state.current_conv_id)
        prefix = "▸  " if act else "    "
        title_short = cdata["title"][:22]
        wrapper_class = "chat-history-btn nav-btn-active" if act else "chat-history-btn"
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.button(f"{prefix}{title_short}", key=f"chat_{cid}", use_container_width=True):
            st.session_state.current_conv_id = cid
            st.session_state.active_mode = get_text("mode_chat", lang)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Settings Drawer (Centered 2-Column Balanced Grids)
    with st.expander(f"⚙️  {get_text('settings_heading', lang)}"):
        # 1. Theme (2 Balanced Columns)
        st.markdown("<div style='font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); margin:4px 0 6px;'>Tema / Theme</div>", unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        with tc1:
            if st.button("🌙  Escuro", use_container_width=True, type="primary" if theme == "dark" else "secondary"):
                if theme != "dark":
                    st.session_state.theme = "dark"
                    save_preference("theme", "dark")
                    st.rerun()
        with tc2:
            if st.button("☀️  Claro", use_container_width=True, type="primary" if theme == "light" else "secondary"):
                if theme != "light":
                    st.session_state.theme = "light"
                    save_preference("theme", "light")
                    st.rerun()

        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        # 2. Language (2 Balanced Columns × 4 Rows for Perfect Fit)
        st.markdown(f"<div style='font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); margin:8px 0 6px;'>{get_text('lang_label', lang)}</div>", unsafe_allow_html=True)
        lang_list = [
            ("pt", "🇧🇷 Português"), ("en", "🇺🇸 English"),
            ("es", "🇪🇸 Español"),   ("fr", "🇫🇷 Français"),
            ("zh", "🇨🇳 中文"),       ("hi", "🇮🇳 हिन्दी"),
            ("ar", "🇸🇦 العربية"),   ("bn", "🇧🇩 বাংলা")
        ]
        l_c1, l_c2 = st.columns(2)
        for i, (code, lbl) in enumerate(lang_list):
            target_col = l_c1 if i % 2 == 0 else l_c2
            with target_col:
                is_sel = (lang == code)
                if st.button(lbl, key=f"l_{code}", use_container_width=True, type="primary" if is_sel else "secondary"):
                    if lang != code:
                        st.session_state.lang = code
                        save_preference("language", code)
                        st.session_state.agent = AncoraAgent(model_id=st.session_state.selected_model, lang=code)
                        st.rerun()

        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        # 3. Model Grid (2 Balanced Columns)
        st.markdown(f"<div style='font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); margin:8px 0 6px;'>{get_text('model_label', lang)}</div>", unsafe_allow_html=True)
        models = [
            ("gemini-3.7-flash", "⚡ Gemini Flash"),
            ("gemini-3.1-pro",   "🧠 Gemini Pro"),
            ("claude-3-5-sonnet","🏛️ Claude Sonnet"),
            ("offline",          "🛡️ Offline TCC")
        ]
        sm = st.session_state.selected_model
        mc1, mc2 = st.columns(2)
        for i, (mid, mlbl) in enumerate(models):
            target_col = mc1 if i % 2 == 0 else mc2
            with target_col:
                is_sel = (sm == mid)
                if st.button(mlbl, key=f"m_{mid}", use_container_width=True, type="primary" if is_sel else "secondary"):
                    if sm != mid:
                        st.session_state.selected_model = mid
                        save_preference("selected_model", mid)
                        st.session_state.agent = AncoraAgent(model_id=mid, lang=lang)
                        st.rerun()

        # 4. LGPD Section
        st.markdown("---")
        st.markdown(f"<div style='font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); margin-bottom:4px;'>{get_text('lgpd_heading', lang)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.75rem; color:var(--success); font-weight:600; margin-bottom:8px;'>{get_text('lgpd_badge', lang)}</div>", unsafe_allow_html=True)
        
        exp_d = export_user_data_lgpd()
        st.download_button(
            label=get_text("lgpd_export_btn", lang),
            data=json.dumps(exp_d, indent=2, ensure_ascii=False),
            file_name=f"ancora_lgpd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        if st.button(get_text("lgpd_delete_btn", lang), use_container_width=True):
            delete_all_user_data_lgpd()
            iid = "conv_1"
            wc = get_text("default_welcome", lang)
            st.session_state.conversations = {iid: {"title": "Clareza & Alinhamento TCC", "messages": [{"role": "assistant", "thought": "", "content": wc}]}}
            st.session_state.current_conv_id = iid
            save_chat_session(iid, "Clareza & Alinhamento TCC")
            st.success(get_text("lgpd_deleted_success", lang))
            st.rerun()

# ══════════════════════════════════════════════════════════════
# MAIN CANVAS
# ══════════════════════════════════════════════════════════════
model_labels = {
    "gemini-3.7-flash": "Gemini 3.7 Flash",
    "gemini-3.1-pro": "Gemini 3.1 Pro",
    "claude-3-5-sonnet": "Claude 3.5 Sonnet",
    "offline": "Offline · TCC/ACT"
}
badge_label = model_labels.get(st.session_state.selected_model, "Gemini")
lang_flag = SUPPORTED_LANGUAGES.get(lang, {}).get("flag", "🌐")

st.markdown(f"""
<div class="ancora-topbar">
  <div>
    <div class="topbar-title">⚓ {current_conv['title']}</div>
    <div class="topbar-sub">Modo: {st.session_state.active_mode}</div>
  </div>
  <div class="topbar-badge">{lang_flag}  {badge_label}</div>
</div>
""", unsafe_allow_html=True)

# ─── 1. CHAT LIVRE ───────────────────────────────────────────
if st.session_state.active_mode == get_text("mode_chat", lang):
    for msg in current_conv["messages"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="assistant-wrap">', unsafe_allow_html=True)
            if msg.get("thought"):
                with st.expander(get_text("thought_title", lang), expanded=False):
                    st.markdown(f'<div class="thought-body">{msg["thought"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="assistant-body">{msg["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if user_prompt := st.chat_input(get_text("input_placeholder", lang)):
        current_conv["messages"].append({"role": "user", "content": user_prompt})
        save_chat_message(st.session_state.current_conv_id, "user", user_prompt)
        st.markdown(f'<div class="user-bubble">{user_prompt}</div>', unsafe_allow_html=True)

        if len(current_conv["messages"]) == 2:
            t = st.session_state.agent.generate_chat_title(user_prompt)
            current_conv["title"] = t
            save_chat_session(st.session_state.current_conv_id, t)

        ph = st.empty()
        for step in get_dynamic_thinking_steps(user_prompt, lang=lang):
            ph.markdown(f'<div class="live-thinking-box"><div class="thinking-spinner"></div><span>{step}</span></div>', unsafe_allow_html=True)
            time.sleep(0.32)

        resp = st.session_state.agent.respond(user_prompt, model_override=st.session_state.selected_model, lang_override=lang)
        ph.empty()
        thought_s = resp.get("thought", "")
        content_s = resp.get("content", "")
        current_conv["messages"].append({"role": "assistant", "thought": thought_s, "content": content_s})
        save_chat_message(st.session_state.current_conv_id, "assistant", content_s, thought_s)
        st.rerun()

# ─── 2. MESSAGE LAB ──────────────────────────────────────────
elif st.session_state.active_mode == get_text("mode_msg_lab", lang):
    st.markdown("### 📱 Message Lab & Flirt Rater")
    st.caption("Diagnóstico comportamental de mensagens antes do envio — nível de segurança, carência e engajamento.")
    c1, c2 = st.columns(2)
    with c1:
        msg_in = st.text_area("Mensagem para análise:", height=140, placeholder="Ex: Oi linda, você sumiu...")
        aud = st.radio("Contexto:", ["Romântico / Flerte", "Profissional / Limites"], horizontal=True)
        if st.button(get_text("diagnose_btn", lang), type="primary", use_container_width=True):
            if msg_in:
                st.session_state["lab_res"] = analyze_message_and_rewrite(msg_in, "romantic" if "Romântico" in aud else "professional")
    with c2:
        if "lab_res" in st.session_state:
            r = st.session_state["lab_res"]
            st.markdown(f"""
            <div class="app-card">
                <h4>Diagnóstico Geral</h4>
                <p>Confiança: <code>{r['confidence_score']}/100</code> &nbsp;·&nbsp; Carência: <strong>{r['neediness_level']}</strong> &nbsp;·&nbsp; Banter: <strong>{r['banter_level']}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            for rw in r["rewrites"]:
                st.markdown(f"""
                <div class="app-card app-card-accent">
                    <span style="font-size:0.75rem; color:var(--accent); font-weight:700; text-transform:uppercase;">{rw['style']}</span>
                    <p style="margin:6px 0; font-weight:600; color:var(--text-primary);">"{rw['text']}"</p>
                    <small>{rw['rationale']}</small>
                </div>
                """, unsafe_allow_html=True)

# ─── 3. ARENA DE SIMULAÇÃO (ROLEPLAY) ────────────────────────
elif st.session_state.active_mode == get_text("mode_roleplay", lang):
    st.markdown("### 🎭 Arena de Simulação em Tempo Real")
    st.caption("Pratique conversas de alta pressão (negociação com chefe, primeiro encontro, limites) em um ambiente seguro.")
    scens = {k: v["title"] for k, v in ROLEPLAY_SCENARIOS.items()}
    chosen = st.selectbox("Cenário:", list(scens.keys()), format_func=lambda x: scens[x])
    meta = get_scenario_details(chosen)
    if "rp_chat" not in st.session_state or st.session_state.get("rp_sc") != chosen:
        st.session_state.rp_chat = [{"role": "partner", "content": meta["initial_message"]}]
        st.session_state.rp_sc = chosen
    if st.button(get_text("restart_sim_btn", lang), use_container_width=True):
        st.session_state.rp_chat = [{"role": "partner", "content": meta["initial_message"]}]
        st.rerun()
    for m in st.session_state.rp_chat:
        if m["role"] == "partner":
            st.markdown(f'<div class="app-card" style="border-left:3px solid #8b5cf6;"><strong>{meta["partner_name"]}:</strong> {m["content"]}</div>', unsafe_allow_html=True)
        elif m["role"] == "user":
            st.markdown(f'<div class="user-bubble">{m["content"]}</div>', unsafe_allow_html=True)
        elif m["role"] == "coach":
            st.markdown(f'<div class="thought-body" style="margin-bottom:10px;">{m["content"]}</div>', unsafe_allow_html=True)
    if rp_in := st.chat_input("Sua resposta na simulação..."):
        st.session_state.rp_chat.append({"role": "user", "content": rp_in})
        out = generate_roleplay_turn(chosen, st.session_state.rp_chat, rp_in)
        st.session_state.rp_chat.append({"role": "partner", "content": out["reply"]})
        if out.get("coach_tip"):
            st.session_state.rp_chat.append({"role": "coach", "content": out["coach_tip"]})
        if out.get("scorecard"):
            st.balloons()
            st.success(f"🏆 Simulação Concluída! Nota: {out['scorecard']['overall_score']}/100")
        st.rerun()

# ─── 4. DESCOMPRESSÃO SOMÁTICA ──────────────────────────────
elif st.session_state.active_mode == get_text("mode_decompress", lang):
    st.markdown("### 🫁 Descompressão & Regulação Somática")
    st.caption("Protocolos neurocientíficos de alívio rápido para quando o sistema nervoso estiver em sobrecarga.")
    c1, c2 = st.columns(2)
    with c1:
        techs = [
            ("physiological_sigh", "Suspiro Fisiológico (Huberman)"),
            ("box_breathing", "Box Breathing (Navy SEALs)"),
            ("grounding_54321", "Ancoragem Tátil 5-4-3-2-1"),
            ("perspective_reset", "Reset de Perspectiva")
        ]
        tech = st.selectbox("Protocolo:", techs, format_func=lambda x: x[1])
        rd = get_decompression_routine(tech[0])
        steps_html = "".join(f"<li style='margin-bottom:6px;'>{s}</li>" for s in rd["steps"])
        st.markdown(f"""
        <div class="app-card">
            <h4>{rd['name']}</h4>
            <span style="display:inline-block; font-size:0.75rem; color:var(--accent); background:var(--accent-bg); padding:2px 8px; border-radius:4px; font-weight:600; margin-bottom:8px;">{rd['duration']}</span>
            <ol style="margin:8px 0 0 18px; line-height:1.7; color:var(--text-primary);">{steps_html}</ol>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("#### Sons Ambientes")
        s_opt = st.selectbox("Som:", ["Chuva Suave", "Ondas do Oceano", "Lareira"])
        urls = {
            "Chuva Suave": "https://assets.mixkit.co/active_storage/sfx/1253/1253-preview.mp3",
            "Ondas do Oceano": "https://assets.mixkit.co/active_storage/sfx/1189/1189-preview.mp3",
            "Lareira": "https://assets.mixkit.co/active_storage/sfx/1243/1243-preview.mp3"
        }
        st.audio(urls[s_opt], format="audio/mp3")

# ─── 5. DASHBOARD & MÉTRICAS ────────────────────────────────
elif st.session_state.active_mode == get_text("mode_dashboard", lang):
    st.markdown("### 📈 Dashboard & Métricas")
    stats = get_mood_stats()
    tok = st.session_state.agent.get_token_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Média de Humor", f"{stats['avg_score']}/10")
    c2.metric("Sessões", f"{stats['total_logs']}")
    c3.metric("Tokens Poupados", f"{tok['tokens_saved']:,}")
    c4.metric("Economia Est.", f"${tok['estimated_cost_saved_usd']:.4f}")
    st.markdown("---")
    st.markdown("#### Registrar Humor")
    sc = st.slider("Nota (1-10):", 1, 10, 7)
    tg = st.multiselect("Emoções:", ["Focado", "Confiante", "Tranquilo", "Ansioso", "Sobrecarregado", "Cansado"])
    tr = st.text_input("Contexto:")
    if st.button(get_text("save_journal_btn", lang), use_container_width=True, type="primary"):
        record_mood_entry(sc, tg, tr, "")
        st.success("Salvo com sucesso!")
