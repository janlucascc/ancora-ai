import streamlit as st
import os
import sys
import json
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.agent.core import AncoraAgent
from src.tools.mood_journal import record_mood_entry, get_mood_history
from src.tools.stress_decompress import get_decompression_routine
from src.tools.social_wingman import generate_wingman_advice
from src.tools.message_analyzer import analyze_message_and_rewrite
from src.tools.roleplay_arena import ROLEPLAY_SCENARIOS, get_scenario_details, generate_roleplay_turn
from src.database.db import get_mood_stats

st.set_page_config(
    page_title="Ancora AI | Everyday Life Anchor & Social Wingman",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling - Modern Dark Glassmorphic Theme with Glowing Accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #090d16 0%, #0d1527 50%, #090d16 100%);
    }
    
    .stChatMessage {
        border-radius: 14px;
        padding: 12px 18px;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .anchor-hero {
        background: linear-gradient(90deg, rgba(30, 58, 138, 0.4) 0%, rgba(14, 116, 144, 0.3) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }

    .metric-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-right: 8px;
    }
    .badge-success { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }
    .badge-warning { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.4); }
    .badge-info { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }

    /* Breathing Circle Animation */
    .breathing-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
    }
    .breathing-circle {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(56,189,248,0.8) 0%, rgba(14,116,144,0.4) 60%, rgba(15,23,42,0.1) 100%);
        box-shadow: 0 0 35px rgba(56, 189, 248, 0.6);
        animation: breath 16s infinite ease-in-out;
    }
    @keyframes breath {
        0%, 100% { transform: scale(0.7); opacity: 0.5; }
        25% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 50px rgba(56, 189, 248, 0.9); }
        50% { transform: scale(1.3); opacity: 0.9; }
        75% { transform: scale(0.7); opacity: 0.6; }
    }
</style>
""", unsafe_allow_html=True)

# Session States
if "agent" not in st.session_state:
    st.session_state.agent = AncoraAgent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Eu sou o **Ancora AI** ⚓ — seu porto seguro diário, mentor de vida e parceiro para desafios no trabalho, vida social e relacionamentos. Como posso te apoiar hoje?"}
    ]

if "roleplay_history" not in st.session_state:
    st.session_state.roleplay_history = []
if "active_scenario" not in st.session_state:
    st.session_state.active_scenario = "boss_negotiation"

# Sidebar Navigation & Ambient Audio
with st.sidebar:
    st.title("⚓ Ancora AI")
    st.caption("Autonomous Everyday Anchor & Social Wingman | Built with Strands & AWS Bedrock")
    st.divider()

    st.subheader("🎧 Som Ambiente Relaxante")
    sound_choice = st.selectbox("Escolha um ambiente para focar ou desestressar:", [
        ("rain", "🌧️ Chuva Suave"),
        ("waves", "🌊 Ondas do Oceano"),
        ("fire", "🔥 Lareira Aconchegante")
    ], format_func=lambda x: x[1])

    audio_urls = {
        "rain": "https://assets.mixkit.co/active_storage/sfx/1253/1253-preview.mp3",
        "waves": "https://assets.mixkit.co/active_storage/sfx/1189/1189-preview.mp3",
        "fire": "https://assets.mixkit.co/active_storage/sfx/1243/1243-preview.mp3"
    }
    st.audio(audio_urls[sound_choice[0]], format="audio/mp3")

    st.divider()
    st.subheader("⚡ Ações Rápidas de Grounding")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Suspiro 1m", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Preciso do Suspiro Fisiológico para acalmar agora."})
            resp = st.session_state.agent.respond("suspiro")
            st.session_state.messages.append({"role": "assistant", "content": resp})
            st.rerun()
    with col2:
        if st.button("🫁 Respiração 2m", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Quero fazer a Respiração Quadrada."})
            resp = st.session_state.agent.respond("respira")
            st.session_state.messages.append({"role": "assistant", "content": resp})
            st.rerun()

    st.divider()
    st.subheader("📊 Registrar Energia do Dia")
    mood_val = st.slider("Nota de 1 a 10:", 1, 10, 7)
    emotions_selected = st.multiselect("Sentimentos:", ["Tranquilo", "Ansioso", "Confiante", "Cansado", "Animado", "Sobrecarregado", "Focado"])
    trigger_note = st.text_input("Gatilho ou contexto rápido:")
    if st.button("💾 Salvar Registro", use_container_width=True):
        record_mood_entry(mood_val, emotions_selected, trigger_note, "")
        st.success("Registro de humor salvo!")

# Main Tabs Layout
tab_chat, tab_wingman, tab_roleplay, tab_decompress, tab_analytics = st.tabs([
    "💬 Chat Âncora", "📱 Message Lab & Wingman", "🎭 Arena de Simulação", "🫁 Descompressão Visual", "📈 Dashboard & Métricas"
])

# 1. TAB: Chat Principal
with tab_chat:
    st.markdown("""
    <div class="anchor-hero">
        <h3 style="margin:0; color:#38bdf8;">⚓ Santuário de Clareza Mental & Orientação Diária</h3>
        <p style="margin:5px 0 0 0; color:#94a3b8;">Desabafe sem julgamentos, tire dúvidas de carreira, relacionamento ou peça um reset mental.</p>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="⚓" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("Escreva o que está na sua cabeça agora..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        response = st.session_state.agent.respond(user_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant", avatar="⚓"):
            st.markdown(response)

# 2. TAB: Message Lab & Wingman
with tab_wingman:
    st.header("📱 Message Lab | Analisador de Mensagens & Flerte")
    st.write("Avalie mensagens antes de enviar ou descubra a resposta perfeita para conversas travadas.")

    col_w1, col_w2 = st.columns([1, 1])
    with col_w1:
        msg_input = st.text_area(
            "Cole a mensagem que você quer enviar (ou recebeu):",
            placeholder="Ex: Oi, tudo bem? Vi sua foto viajando... achei muito bonita, queria saber que lugar é esse haha se você puder me falar...",
            height=130
        )
        target = st.radio("Contexto da Mensagem:", ["Romântico / Flerte / Social", "Profissional / Trabalho & Limites"], horizontal=True)
        analyze_btn = st.button("🔥 Analisar Mensagem com IA", type="primary", use_container_width=True)

    with col_w2:
        if analyze_btn and msg_input:
            ctx_key = "romantic" if "Romântico" in target else "professional"
            res = analyze_message_and_rewrite(msg_input, ctx_key)
            
            st.markdown(f"""
            <div class="glass-card">
                <h4>📊 Diagnóstico da Mensagem</h4>
                <p><span class="metric-badge badge-info">Confiança: {res['confidence_score']}/100</span>
                <span class="metric-badge badge-warning">Carência: {res['neediness_level']}</span>
                <span class="metric-badge badge-success">Banter: {res['banter_level']}</span></p>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("💡 3 Sugestões de Alto Valor")
            for rw in res["rewrites"]:
                with st.expander(f"{rw['style']}", expanded=True):
                    st.code(rw["text"], language="text")
                    st.caption(f"**Por que funciona:** {rw['rationale']}")

# 3. TAB: Arena de Simulação (Roleplay)
with tab_roleplay:
    st.header("🎭 Arena de Simulação & Treinamento em Tempo Real")
    st.write("Pratique conversas difíceis da vida real em um ambiente 100% seguro com feedback imediato.")

    scenario_options = {k: v["title"] for k, v in ROLEPLAY_SCENARIOS.items()}
    chosen_scenario_key = st.selectbox("Escolha o cenário para simular:", list(scenario_options.keys()), format_func=lambda x: scenario_options[x])

    scenario_meta = get_scenario_details(chosen_scenario_key)

    if st.button("🔄 Reiniciar Simulação", use_container_width=False):
        st.session_state.roleplay_history = [{"role": "partner", "content": scenario_meta["initial_message"]}]
        st.session_state.active_scenario = chosen_scenario_key
        st.rerun()

    if not st.session_state.roleplay_history or st.session_state.active_scenario != chosen_scenario_key:
        st.session_state.roleplay_history = [{"role": "partner", "content": scenario_meta["initial_message"]}]
        st.session_state.active_scenario = chosen_scenario_key

    st.info(f"**Interlocutor:** {scenario_meta['partner_name']} ({scenario_meta['partner_role']})")

    for m in st.session_state.roleplay_history:
        if m["role"] == "partner":
            with st.chat_message("assistant", avatar="👤"):
                st.markdown(m["content"])
        elif m["role"] == "user":
            with st.chat_message("user"):
                st.markdown(m["content"])
        elif m["role"] == "coach":
            st.info(m["content"])

    user_reply = st.chat_input("Digite sua resposta na simulação...", key="roleplay_input")
    if user_reply:
        st.session_state.roleplay_history.append({"role": "user", "content": user_reply})
        turn_result = generate_roleplay_turn(chosen_scenario_key, st.session_state.roleplay_history, user_reply)
        
        st.session_state.roleplay_history.append({"role": "partner", "content": turn_result["reply"]})
        if turn_result.get("coach_tip"):
            st.session_state.roleplay_history.append({"role": "coach", "content": turn_result["coach_tip"]})
        
        if turn_result.get("scorecard"):
            sc = turn_result["scorecard"]
            st.balloons()
            st.success(f"🏆 **Simulação Concluída! Nota Geral: {sc['overall_score']}/100**\n\n- **Clareza:** {sc['clarity']}\n- **Confiança:** {sc['confidence']}\n- **Inteligência Emocional:** {sc['emotional_intelligence']}\n\n*Resumo:* {sc['summary']}")
        st.rerun()

# 4. TAB: Descompressão Visual
with tab_decompress:
    st.header("🫁 Central de Descompressão Visual & Somática")
    st.write("Exercícios somáticos para acalmar os batimentos cardíacos e silenciar a mente.")

    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.markdown("""
        <div class="glass-card breathing-container">
            <h4 style="color:#38bdf8; text-align:center;">Guia Visual de Respiração</h4>
            <p style="color:#94a3b8; font-size:0.85rem; text-align:center;">Acompanhe o ritmo: Inspire quando expandir, segure no topo, expire quando contrair.</p>
            <div class="breathing-circle"></div>
            <p style="margin-top:20px; font-weight:600; color:#38bdf8;">Inspire (4s) ➔ Segure (4s) ➔ Expire (4s) ➔ Segure (4s)</p>
        </div>
        """, unsafe_allow_html=True)

    with col_d2:
        st.subheader("⚡ Escolha a Técnica Guiada")
        t_choice = st.radio("Técnicas Rápidas:", [
            ("physiological_sigh", "⚡ Suspiro Fisiológico (Alívio em 1 min)"),
            ("box_breathing", "🫁 Respiração Quadrada (Navy SEALs)"),
            ("grounding_54321", "⚓ Ancoragem Tátil 5-4-3-2-1"),
            ("perspective_reset", "🧠 Reset de Perspectiva Pré-Reunião")
        ], format_func=lambda x: x[1])

        routine_data = get_decompression_routine(t_choice[0])
        st.markdown(f"""
        <div class="glass-card">
            <h4>{routine_data['name']}</h4>
            <p><span class="metric-badge badge-info">Duração: {routine_data['duration']}</span></p>
            <ol>
                {"".join(f"<li>{s}</li>" for s in routine_data['steps'])}
            </ol>
        </div>
        """, unsafe_allow_html=True)

# 5. TAB: Dashboard & Métricas + Token Optimizer
with tab_analytics:
    st.header("📈 Dashboard de Evolução, Métricas & Otimização de Tokens")
    stats = get_mood_stats()
    token_metrics = st.session_state.agent.get_token_metrics()

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("Média de Humor", f"{stats['avg_score']}/10", delta="Estável")
    mcol2.metric("Total de Registros", f"{stats['total_logs']}")
    mcol3.metric("Tokens Economizados", f"{token_metrics['tokens_saved']:,}", delta="Zero-Token Routing")
    mcol4.metric("Economia Estimada ($)", f"${token_metrics['estimated_cost_saved_usd']:.4f}")

    st.divider()

    st.subheader("⚡ Arquitetura de Economia de Tokens & Nuvem AWS")
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        st.markdown("""
        <div class="glass-card">
            <h4>🛡️ Roteamento Inteligente Zero-Tokens</h4>
            <p style="color:#94a3b8; font-size:0.9rem;">
                Guardrails de segurança, exercícios somáticos e diagnósticos determinísticos rodam <strong>100% localmente</strong> sem chamar a API de LLM. Isso poupa créditos AWS e reduz latência a quase zero.
            </p>
            <span class="metric-badge badge-success">Prompt Caching: Ativo (-90% custo input)</span>
            <span class="metric-badge badge-info">Janela Deslizante: 6 turnos (Sem overhead O(N²))</span>
        </div>
        """, unsafe_allow_html=True)
    with tcol2:
        st.markdown("""
        <div class="glass-card">
            <h4>📊 Resumo de Consumo de Tokens</h4>
            <p style="color:#94a3b8; font-size:0.9rem;">
                Acompanhamento em tempo real da sessão ativa do usuário:
            </p>
            <p><strong>Tokens LLM Consumidos:</strong> <code>{}</code> tokens</p>
            <p><strong>Tokens Poupados por Roteamento Local:</strong> <code>{}</code> tokens</p>
        </div>
        """.format(token_metrics['tokens_used'], token_metrics['tokens_saved']), unsafe_allow_html=True)

    st.divider()

    st.subheader("📊 Frequência de Sentimentos Registrados")
    if stats["emotion_counts"]:
        df_emotions = pd.DataFrame(list(stats["emotion_counts"].items()), columns=["Sentimento", "Contagem"]).set_index("Sentimento")
        st.bar_chart(df_emotions)
    else:
        st.info("Registre seus sentimentos na barra lateral para visualizar os gráficos interativos.")

    st.subheader("🗓️ Histórico Recente de Registros")
    recent_history = get_mood_history(limit=8)
    if recent_history:
        for r in recent_history:
            tags = ", ".join(r["emotion_tags"]) if r["emotion_tags"] else "Nenhum"
            st.markdown(f"""
            <div class="glass-card">
                <strong>Nota: {r['mood_score']}/10</strong> — <small>{r['timestamp']}</small><br/>
                <span class="metric-badge badge-info">{tags}</span><br/>
                <small><strong>Contexto:</strong> {r['context_trigger'] or 'Sem notas adicionais'}</small>
            </div>
            """, unsafe_allow_html=True)
