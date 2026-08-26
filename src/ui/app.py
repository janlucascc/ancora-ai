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

# Page Config
st.set_page_config(
    page_title="Ancora AI | Antigravity Workspace",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# ANTIGRAVITY DARK THEME & MINIMALIST IDE CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Colors & Reset */
    :root {
        --bg-main: #131417;
        --bg-sidebar: #18191d;
        --bg-card: #1e1f25;
        --bg-user-bubble: #272932;
        --border-color: #2b2d37;
        --text-main: #e2e8f0;
        --text-muted: #94a3b8;
        --accent-blue: #3b82f6;
        --accent-hover: #2563eb;
    }

    html, body, [class*="css"], .stApp {
        background-color: var(--bg-main) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-main) !important;
    }

    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 950px !important;
    }

    /* Sidebar Styling (Antigravity Look) */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--border-color) !important;
    }

    /* Antigravity Header Bar */
    .antigravity-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 16px;
        background-color: transparent;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 24px;
    }
    .topbar-title {
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--text-muted);
    }
    .topbar-badge {
        font-size: 0.75rem;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 500;
    }

    /* Chat Bubbles */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 8px 0px !important;
    }

    /* User Message Bubble */
    .user-bubble {
        background-color: var(--bg-user-bubble);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 14px 18px;
        color: #f1f5f9;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 12px;
    }

    /* Assistant Message */
    .assistant-body {
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Thought / Reasoning Collapsible Block (Antigravity Style) */
    .thought-container {
        background-color: rgba(30, 31, 37, 0.6);
        border-left: 2px solid #64748b;
        border-radius: 4px;
        padding: 8px 14px;
        margin-bottom: 14px;
        font-size: 0.85rem;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
    }

    /* New Chat Button */
    .stButton>button {
        background-color: var(--bg-card) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        border-color: var(--accent-blue) !important;
        background-color: #282a33 !important;
    }

    /* Bottom Input Container */
    .stChatInput {
        border-color: var(--border-color) !important;
        background-color: var(--bg-sidebar) !important;
        border-radius: 14px !important;
    }
    .stChatInput:focus-within {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 1px var(--accent-blue) !important;
    }

    /* Cards & Panels */
    .ide-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Subtle Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: #2b2d37;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════
if "conversations" not in st.session_state:
    st.session_state.conversations = {
        "conv_1": {
            "title": "⚓ Clareza & Alinhamento TCC",
            "messages": [
                {
                    "role": "assistant",
                    "thought": "Sistema inicializado. Protocolo de psicologia comportamental e social ativo.",
                    "content": "Olá. Eu sou o **Ancora AI** ⚓ — trabalho com psicologia comportamental (TCC/ACT) e inteligência social para trazer clareza prática e honesta nos momentos de estresse, trabalho ou relacionamentos.\n\nO que você gostaria de colocar na mesa hoje?"
                }
            ]
        }
    }

if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = "conv_1"

if "agent" not in st.session_state:
    st.session_state.agent = AncoraAgent()

if "active_mode" not in st.session_state:
    st.session_state.active_mode = "Chat Livre"

current_conv = st.session_state.conversations[st.session_state.current_conv_id]

# ══════════════════════════════════════════════════════════════
# SIDEBAR (Antigravity Navigation Style)
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚓ **Antigravity** <span style='font-size:0.75rem; color:#64748b;'>v2.0</span>", unsafe_allow_html=True)
    
    # New Conversation Button
    if st.button("＋ New Conversation", use_container_width=True):
        new_id = f"conv_{len(st.session_state.conversations) + 1}"
        st.session_state.conversations[new_id] = {
            "title": f"Nova Conversa {len(st.session_state.conversations) + 1}",
            "messages": [
                {
                    "role": "assistant",
                    "thought": "Nova sessão criada. Princípios de honestidade, separação de fatos e grounding ativos.",
                    "content": "Nova sessão iniciada. O que está acontecendo agora que você quer examinar com clareza?"
                }
            ]
        }
        st.session_state.current_conv_id = new_id
        st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Mode Selector
    st.caption("FERRAMENTAS & MODOS")
    selected_mode = st.radio(
        "Modo:",
        ["Chat Livre", "Message Lab (Flerte/Trabalho)", "Arena de Simulação (Roleplay)", "Descompressão Somática", "Dashboard & Métricas"],
        label_visibility="collapsed"
    )
    st.session_state.active_mode = selected_mode

    st.divider()

    # Conversation History List (Like Antigravity sidebar)
    st.caption("CONVERSAS RECENTES")
    for cid, cdata in list(st.session_state.conversations.items()):
        is_active = (cid == st.session_state.current_conv_id)
        label = f"💬 {cdata['title'][:22]}..." if is_active else f"{cdata['title'][:22]}..."
        if st.button(label, key=f"btn_{cid}", use_container_width=True):
            st.session_state.current_conv_id = cid
            st.session_state.active_mode = "Chat Livre"
            st.rerun()

    st.divider()

    # Settings / Provider Info at the Bottom
    with st.expander("⚙️ Configurações & API Keys"):
        custom_key = st.text_input("Google Gemini API Key (Opcional):", type="password", placeholder="AIzaSy...")
        if st.button("Salvar Chave", use_container_width=True):
            if custom_key:
                os.environ["GEMINI_API_KEY"] = custom_key
                st.session_state.agent = AncoraAgent(api_key=custom_key)
                st.success("Motor Gemini conectado com sucesso!")
        st.caption("AWS Bedrock ativo via `.env` ou chaves IAM.")

# ══════════════════════════════════════════════════════════════
# MAIN CANVAS (Antigravity UI Layout)
# ══════════════════════════════════════════════════════════════

# Top Bar
st.markdown(f"""
<div class="antigravity-topbar">
    <div class="topbar-title">
        ⚓ <strong>{current_conv['title']}</strong> &nbsp;·&nbsp; <span style="font-size:0.8rem; color:#64748b;">Modo: {st.session_state.active_mode}</span>
    </div>
    <div class="topbar-badge">
        Claude 3.5 Sonnet / ACT & TCC Engine
    </div>
</div>
""", unsafe_allow_html=True)

# ─── VIEW 1: CHAT LIVRE (Default Antigravity View) ───────────
if st.session_state.active_mode == "Chat Livre":
    # Render Conversation Messages
    for msg in current_conv["messages"]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-bubble">
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Render Thought / Reasoning Box if available (Antigravity Style)
            if msg.get("thought"):
                with st.expander(f"💡 Thought process (TCC / ACT Method)"):
                    st.markdown(f"""
                    <div class="thought-container">
                        {msg['thought']}
                    </div>
                    """, unsafe_allow_html=True)

            # Assistant Content
            st.markdown(f"""
            <div class="assistant-body">
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Bottom Chat Input (Antigravity floating style)
    if user_prompt := st.chat_input("Digite sua dúvida, desabafo ou situação..."):
        # Append User Msg
        current_conv["messages"].append({"role": "user", "content": user_prompt})
        
        # Auto-update conversation title on first user turn
        if len(current_conv["messages"]) == 2:
            current_conv["title"] = user_prompt[:25]

        # Generate Response via Agent
        with st.spinner("Analisando com metodologia comportamental..."):
            response_dict = st.session_state.agent.respond(user_prompt)
            current_conv["messages"].append({
                "role": "assistant",
                "thought": response_dict.get("thought", ""),
                "content": response_dict.get("content", "")
            })

        st.rerun()

# ─── VIEW 2: MESSAGE LAB & WINGMAN ───────────────────────────
elif st.session_state.active_mode == "Message Lab (Flerte/Trabalho)":
    st.markdown("### 📱 **Message Lab & Flirt Rater**")
    st.caption("Diagnóstico comportamental de mensagens antes do envio. Avalia nível de pressão, segurança e autenticidade.")

    col1, col2 = st.columns([1, 1])
    with col1:
        msg_in = st.text_area("Cole a mensagem para análise:", height=140, placeholder="Ex: Oi, vi que você sumiu... queria saber se fiz algo errado...")
        aud = st.radio("Contexto:", ["Romântico / Flerte", "Profissional / Limites"], horizontal=True)
        if st.button("🔥 Diagnosticar Mensagem", type="primary", use_container_width=True):
            if msg_in:
                res = analyze_message_and_rewrite(msg_in, "romantic" if "Romântico" in aud else "professional")
                st.session_state["msg_lab_result"] = res

    with col2:
        if "msg_lab_result" in st.session_state:
            res = st.session_state["msg_lab_result"]
            st.markdown(f"""
            <div class="ide-card">
                <h4>📊 Diagnóstico da Mensagem</h4>
                <p><strong>Confiança:</strong> <code>{res['confidence_score']}/100</code></p>
                <p><strong>Nível de Pressão/Carência:</strong> {res['neediness_level']}</p>
                <p><strong>Engajamento/Banter:</strong> {res['banter_level']}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 💡 3 Alternativas Estruturadas:")
            for rw in res["rewrites"]:
                st.markdown(f"""
                <div class="ide-card" style="border-left: 3px solid #3b82f6;">
                    <span style="font-size:0.8rem; color:#60a5fa; font-weight:600;">{rw['style']}</span>
                    <p style="margin:6px 0; font-size:0.95rem; font-weight:500;">"{rw['text']}"</p>
                    <small style="color:#94a3b8;"><em>{rw['rationale']}</em></small>
                </div>
                """, unsafe_allow_html=True)

# ─── VIEW 3: ARENA DE SIMULAÇÃO (ROLEPLAY) ───────────────────
elif st.session_state.active_mode == "Arena de Simulação (Roleplay)":
    st.markdown("### 🎭 **Arena de Simulação em Tempo Real**")
    st.caption("Pratique conversas de alta pressão (negociação com chefe, primeiro encontro, limites) em um ambiente seguro.")

    scenarios = {k: v["title"] for k, v in ROLEPLAY_SCENARIOS.items()}
    chosen_k = st.selectbox("Selecione o cenário:", list(scenarios.keys()), format_func=lambda x: scenarios[x])
    meta = get_scenario_details(chosen_k)

    if "rp_chat" not in st.session_state or st.session_state.get("rp_scenario") != chosen_k:
        st.session_state.rp_chat = [{"role": "partner", "content": meta["initial_message"]}]
        st.session_state.rp_scenario = chosen_k

    if st.button("🔄 Reiniciar Simulação"):
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
elif st.session_state.active_mode == "Descompressão Somática":
    st.markdown("### 🫁 **Descompressão & Regulação Somática**")
    st.caption("Protocolos neurocientíficos de alívio rápido para quando o sistema nervoso estiver em sobrecarga.")

    col1, col2 = st.columns([1, 1])
    with col1:
        tech = st.selectbox("Escolha o protocolo:", [
            ("physiological_sigh", "⚡ Suspiro Fisiológico (Huberman — Alívio em 1 min)"),
            ("box_breathing", "🫁 Box Breathing (Respiração Quadrada — Navy SEALs)"),
            ("grounding_54321", "⚓ Ancoragem Tátil 5-4-3-2-1"),
            ("perspective_reset", "🧠 Reset de Perspectiva")
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
        st.markdown("#### 🎧 Sons Ambientes")
        s_opt = st.selectbox("Som de fundo:", ["Chuva Suave", "Ondas do Oceano", "Lareira"])
        urls = {
            "Chuva Suave": "https://assets.mixkit.co/active_storage/sfx/1253/1253-preview.mp3",
            "Ondas do Oceano": "https://assets.mixkit.co/active_storage/sfx/1189/1189-preview.mp3",
            "Lareira": "https://assets.mixkit.co/active_storage/sfx/1243/1243-preview.mp3"
        }
        st.audio(urls[s_opt], format="audio/mp3")

# ─── VIEW 5: DASHBOARD & MÉTRICAS ───────────────────────────
elif st.session_state.active_mode == "Dashboard & Métricas":
    st.markdown("### 📈 **Dashboard & Otimização de Tokens**")
    stats = get_mood_stats()
    token_m = st.session_state.agent.get_token_metrics()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Média de Humor", f"{stats['avg_score']}/10")
    c2.metric("Sessões Registradas", f"{stats['total_logs']}")
    c3.metric("Tokens Poupados", f"{token_m['tokens_saved']:,}")
    c4.metric("Economia Est. ($)", f"${token_m['estimated_cost_saved_usd']:.4f}")

    st.markdown("---")
    st.markdown("#### 📝 Registrar Humor Rápido")
    score_in = st.slider("Nota de Humor (1-10):", 1, 10, 7)
    tag_in = st.multiselect("Sentimentos:", ["Focado", "Confiante", "Tranquilo", "Ansioso", "Sobrecarregado", "Cansado"])
    trig_in = st.text_input("Gatilho ou contexto:")
    if st.button("Salvar no Diário", use_container_width=True):
        record_mood_entry(score_in, tag_in, trig_in, "")
        st.success("Salvo com sucesso!")
