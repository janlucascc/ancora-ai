import streamlit as st
import os
import sys
import json
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.agent.core import AncoraAgent
from src.tools.mood_journal import record_mood_entry, get_mood_history
from src.tools.stress_decompress import get_decompression_routine
from src.tools.social_wingman import generate_wingman_advice
from src.tools.message_analyzer import analyze_message_and_rewrite
from src.tools.roleplay_arena import ROLEPLAY_SCENARIOS, get_scenario_details, generate_roleplay_turn
from src.database.db import get_mood_stats
from src.ui.i18n import get_system_language, get_text, TRANSLATIONS

# Auto-detect language once
if "lang" not in st.session_state:
    st.session_state.lang = get_system_language()

lang = st.session_state.lang

# Page Config
st.set_page_config(
    page_title=get_text("app_title", lang),
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# MODERN DARK GLASSMORPHIC & ANIMATED UI CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-main: #0f1013;
        --bg-sidebar: #14151a;
        --bg-card: #191a22;
        --bg-user-bubble: #22242e;
        --border-color: #272833;
        --text-main: #f1f5f9;
        --text-muted: #94a3b8;
        --accent-blue: #3b82f6;
        --accent-cyan: #38bdf8;
    }

    html, body, [class*="css"], .stApp {
        background-color: var(--bg-main) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-main) !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
        max-width: 940px !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color) !important;
    }

    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-bubble, .assistant-body, .thought-container, .ide-card {
        animation: fadeInSlide 0.25s ease-out;
    }

    .status-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        background-color: #22c55e;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 8px #22c55e;
        animation: pulseDot 2s infinite;
    }
    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    .ancora-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0px 14px 0px;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }
    .topbar-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f1f5f9;
    }
    .topbar-badge {
        font-size: 0.75rem;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(56, 189, 248, 0.1) 100%);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 500;
    }

    .user-bubble {
        background-color: var(--bg-user-bubble);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 13px 18px;
        color: #f8fafc;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .assistant-body {
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.65;
    }

    .thought-container {
        background-color: rgba(25, 26, 34, 0.7);
        border-left: 2px solid #38bdf8;
        border-radius: 4px;
        padding: 10px 14px;
        margin-bottom: 12px;
        font-size: 0.85rem;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
    }

    .stButton>button {
        background: linear-gradient(180deg, #1b1c24 0%, #16171d 100%) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover {
        border-color: var(--accent-blue) !important;
        background: #232530 !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    .stChatInput {
        border-color: var(--border-color) !important;
        background-color: var(--bg-sidebar) !important;
        border-radius: 14px !important;
    }
    .stChatInput:focus-within {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.25) !important;
    }

    .ide-card {
        background: linear-gradient(180deg, #191a22 0%, #15161c 100%);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .ide-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35), 0 0 12px rgba(56, 189, 248, 0.12);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-3.6-flash"

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
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"### ⚓ **{get_text('sidebar_brand', lang)}** <span style='font-size:0.75rem; color:#64748b;'>v2.0</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='status-dot'></span><small style='color:#94a3b8;'>{get_text('sidebar_status', lang)}</small>", unsafe_allow_html=True)
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
                    "content": "Nova sessão iniciada. O que está acontecendo agora que você quer examinar com clareza?" if lang == "pt" else "New session started. What would you like to examine clearly today?"
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

    # Settings & Model Selection Drawer
    with st.expander(get_text("settings_heading", lang)):
        # 1. Model Selector
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
            st.session_state.agent = AncoraAgent(model_id=chosen_model_key, lang=lang)
            st.toast(f"Modelo alterado para: {model_choices[chosen_model_key]}")

        # 2. Language Selector
        lang_choices = {"pt": "🇧🇷 Português (Brasil)", "en": "🇺🇸 English (US)"}
        chosen_lang = st.selectbox(
            get_text("lang_label", lang),
            ["pt", "en"],
            format_func=lambda x: lang_choices[x],
            index=0 if lang == "pt" else 1
        )
        if chosen_lang != st.session_state.lang:
            st.session_state.lang = chosen_lang
            st.rerun()

        # 3. Gemini API Key input
        custom_key = st.text_input("Gemini API Key:", type="password", placeholder="AQ.Ab8RN...")
        if st.button("Salvar Chave / Save Key", use_container_width=True):
            if custom_key:
                os.environ["GEMINI_API_KEY"] = custom_key
                st.session_state.agent = AncoraAgent(api_key=custom_key, model_id=st.session_state.selected_model, lang=lang)
                st.success("Chave salva com sucesso!")

# ══════════════════════════════════════════════════════════════
# MAIN CANVAS
# ══════════════════════════════════════════════════════════════

# Model Badge Label
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
        ⚓ {current_conv['title']} &nbsp;·&nbsp; <span style="font-weight:400; font-size:0.8rem; color:#64748b;">Modo: {st.session_state.active_mode}</span>
    </div>
    <div class="topbar-badge">
        {active_model_badge}
    </div>
</div>
""", unsafe_allow_html=True)

# ─── VIEW 1: CHAT LIVRE ──────────────────────────────────────
if st.session_state.active_mode == get_text("mode_chat", lang):
    # Render all historic messages
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

    # User Input & Instant Message Display
    if user_prompt := st.chat_input(get_text("input_placeholder", lang)):
        # 1. Immediately append to conversation history
        current_conv["messages"].append({"role": "user", "content": user_prompt})
        
        # 2. Render user message right away so it appears on screen immediately!
        st.markdown(f"""
        <div class="user-bubble">
            {user_prompt}
        </div>
        """, unsafe_allow_html=True)

        if len(current_conv["messages"]) == 2:
            clean_title = user_prompt.replace("⚓", "").replace("💬", "").strip()
            current_conv["title"] = clean_title[:25]

        # 3. Model generation with spinner
        with st.spinner(get_text("analyzing_spinner", lang)):
            response_dict = st.session_state.agent.respond(
                user_prompt,
                model_override=st.session_state.selected_model,
                lang_override=lang
            )
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
                <div class="ide-card" style="border-left: 3px solid #3b82f6;">
                    <span style="font-size:0.8rem; color:#60a5fa; font-weight:600;">{rw['style']}</span>
                    <p style="margin:6px 0; font-size:0.95rem; font-weight:500;">"{rw['text']}"</p>
                    <small style="color:#94a3b8;"><em>{rw['rationale']}</em></small>
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
            <p><small style="color:#60a5fa;">{r_data['duration']}</small></p>
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
