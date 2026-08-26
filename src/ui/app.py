import streamlit as st
import os
import sys
import json
import time
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
    delete_all_user_data_lgpd
)
from src.ui.i18n import get_system_language, get_text, SUPPORTED_LANGUAGES

# ══════════════════════════════════════════════════════════════
# PERSISTENT SETTINGS INITIALIZATION (Database -> Session State)
# ══════════════════════════════════════════════════════════════
if "lang" not in st.session_state:
    stored_lang = get_preference("language", "")
    st.session_state.lang = stored_lang if stored_lang in SUPPORTED_LANGUAGES else get_system_language()

if "theme" not in st.session_state:
    st.session_state.theme = get_preference("theme", "dark")

if "selected_model" not in st.session_state:
    st.session_state.selected_model = get_preference("selected_model", "gemini-3.6-flash")

lang = st.session_state.lang
theme = st.session_state.theme

# Page Config
st.set_page_config(
    page_title=get_text("app_title", lang),
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# THEME ENGINE (DARK & FLAWLESS LIGHT CSS)
# ══════════════════════════════════════════════════════════════
if theme == "light":
    css_theme_vars = """
        --bg-main: #f8fafc;
        --bg-sidebar: #f1f5f9;
        --bg-card: #ffffff;
        --bg-user-bubble: #e2e8f0;
        --border-color: #cbd5e1;
        --text-main: #0f172a;
        --text-muted: #64748b;
        --accent-blue: #2563eb;
        --accent-cyan: #0284c7;
        --thought-bg: rgba(241, 245, 249, 0.9);
        --thought-text: #475569;
        --shimmer-bg: linear-gradient(90deg, rgba(226, 232, 240, 0.6) 0%, rgba(186, 230, 253, 0.6) 50%, rgba(226, 232, 240, 0.6) 100%);
    """
else:
    css_theme_vars = """
        --bg-main: #0f1013;
        --bg-sidebar: #14151a;
        --bg-card: #191a22;
        --bg-user-bubble: #22242e;
        --border-color: #272833;
        --text-main: #f1f5f9;
        --text-muted: #94a3b8;
        --accent-blue: #3b82f6;
        --accent-cyan: #38bdf8;
        --thought-bg: rgba(25, 26, 34, 0.7);
        --thought-text: #94a3b8;
        --shimmer-bg: linear-gradient(90deg, rgba(30, 41, 59, 0.4) 0%, rgba(56, 189, 248, 0.1) 50%, rgba(30, 41, 59, 0.4) 100%);
    """

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {{
        {css_theme_vars}
    }}

    html, body, [class*="css"], .stApp {{
        background-color: var(--bg-main) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-main) !important;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 940px !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color) !important;
    }}

    @keyframes fadeInSlide {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .user-bubble, .assistant-body, .thought-container, .ide-card {{
        animation: fadeInSlide 0.25s ease-out;
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

    .ancora-topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0px 14px 0px;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }}
    .topbar-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-main);
    }}
    .topbar-badge {{
        font-size: 0.75rem;
        background: rgba(59, 130, 246, 0.12);
        color: var(--accent-blue);
        border: 1px solid var(--border-color);
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 500;
    }}

    .user-bubble {{
        background-color: var(--bg-user-bubble);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 13px 18px;
        color: var(--text-main);
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }}

    .assistant-body {{
        color: var(--text-main);
        font-size: 0.95rem;
        line-height: 1.65;
    }}

    .thought-container {{
        background-color: var(--thought-bg);
        border-left: 2px solid var(--accent-cyan);
        border-radius: 4px;
        padding: 10px 14px;
        margin-bottom: 12px;
        font-size: 0.85rem;
        color: var(--thought-text);
        font-family: 'JetBrains Mono', monospace;
    }}

    .stButton>button {{
        background: var(--bg-card) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton>button:hover {{
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.2) !important;
        transform: translateY(-1px) !important;
    }}

    .stChatInput {{
        border-color: var(--border-color) !important;
        background-color: var(--bg-sidebar) !important;
        border-radius: 14px !important;
    }}
    .stChatInput:focus-within {{
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.2) !important;
    }}

    .ide-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }}
    .ide-card:hover {{
        border-color: var(--accent-cyan);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transform: translateY(-1px);
    }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE & PERSISTENCE
# ══════════════════════════════════════════════════════════════
if "conversations" not in st.session_state:
    st.session_state.conversations = {
        "conv_1": {
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

if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = "conv_1"

if "agent" not in st.session_state:
    st.session_state.agent = AncoraAgent(model_id=st.session_state.selected_model, lang=lang)

if "active_mode" not in st.session_state:
    st.session_state.active_mode = get_text("mode_chat", lang)

current_conv = st.session_state.conversations[st.session_state.current_conv_id]

# ══════════════════════════════════════════════════════════════
# SIDEBAR (8 Languages, Themes & LGPD Tools)
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"### ⚓ **{get_text('sidebar_brand', lang)}** <span style='font-size:0.75rem; color:var(--text-muted);'>v2.0</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='status-dot'></span><small style='color:var(--text-muted);'>{get_text('sidebar_status', lang)}</small>", unsafe_allow_html=True)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # New Conversation Button
    if st.button(get_text("new_chat_btn", lang), use_container_width=True):
        new_id = f"conv_{len(st.session_state.conversations) + 1}"
        st.session_state.conversations[new_id] = {
            "title": f"Conversa {len(st.session_state.conversations) + 1}",
            "messages": [
                {
                    "role": "assistant",
                    "thought": "Nova sessão criada.",
                    "content": get_text("default_welcome", lang)
                }
            ]
        }
        st.session_state.current_conv_id = new_id
        st.session_state.active_mode = get_text("mode_chat", lang)
        st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Mode Selector
    st.caption(get_text("tools_heading", lang))
    mode_options = [
        get_text("mode_chat", lang),
        get_text("mode_msg_lab", lang),
        get_text("mode_roleplay", lang),
        get_text("mode_decompress", lang),
        get_text("mode_dashboard", lang)
    ]
    selected_mode = st.radio("Modo:", mode_options, label_visibility="collapsed")
    st.session_state.active_mode = selected_mode

    st.divider()

    # Conversation History List
    st.caption(get_text("recent_convs", lang))
    for cid, cdata in list(st.session_state.conversations.items()):
        is_active = (cid == st.session_state.current_conv_id)
        display_title = cdata['title'][:22]
        label = f"• {display_title}..." if is_active else f"  {display_title}..."
        if st.button(label, key=f"btn_{cid}", use_container_width=True):
            st.session_state.current_conv_id = cid
            st.session_state.active_mode = get_text("mode_chat", lang)
            st.rerun()

    st.divider()

    # Settings Drawer (Theme, Language, Model & LGPD)
    with st.expander(get_text("settings_heading", lang)):
        # 1. Theme Switcher (Dark vs Light)
        theme_choices = {
            "dark": get_text("theme_dark", lang),
            "light": get_text("theme_light", lang)
        }
        chosen_theme = st.selectbox(
            get_text("theme_label", lang),
            ["dark", "light"],
            format_func=lambda t: theme_choices[t],
            index=0 if st.session_state.theme == "dark" else 1
        )
        if chosen_theme != st.session_state.theme:
            st.session_state.theme = chosen_theme
            save_preference("theme", chosen_theme)
            st.rerun()

        # 2. 8 Most Spoken Languages in the World Selector
        lang_keys = list(SUPPORTED_LANGUAGES.keys())
        chosen_lang = st.selectbox(
            get_text("lang_label", lang),
            lang_keys,
            format_func=lambda code: f"{SUPPORTED_LANGUAGES[code]['flag']} {SUPPORTED_LANGUAGES[code]['label']}",
            index=lang_keys.index(st.session_state.lang) if st.session_state.lang in lang_keys else 0
        )
        if chosen_lang != st.session_state.lang:
            st.session_state.lang = chosen_lang
            save_preference("language", chosen_lang)
            st.session_state.agent = AncoraAgent(model_id=st.session_state.selected_model, lang=chosen_lang)
            st.rerun()

        # 3. Model Selector
        model_choices = {
            "gemini-3.6-flash": "⚡ Gemini 3.6 Flash (Padrão Rápido)",
            "gemini-3.7-flash": "🧠 Gemini 3.7 Flash (Raciocínio)",
            "claude-3-5-sonnet": "🏛️ Claude 3.5 Sonnet (AWS Bedrock)",
            "offline": "🛡️ Modo Offline (TCC/ACT Local)"
        }
        chosen_model_key = st.selectbox(
            get_text("model_label", lang),
            list(model_choices.keys()),
            format_func=lambda x: model_choices[x],
            index=list(model_choices.keys()).index(st.session_state.selected_model) if st.session_state.selected_model in model_choices else 0
        )
        if chosen_model_key != st.session_state.selected_model:
            st.session_state.selected_model = chosen_model_key
            save_preference("selected_model", chosen_model_key)
            st.session_state.agent = AncoraAgent(model_id=chosen_model_key, lang=lang)
            st.toast(f"Modelo: {model_choices[chosen_model_key]}")

        # 4. LGPD & Privacy Section
        st.markdown("---")
        st.caption(get_text("lgpd_heading", lang))
        st.markdown(f"<small style='color:#22c55e;'>{get_text('lgpd_badge', lang)}</small>", unsafe_allow_html=True)
        
        # Export Data (LGPD Art. 18, II)
        user_export_data = export_user_data_lgpd()
        st.download_button(
            label=get_text("lgpd_export_btn", lang),
            data=json.dumps(user_export_data, indent=2, ensure_ascii=False),
            file_name=f"ancora_ai_lgpd_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

        # Delete Data (LGPD Art. 18, VI)
        if st.button(get_text("lgpd_delete_btn", lang), use_container_width=True):
            delete_all_user_data_lgpd()
            st.session_state.conversations = {
                "conv_1": {
                    "title": "Clareza & Alinhamento TCC" if lang == "pt" else "Clarity & CBT Alignment",
                    "messages": [{"role": "assistant", "thought": "Dados limpos.", "content": get_text("default_welcome", lang)}]
                }
            }
            st.success(get_text("lgpd_deleted_success", lang))
            st.rerun()

# ══════════════════════════════════════════════════════════════
# MAIN CANVAS
# ══════════════════════════════════════════════════════════════

model_display_names = {
    "gemini-3.6-flash": "Gemini 3.6 Flash / Live",
    "gemini-3.7-flash": "Gemini 3.7 Flash / Deep",
    "claude-3-5-sonnet": "Claude 3.5 Sonnet / AWS Bedrock",
    "offline": "Offline TCC/ACT Engine"
}
active_model_badge = model_display_names.get(st.session_state.selected_model, "Gemini Live")

# Top Bar
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
            st.markdown(f"""
            <div class="user-bubble">
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            if msg.get("thought"):
                with st.expander(get_text("thought_title", lang)):
                    st.markdown(f"""
                    <div class="thought-container">
                        {msg['thought']}
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="assistant-body">
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # Chat Input with Instant Display & Shimmer Thought Steps
    if user_prompt := st.chat_input(get_text("input_placeholder", lang)):
        current_conv["messages"].append({"role": "user", "content": user_prompt})
        
        # Render user message right away
        st.markdown(f"""
        <div class="user-bubble">
            {user_prompt}
        </div>
        """, unsafe_allow_html=True)

        if len(current_conv["messages"]) == 2:
            clean_title = user_prompt.replace("⚓", "").replace("💬", "").strip()
            current_conv["title"] = clean_title[:25]

        # Live Shimmer Thought Animation
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

        # Invoke Agent
        response_dict = st.session_state.agent.respond(
            user_prompt,
            model_override=st.session_state.selected_model,
            lang_override=lang
        )

        thinking_placeholder.empty()

        current_conv["messages"].append({
            "role": "assistant",
            "thought": response_dict.get("thought", ""),
            "content": response_dict.get("content", "")
        })

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
            st.markdown(f"""
            <div class="ide-card">
                <h4>Diagnóstico da Mensagem</h4>
                <p><strong>Confiança:</strong> <code>{res['confidence_score']}/100</code></p>
                <p><strong>Nível de Pressão/Carência:</strong> {res['neediness_level']}</p>
                <p><strong>Engajamento/Banter:</strong> {res['banter_level']}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 3 Alternativas Estruturadas:")
            for rw in res["rewrites"]:
                st.markdown(f"""
                <div class="ide-card" style="border-left: 3px solid var(--accent-blue);">
                    <span style="font-size:0.8rem; color:var(--accent-cyan); font-weight:600;">{rw['style']}</span>
                    <p style="margin:6px 0; font-size:0.95rem; font-weight:500;">"{rw['text']}"</p>
                    <small style="color:var(--text-muted);"><em>{rw['rationale']}</em></small>
                </div>
                """, unsafe_allow_html=True)

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
        tech = st.selectbox("Escolha o protocolo:", [
            ("physiological_sigh", "Suspiro Fisiológico (Huberman — Alívio em 1 min)"),
            ("box_breathing", "Box Breathing (Respiração Quadrada — Navy SEALs)"),
            ("grounding_54321", "Ancoragem Tátil 5-4-3-2-1"),
            ("perspective_reset", "Reset de Perspectiva")
        ], format_func=lambda x: x[1])
        r_data = get_decompression_routine(tech[0])

        st.markdown(f"""
        <div class="ide-card">
            <h4>{r_data['name']}</h4>
            <p><small style="color:var(--accent-cyan);">{r_data['duration']}</small></p>
            <ol style="margin-left: 18px; line-height: 1.7;">
                {"".join(f"<li>{s}</li>" for s in r_data['steps'])}
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Sons Ambientes")
        s_opt = st.selectbox("Som de fundo:", ["Chuva Suave", "Ondas do Oceano", "Lareira"])
        urls = {
            "Chuva Suave": "https://assets.mixkit.co/active_storage/sfx/1253/1253-preview.mp3",
            "Ondas do Oceano": "https://assets.mixkit.co/active_storage/sfx/1189/1189-preview.mp3",
            "Lareira": "https://assets.mixkit.co/active_storage/sfx/1243/1243-preview.mp3"
        }
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
