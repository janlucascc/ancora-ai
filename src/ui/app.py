import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.agent.core import AncoraAgent
from src.tools.mood_journal import record_mood_entry, get_mood_history
from src.tools.stress_decompress import get_decompression_routine
from src.tools.social_wingman import generate_wingman_advice

st.set_page_config(
    page_title="Ancora AI | Your Everyday Life & Social Anchor",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .anchor-card {
        background-color: #1a1f2c;
        border-radius: 10px;
        padding: 16px;
        border-left: 4px solid #4a90e2;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

if "agent" not in st.session_state:
    st.session_state.agent = AncoraAgent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Eu sou o **Ancora AI** ⚓ — seu porto seguro diário, mentor de vida e parceiro para desafios no trabalho, vida social e relacionamentos. Como posso te apoiar hoje?"}
    ]

with st.sidebar:
    st.title("⚓ Ancora AI")
    st.caption("Everyday Life Anchor & Social Wingman | Built with Strands & AWS Bedrock")
    st.divider()

    st.subheader("⚡ Ações Rápidas")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🫁 Respirar 2m", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Preciso respirar e me acalmar."})
            resp = st.session_state.agent.respond("Preciso respirar e me acalmar.")
            st.session_state.messages.append({"role": "assistant", "content": resp})
            st.rerun()
    with col2:
        if st.button("🔥 Dica Wingman", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Quero dicas para puxar assunto e flertar."})
            resp = st.session_state.agent.respond("Quero dicas para puxar assunto e flertar.")
            st.session_state.messages.append({"role": "assistant", "content": resp})
            st.rerun()

    st.divider()
    st.subheader("📊 Registrar Humor do Dia")
    mood_val = st.slider("Como está sua energia agora?", 1, 10, 7)
    emotions_selected = st.multiselect("Sentimentos:", ["Tranquilo", "Ansioso", "Confiante", "Cansado", "Animado", "Sobrecarregado"])
    trigger_note = st.text_input("Gatilho ou contexto rápido:")
    if st.button("Salvar Registro", use_container_width=True):
        record_mood_entry(mood_val, emotions_selected, trigger_note, "")
        st.success("Humor registrado com sucesso!")

tab_chat, tab_wingman, tab_decompress, tab_history = st.tabs([
    "💬 Chat Âncora", "🔥 Wingman Social & Flerte", "🧘 Descompressão Rápida", "📈 Histórico & Evolução"
])

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="⚓" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("Desabafe, peça um conselho de trabalho ou uma dica de conversa..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        response = st.session_state.agent.respond(user_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant", avatar="⚓"):
            st.markdown(response)

with tab_wingman:
    st.header("🔥 Central do Wingman | Social & Conquista")
    st.write("Dicas práticas, quebra-gelos e dinâmica de conversa sem joguinhos tóxicos.")
    scenario = st.selectbox("Qual é a situação?", [
        ("dating_text", "📱 O que responder / Mandar mensagem no WhatsApp ou Instagram"),
        ("approach_icebreaker", "🤝 Como puxar papo pessoalmente (Festa, Bar, Academia, Café)"),
        ("flirting_banter", "🔥 Como flertar de forma leve e interessante"),
        ("handling_rejection", "🛡️ Como lidar com vácuo ou rejeição com maturidade")
    ], format_func=lambda x: x[1])

    detail = st.text_area("Descreva o contexto ou a mensagem que você recebeu:", placeholder="Ex: Ela postou uma foto viajando e quero puxar assunto sem parecer chato...")
    if st.button("Gerar Estratégia do Wingman", type="primary"):
        if detail:
            adv = generate_wingman_advice(scenario[0], detail)["advice"]
            st.subheader(adv["title"])
            st.write("### 📌 Princípios Fundamentais:")
            for p in adv["principles"]:
                st.write(f"- {p}")
            st.write("### 💡 Modelos e Ganchos Sugeridos:")
            for e in adv["example_templates"]:
                st.info(e)
        else:
            st.warning("Por favor, descreva o contexto.")

with tab_decompress:
    st.header("🧘 Central de Descompressão 2-Minutos")
    st.write("Exercícios práticos para reduzir o ritmo cardíaco e silenciar o excesso de pensamentos.")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🫁 Box Breathing (Respiração)", use_container_width=True):
            r = get_decompression_routine("box_breathing")
            st.subheader(r["name"])
            for s in r["steps"]:
                st.write(s)
    with col_b:
        if st.button("⚓ Grounding 5-4-3-2-1", use_container_width=True):
            r = get_decompression_routine("grounding_54321")
            st.subheader(r["name"])
            for s in r["steps"]:
                st.write(s)
    with col_c:
        if st.button("🧠 Reset de Perspectiva", use_container_width=True):
            r = get_decompression_routine("perspective_reset")
            st.subheader(r["name"])
            for s in r["steps"]:
                st.write(s)

with tab_history:
    st.header("📈 Seus Registros Recentes")
    history = get_mood_history(limit=10)
    if history:
        for item in history:
            tags = ", ".join(item["emotion_tags"]) if item["emotion_tags"] else "Sem tags"
            st.markdown(f"""
            <div class="anchor-card">
                <h4>Nota: {item['mood_score']}/10 — {item['timestamp']}</h4>
                <p><strong>Sentimentos:</strong> {tags}</p>
                <p><strong>Contexto:</strong> {item['context_trigger'] or 'Nenhum contexto adicionado'}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum registro de humor ainda. Use a barra lateral para salvar seu primeiro registro!")
