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

lang  = st.session_state.lang
theme = st.session_state.theme

st.set_page_config(
    page_title=get_text("app_title", lang),
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Zinc + Indigo Palette (Ancora AI)
# Reference: building_data_apps/references/shared_design_system.md
# ══════════════════════════════════════════════════════════════
if theme == "dark":
    T = {
        "bg": "#09090b", "bg_s": "#0c0c0f", "card": "#111114",
        "card_h": "#18181b", "border": "#27272a", "border_s": "#1e1e24",
        "text": "#fafafa", "text_m": "#a1a1aa", "text_d": "#52525b",
        "acc_a": "#6366f1", "acc_b": "#818cf8",
        "acc_muted": "rgba(99,102,241,0.13)",
        "acc_shadow": "rgba(99,102,241,0.35)",
        "cyan": "#22d3ee", "cyan_m": "rgba(34,211,238,0.1)",
        "green": "#22c55e", "green_m": "rgba(34,197,94,0.12)",
        "user_bub": "#18181b",
        "shadow": "none", "shadow_c": "0 1px 6px rgba(0,0,0,0.4)",
        "input_bg": "#111114",
        "nav_act_bg": "rgba(99,102,241,0.15)",
        "nav_act_b": "#6366f1",
        "sh_a": "#1e1e2e", "sh_b": "rgba(99,102,241,0.15)",
    }
else:
    T = {
        "bg": "#ffffff", "bg_s": "#fafafa", "card": "#ffffff",
        "card_h": "#f4f4f5", "border": "#e4e4e7", "border_s": "#f0f0f2",
        "text": "#09090b", "text_m": "#71717a", "text_d": "#a1a1aa",
        "acc_a": "#4f46e5", "acc_b": "#6366f1",
        "acc_muted": "rgba(79,70,229,0.08)",
        "acc_shadow": "rgba(79,70,229,0.28)",
        "cyan": "#0284c7", "cyan_m": "rgba(2,132,199,0.08)",
        "green": "#16a34a", "green_m": "rgba(22,163,74,0.08)",
        "user_bub": "#f4f4f5",
        "shadow": "0 1px 3px rgba(0,0,0,0.05)", "shadow_c": "0 1px 4px rgba(0,0,0,0.06)",
        "input_bg": "#ffffff",
        "nav_act_bg": "rgba(79,70,229,0.08)",
        "nav_act_b": "#4f46e5",
        "sh_a": "#f1f5f9", "sh_b": "rgba(79,70,229,0.1)",
    }

CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ─ TOKENS ─────────────────────────────────────────── */
  :root {{
    --bg:         {T['bg']};
    --bg-s:       {T['bg_s']};
    --card:       {T['card']};
    --card-h:     {T['card_h']};
    --bd:         {T['border']};
    --bd-s:       {T['border_s']};
    --tx:         {T['text']};
    --tx-m:       {T['text_m']};
    --tx-d:       {T['text_d']};
    --acc-a:      {T['acc_a']};
    --acc-b:      {T['acc_b']};
    --acc-m:      {T['acc_muted']};
    --acc-sh:     {T['acc_shadow']};
    --cyan:       {T['cyan']};
    --cyan-m:     {T['cyan_m']};
    --green:      {T['green']};
    --green-m:    {T['green_m']};
    --ub:         {T['user_bub']};
    --shw:        {T['shadow']};
    --shw-c:      {T['shadow_c']};
    --inp:        {T['input_bg']};
    --nav-a-bg:   {T['nav_act_bg']};
    --nav-a-bd:   {T['nav_act_b']};
    --sh-a:       {T['sh_a']};
    --sh-b:       {T['sh_b']};
    --r:          10px;
    --r-sm:       7px;
  }}

  /* ─ GLOBAL ──────────────────────────────────────────── */
  html, body,
  [data-testid="stApp"],
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"],
  section[data-testid="stMain"],
  .main {{
    background: var(--bg) !important;
    color: var(--tx) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
  }}
  .block-container {{
    padding: 2rem 2.5rem 5rem !important;
    max-width: 960px !important;
  }}

  /* ─ SIDEBAR ─────────────────────────────────────────── */
  [data-testid="stSidebar"],
  [data-testid="stSidebar"] > div:first-child,
  [data-testid="stSidebarContent"],
  [data-testid="stSidebarUserContent"] {{
    background: var(--bg-s) !important;
    border-right: 1px solid var(--bd) !important;
  }}
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] small,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label {{
    color: var(--tx-m) !important;
    font-family: 'DM Sans', sans-serif !important;
  }}

  /* ─ ANIMATIONS ──────────────────────────────────────── */
  @keyframes fadeUp {{
    from {{ opacity:0; transform:translateY(7px); }}
    to   {{ opacity:1; transform:translateY(0); }}
  }}
  @keyframes shimmer {{
    0%   {{ background-position: 200% 0; }}
    100% {{ background-position: -200% 0; }}
  }}
  @keyframes pulse-dot {{
    0%,100% {{ opacity:1; transform:scale(1); }}
    50%     {{ opacity:0.4; transform:scale(0.8); }}
  }}
  @keyframes spin {{ to {{ transform:rotate(360deg); }} }}

  /* ─ BRAND ───────────────────────────────────────────── */
  .brand-wrap {{
    display: flex; align-items: center; gap: 10px;
    padding: 4px 0 14px;
  }}
  .brand-icon {{
    font-size: 1.35rem;
    background: linear-gradient(135deg, var(--acc-a), var(--acc-b));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .brand-name {{
    font-size: 1.05rem; font-weight: 700; color: var(--tx);
    letter-spacing: -0.02em;
  }}
  .brand-ver {{
    font-size: 0.7rem; color: var(--tx-d);
    background: var(--card); border: 1px solid var(--bd);
    padding: 1px 7px; border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
  }}

  /* ─ STATUS ───────────────────────────────────────────── */
  .status-row {{ margin-bottom: 14px; }}
  .status-dot {{
    display: inline-block; width:7px; height:7px;
    background: var(--green); border-radius: 50%;
    margin-right: 6px; box-shadow: 0 0 8px var(--green);
    animation: pulse-dot 2.5s infinite;
  }}
  .status-text {{ font-size: 0.78rem; color: var(--tx-m); }}

  /* ─ NAV LABEL ────────────────────────────────────────── */
  .nav-label {{
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--tx-d); padding: 14px 2px 6px;
  }}

  /* ─ ALL STREAMLIT BUTTONS (default = ghost nav) ──────── */
  .stButton > button {{
    width: 100%;
    text-align: left !important;
    background: transparent !important;
    color: var(--tx-m) !important;
    border: 1px solid transparent !important;
    border-radius: var(--r-sm) !important;
    padding: 9px 13px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: background 0.13s, color 0.13s, border-color 0.13s !important;
    box-shadow: none !important;
  }}
  .stButton > button:hover {{
    background: var(--card-h) !important;
    color: var(--tx) !important;
    border-color: var(--bd) !important;
  }}

  /* Primary CTA (New Chat + Save) */
  .stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, var(--acc-a) 0%, var(--acc-b) 100%) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: var(--r) !important;
    box-shadow: 0 2px 10px var(--acc-sh) !important;
    justify-content: center !important;
    text-align: center !important;
  }}
  .stButton > button[kind="primary"]:hover {{
    filter: brightness(1.08) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px var(--acc-sh) !important;
  }}

  /* Secondary (selected state for theme/lang/model pills) */
  .stButton > button[kind="secondary"] {{
    background: var(--card) !important;
    color: var(--tx-m) !important;
    border: 1px solid var(--bd) !important;
    border-radius: var(--r-sm) !important;
    justify-content: center !important;
    text-align: center !important;
    font-size: 0.82rem !important;
  }}
  .stButton > button[kind="secondary"]:hover {{
    border-color: var(--acc-a) !important;
    color: var(--tx) !important;
  }}

  /* ─ TOP BAR ──────────────────────────────────────────── */
  .topbar {{
    display: flex; align-items: flex-start;
    justify-content: space-between;
    padding: 0 0 18px; margin-bottom: 22px;
    border-bottom: 1px solid var(--bd);
    animation: fadeUp 0.2s ease;
  }}
  .topbar-title {{
    font-size: 1rem; font-weight: 600; color: var(--tx);
    letter-spacing: -0.015em;
  }}
  .topbar-sub {{
    font-size: 0.78rem; color: var(--tx-m); margin-top: 2px;
  }}
  .topbar-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.76rem; padding: 5px 13px;
    background: var(--acc-m); color: var(--acc-a);
    border: 1px solid var(--bd); border-radius: 20px;
    font-weight: 500; white-space: nowrap;
  }}

  /* ─ MESSAGES ─────────────────────────────────────────── */
  .user-bubble {{
    background: var(--ub);
    border: 1px solid var(--bd);
    border-radius: 12px 12px 4px 12px;
    padding: 13px 18px;
    color: var(--tx); font-size: 0.93rem; line-height: 1.55;
    margin: 0 0 16px auto;
    max-width: 86%;
    box-shadow: var(--shw);
    animation: fadeUp 0.2s ease;
  }}
  .ai-wrap {{
    animation: fadeUp 0.25s ease;
    margin-bottom: 22px;
  }}
  .assistant-body {{
    color: var(--tx); font-size: 0.93rem; line-height: 1.72;
  }}
  .assistant-body p   {{ margin-bottom: 0.55rem; }}
  .assistant-body strong {{ color: var(--tx); font-weight: 600; }}
  .assistant-body code {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
    background: var(--card-h); border: 1px solid var(--bd);
    border-radius: 4px; padding: 1px 5px; color: var(--cyan);
  }}

  /* ─ THOUGHT ──────────────────────────────────────────── */
  .thought-body {{
    background: var(--bg-s); border-left: 3px solid var(--cyan);
    border-radius: 0 var(--r-sm) var(--r-sm) 0;
    padding: 10px 14px; font-size: 0.82rem;
    color: var(--tx-m); font-family: 'JetBrains Mono', monospace;
    line-height: 1.6;
  }}

  /* ─ THINKING SHIMMER ─────────────────────────────────── */
  .thinking-box {{
    display: flex; align-items: center; gap: 12px;
    padding: 11px 16px; margin: 12px 0;
    border-left: 3px solid var(--acc-a);
    border-radius: 0 var(--r-sm) var(--r-sm) 0;
    background: linear-gradient(90deg, var(--sh-a) 0%, var(--sh-b) 50%, var(--sh-a) 100%);
    background-size: 200% 100%;
    animation: shimmer 2.2s infinite linear;
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
    color: var(--acc-a);
  }}
  .thinking-spinner {{
    flex-shrink: 0; width: 12px; height: 12px;
    border: 2px solid var(--acc-m); border-top-color: var(--acc-a);
    border-radius: 50%; animation: spin 0.75s linear infinite;
  }}

  /* ─ CARDS ────────────────────────────────────────────── */
  .card {{
    background: var(--card); border: 1px solid var(--bd);
    border-radius: var(--r); padding: 16px 18px; margin-bottom: 14px;
    color: var(--tx); box-shadow: var(--shw-c);
    transition: border-color 0.15s, transform 0.15s;
  }}
  .card:hover {{ border-color: var(--acc-a); transform: translateY(-1px); }}
  .card-accent {{ border-left: 3px solid var(--acc-a) !important; }}
  .card h4 {{ font-size: 0.88rem; font-weight: 600; margin-bottom: 8px; color: var(--tx); }}
  .card code {{ font-family: 'JetBrains Mono', monospace; color: var(--cyan); font-size: 0.83rem; }}
  .card p, .card small {{ color: var(--tx-m); font-size: 0.84rem; }}

  /* ─ BADGES ───────────────────────────────────────────── */
  .badge {{
    display: inline-flex; align-items: center;
    padding: 2px 10px; border-radius: 6px;
    font-size: 0.72rem; font-weight: 500;
  }}
  .b-indigo {{ color: var(--acc-a); background: var(--acc-m); }}
  .b-green  {{ color: var(--green); background: var(--green-m); }}
  .b-cyan   {{ color: var(--cyan);  background: var(--cyan-m);  }}

  /* ─ SETTINGS BLOCK LABEL ────────────────────────────── */
  .set-label {{
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
    color: var(--tx-d); margin: 12px 0 6px;
  }}

  /* ─ CHAT INPUT ───────────────────────────────────────── */
  [data-testid="stChatInput"] {{
    border-radius: 14px !important;
    border-color: var(--bd) !important;
    background: var(--inp) !important;
  }}
  [data-testid="stChatInput"]:focus-within {{
    border-color: var(--acc-a) !important;
    box-shadow: 0 0 0 3px var(--acc-m) !important;
  }}
  [data-testid="stChatInput"] textarea {{ color: var(--tx) !important; }}

  /* ─ EXPANDER ─────────────────────────────────────────── */
  [data-testid="stExpander"] {{
    background: var(--card) !important;
    border: 1px solid var(--bd) !important;
    border-radius: var(--r) !important;
  }}

  /* ─ HIDE CHROME ──────────────────────────────────────── */
  header[data-testid="stHeader"], footer,
  [data-testid="stToolbar"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"], .stDeployButton {{
    display: none !important;
  }}

  /* ─ GAP FIX ──────────────────────────────────────────── */
  [data-testid="stHorizontalBlock"] {{ gap: 1.1rem !important; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Chat History Init ────────────────────────────────────────
if "conversations" not in st.session_state:
    loaded = get_all_chat_sessions()
    if not loaded:
        init_id = f"conv_{uuid.uuid4().hex[:8]}"
        welcome = get_text("default_welcome", lang)
        loaded = {init_id: {"title": "Clareza & Alinhamento TCC" if lang == "pt" else "Clarity & CBT", "messages": [{"role":"assistant","thought":"Sistema inicializado.","content":welcome}]}}
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
    # Brand
    st.markdown(f"""
    <div class="brand-wrap">
      <span class="brand-icon">⚓</span>
      <span class="brand-name">Ancora AI</span>
      <span class="brand-ver">v2.0</span>
    </div>
    <div class="status-row">
      <span class="status-dot"></span>
      <span class="status-text">{get_text('sidebar_status', lang)}</span>
    </div>
    """, unsafe_allow_html=True)

    # New Chat CTA
    if st.button(f"＋  {get_text('new_chat_btn', lang)}", use_container_width=True, type="primary"):
        nid = f"conv_{uuid.uuid4().hex[:8]}"
        welcome = get_text("default_welcome", lang)
        st.session_state.conversations[nid] = {"title":"Nova Conversa" if lang=="pt" else "New Chat","messages":[{"role":"assistant","thought":"","content":welcome}]}
        st.session_state.current_conv_id = nid
        st.session_state.active_mode = get_text("mode_chat", lang)
        save_chat_session(nid, st.session_state.conversations[nid]["title"])
        save_chat_message(nid, "assistant", welcome, "")
        st.rerun()

    # Navigation
    st.markdown(f'<div class="nav-label">{get_text("tools_heading", lang)}</div>', unsafe_allow_html=True)
    modes = [
        ("mode_chat",       "💬", get_text("mode_chat", lang)),
        ("mode_msg_lab",    "📱", get_text("mode_msg_lab", lang)),
        ("mode_roleplay",   "🎭", get_text("mode_roleplay", lang)),
        ("mode_decompress", "🫁", get_text("mode_decompress", lang)),
        ("mode_dashboard",  "📈", get_text("mode_dashboard", lang)),
    ]
    for m_key, m_icon, m_label in modes:
        is_act = st.session_state.active_mode == m_label
        prefix = "▸  " if is_act else "    "
        if st.button(f"{prefix}{m_icon}  {m_label}", key=f"nav_{m_key}", use_container_width=True):
            st.session_state.active_mode = m_label
            st.rerun()

    st.divider()

    # Recent Conversations
    st.markdown(f'<div class="nav-label">{get_text("recent_convs", lang)}</div>', unsafe_allow_html=True)
    for cid, cdata in reversed(list(st.session_state.conversations.items())):
        act = cid == st.session_state.current_conv_id
        prefix = "▸  " if act else "    "
        title_short = cdata["title"][:22]
        if st.button(f"{prefix}{title_short}", key=f"chat_{cid}", use_container_width=True):
            st.session_state.current_conv_id = cid
            st.session_state.active_mode = get_text("mode_chat", lang)
            st.rerun()

    st.divider()

    # Settings
    with st.expander(f"⚙️  {get_text('settings_heading', lang)}"):
        # Theme
        st.markdown('<div class="set-label">Tema / Theme</div>', unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        with tc1:
            if st.button("🌙  Escuro", use_container_width=True, type="primary" if theme=="dark" else "secondary"):
                if theme != "dark":
                    st.session_state.theme = "dark"; save_preference("theme","dark"); st.rerun()
        with tc2:
            if st.button("☀️  Claro", use_container_width=True, type="primary" if theme=="light" else "secondary"):
                if theme != "light":
                    st.session_state.theme = "light"; save_preference("theme","light"); st.rerun()

        # Language (2 rows of 4 aligned)
        st.markdown(f'<div class="set-label">{get_text("lang_label", lang)}</div>', unsafe_allow_html=True)
        flags = [("pt","🇧🇷 PT"),("en","🇺🇸 EN"),("es","🇪🇸 ES"),("fr","🇫🇷 FR"),
                 ("zh","🇨🇳 ZH"),("hi","🇮🇳 HI"),("ar","🇸🇦 AR"),("bn","🇧🇩 BN")]
        lc = st.columns(4)
        for i, (code, lbl) in enumerate(flags):
            with lc[i % 4]:
                if st.button(lbl, key=f"l_{code}", use_container_width=True,
                             type="primary" if lang==code else "secondary"):
                    if lang != code:
                        st.session_state.lang = code; save_preference("language", code)
                        st.session_state.agent = AncoraAgent(model_id=st.session_state.selected_model, lang=code)
                        st.rerun()

        # Model (2x2 aligned grid)
        st.markdown(f'<div class="set-label">{get_text("model_label", lang)}</div>', unsafe_allow_html=True)
        mdls = [("gemini-3.7-flash","⚡ Flash 3.7"),("gemini-3.1-pro","🧠 Pro 3.1"),
                ("claude-3-5-sonnet","🏛️ Claude 3.5"),("offline","🛡️ Offline")]
        sm = st.session_state.selected_model
        mc = st.columns(2)
        for i, (mid, mlbl) in enumerate(mdls):
            with mc[i % 2]:
                if st.button(mlbl, key=f"m_{mid}", use_container_width=True,
                             type="primary" if sm==mid else "secondary"):
                    if sm != mid:
                        st.session_state.selected_model = mid; save_preference("selected_model", mid)
                        st.session_state.agent = AncoraAgent(model_id=mid, lang=lang)
                        st.rerun()

        # LGPD
        st.markdown("---")
        st.markdown(f'<div class="set-label">{get_text("lgpd_heading", lang)}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="badge b-green">{get_text("lgpd_badge", lang)}</span>', unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        exp_d = export_user_data_lgpd()
        st.download_button(get_text("lgpd_export_btn", lang),
            data=json.dumps(exp_d, indent=2, ensure_ascii=False),
            file_name=f"ancora_lgpd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json", use_container_width=True)
        if st.button(get_text("lgpd_delete_btn", lang), use_container_width=True):
            delete_all_user_data_lgpd()
            iid = "conv_1"; wc = get_text("default_welcome", lang)
            st.session_state.conversations = {iid:{"title":"Clareza & Alinhamento TCC","messages":[{"role":"assistant","thought":"","content":wc}]}}
            st.session_state.current_conv_id = iid
            save_chat_session(iid, "Clareza & Alinhamento TCC")
            st.success(get_text("lgpd_deleted_success", lang))
            st.rerun()

# ══════════════════════════════════════════════════════════════
# MAIN CANVAS
# ══════════════════════════════════════════════════════════════
model_labels = {"gemini-3.7-flash":"Gemini 3.7 Flash","gemini-3.1-pro":"Gemini 3.1 Pro",
                "claude-3-5-sonnet":"Claude 3.5 Sonnet","offline":"Offline · TCC/ACT"}
badge_label = model_labels.get(st.session_state.selected_model, "Gemini")
lang_flag = SUPPORTED_LANGUAGES.get(lang, {}).get("flag", "🌐")

st.markdown(f"""
<div class="topbar">
  <div>
    <div class="topbar-title">⚓ {current_conv['title']}</div>
    <div class="topbar-sub">Modo: {st.session_state.active_mode}</div>
  </div>
  <div class="topbar-badge">{lang_flag}  {badge_label}</div>
</div>
""", unsafe_allow_html=True)

# ─── CHAT ────────────────────────────────────────────────────
if st.session_state.active_mode == get_text("mode_chat", lang):
    for msg in current_conv["messages"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ai-wrap">', unsafe_allow_html=True)
            if msg.get("thought"):
                with st.expander(get_text("thought_title", lang), expanded=False):
                    st.markdown(f'<div class="thought-body">{msg["thought"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="assistant-body">{msg["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if user_prompt := st.chat_input(get_text("input_placeholder", lang)):
        current_conv["messages"].append({"role":"user","content":user_prompt})
        save_chat_message(st.session_state.current_conv_id, "user", user_prompt)
        st.markdown(f'<div class="user-bubble">{user_prompt}</div>', unsafe_allow_html=True)

        if len(current_conv["messages"]) == 2:
            t = st.session_state.agent.generate_chat_title(user_prompt)
            current_conv["title"] = t
            save_chat_session(st.session_state.current_conv_id, t)

        ph = st.empty()
        for step in get_dynamic_thinking_steps(user_prompt, lang=lang):
            ph.markdown(f'<div class="thinking-box"><div class="thinking-spinner"></div><span>{step}</span></div>', unsafe_allow_html=True)
            time.sleep(0.32)

        resp = st.session_state.agent.respond(user_prompt, model_override=st.session_state.selected_model, lang_override=lang)
        ph.empty()
        thought_s = resp.get("thought",""); content_s = resp.get("content","")
        current_conv["messages"].append({"role":"assistant","thought":thought_s,"content":content_s})
        save_chat_message(st.session_state.current_conv_id, "assistant", content_s, thought_s)
        st.rerun()

# ─── MESSAGE LAB ─────────────────────────────────────────────
elif st.session_state.active_mode == get_text("mode_msg_lab", lang):
    st.markdown("### 📱 Message Lab & Flirt Rater")
    st.caption("Diagnóstico comportamental de mensagens — confiança, carência, banter.")
    c1, c2 = st.columns(2)
    with c1:
        msg_in = st.text_area("Mensagem para análise:", height=140, placeholder="Ex: Oi linda, você sumiu...")
        aud = st.radio("Contexto:", ["Romântico / Flerte","Profissional / Limites"], horizontal=True)
        if st.button(get_text("diagnose_btn", lang), type="primary", use_container_width=True):
            if msg_in:
                st.session_state["lab_res"] = analyze_message_and_rewrite(msg_in, "romantic" if "Romântico" in aud else "professional")
    with c2:
        if "lab_res" in st.session_state:
            r = st.session_state["lab_res"]
            st.markdown(f'<div class="card"><h4>Diagnóstico</h4><p>Confiança: <code>{r["confidence_score"]}/100</code> &nbsp;·&nbsp; Carência: <span class="badge b-indigo">{r["neediness_level"]}</span> &nbsp;·&nbsp; Banter: <span class="badge b-cyan">{r["banter_level"]}</span></p></div>', unsafe_allow_html=True)
            for rw in r["rewrites"]:
                st.markdown(f'<div class="card card-accent"><span class="badge b-indigo">{rw["style"]}</span><p style="margin:8px 0 4px;font-weight:500;">"{rw["text"]}"</p><small>{rw["rationale"]}</small></div>', unsafe_allow_html=True)

# ─── ROLEPLAY ────────────────────────────────────────────────
elif st.session_state.active_mode == get_text("mode_roleplay", lang):
    st.markdown("### 🎭 Arena de Simulação em Tempo Real")
    st.caption("Pratique negociação com chefe, flerte ou networking em ambiente seguro.")
    scens = {k: v["title"] for k, v in ROLEPLAY_SCENARIOS.items()}
    chosen = st.selectbox("Cenário:", list(scens.keys()), format_func=lambda x: scens[x])
    meta = get_scenario_details(chosen)
    if "rp_chat" not in st.session_state or st.session_state.get("rp_sc") != chosen:
        st.session_state.rp_chat = [{"role":"partner","content":meta["initial_message"]}]
        st.session_state.rp_sc = chosen
    if st.button(get_text("restart_sim_btn", lang), use_container_width=True):
        st.session_state.rp_chat = [{"role":"partner","content":meta["initial_message"]}]
        st.rerun()
    for m in st.session_state.rp_chat:
        if m["role"] == "partner":
            st.markdown(f'<div class="card" style="border-left:3px solid #8b5cf6"><strong>{meta["partner_name"]}:</strong> {m["content"]}</div>', unsafe_allow_html=True)
        elif m["role"] == "user":
            st.markdown(f'<div class="user-bubble">{m["content"]}</div>', unsafe_allow_html=True)
        elif m["role"] == "coach":
            st.markdown(f'<div class="thought-body" style="margin-bottom:10px">{m["content"]}</div>', unsafe_allow_html=True)
    if rp_in := st.chat_input("Sua resposta na simulação..."):
        st.session_state.rp_chat.append({"role":"user","content":rp_in})
        out = generate_roleplay_turn(chosen, st.session_state.rp_chat, rp_in)
        st.session_state.rp_chat.append({"role":"partner","content":out["reply"]})
        if out.get("coach_tip"): st.session_state.rp_chat.append({"role":"coach","content":out["coach_tip"]})
        if out.get("scorecard"):
            st.balloons(); st.success(f"🏆 Concluído! Nota: {out['scorecard']['overall_score']}/100")
        st.rerun()

# ─── DECOMPRESSION ───────────────────────────────────────────
elif st.session_state.active_mode == get_text("mode_decompress", lang):
    st.markdown("### 🫁 Descompressão & Regulação Somática")
    st.caption("Protocolos neurocientíficos de alívio para sobrecarga do sistema nervoso.")
    c1, c2 = st.columns(2)
    with c1:
        techs = [("physiological_sigh","Suspiro Fisiológico (Huberman)"),
                 ("box_breathing","Box Breathing (Navy SEALs)"),
                 ("grounding_54321","Ancoragem Tátil 5-4-3-2-1"),
                 ("perspective_reset","Reset de Perspectiva")]
        tech = st.selectbox("Protocolo:", techs, format_func=lambda x: x[1])
        rd = get_decompression_routine(tech[0])
        steps_html = "".join(f"<li style='margin-bottom:5px'>{s}</li>" for s in rd["steps"])
        st.markdown(f'<div class="card"><h4>{rd["name"]}</h4><span class="badge b-cyan">{rd["duration"]}</span><ol style="margin:12px 0 0 18px;line-height:1.7;color:var(--tx);">{steps_html}</ol></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("#### Sons Ambientes")
        s_opt = st.selectbox("Som:", ["Chuva Suave","Ondas do Oceano","Lareira"])
        urls = {"Chuva Suave":"https://assets.mixkit.co/active_storage/sfx/1253/1253-preview.mp3","Ondas do Oceano":"https://assets.mixkit.co/active_storage/sfx/1189/1189-preview.mp3","Lareira":"https://assets.mixkit.co/active_storage/sfx/1243/1243-preview.mp3"}
        st.audio(urls[s_opt], format="audio/mp3")

# ─── DASHBOARD ───────────────────────────────────────────────
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
    tg = st.multiselect("Emoções:", ["Focado","Confiante","Tranquilo","Ansioso","Sobrecarregado","Cansado"])
    tr = st.text_input("Contexto:")
    if st.button(get_text("save_journal_btn", lang), use_container_width=True, type="primary"):
        record_mood_entry(sc, tg, tr, "")
        st.success("Salvo com sucesso!")
