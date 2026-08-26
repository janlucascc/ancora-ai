import os
import json
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.agent.prompts import ANCORA_SYSTEM_PROMPT
from src.agent.guardrails import check_crisis_risk
from src.tools.social_wingman import generate_wingman_advice
from src.tools.stress_decompress import get_decompression_routine
from src.tools.confidence_anchor import reframe_negative_thought
from src.tools.mood_journal import record_mood_entry, get_mood_history

# Check if boto3 and Bedrock are configured
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

class AncoraAgent:
    """
    Ancora AI Core Agent.
    Orchestrates LLM (Bedrock / Anthropic / Local fallback), Guardrails, and Custom Strands Tools.
    """
    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.system_prompt = ANCORA_SYSTEM_PROMPT
        self.history: List[Dict[str, str]] = []
        self.bedrock_client = None
        
        if HAS_BOTO3 and os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            try:
                self.bedrock_client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                )
            except Exception as e:
                print(f"Warning: Could not initialize Bedrock client: {e}")

    def respond(self, user_message: str) -> str:
        """Processes user message through guardrails, tool dispatching, and agent reasoning."""
        # 1. Immediate Safety Crisis Guardrail
        crisis = check_crisis_risk(user_message)
        if crisis:
            return crisis["message"]

        msg_lower = user_message.lower()

        # 2. Contextual Routing to Specialized Tools
        if any(w in msg_lower for w in ["respira", "ansiedade", "pânico", "panico", "estresse", "desacelerar", "calma", "grounding"]):
            routine = get_decompression_routine("box_breathing" if "respira" in msg_lower else "grounding_54321")
            steps_formatted = "\n".join(routine["steps"])
            return f"Respira fundo, estou aqui contigo. Vamos fazer um reset rápido agora:\n\n### {routine['name']}\n**Tempo sugerido:** {routine['duration']}\n\n{steps_formatted}\n\nQuando terminar essas repetições, me conta como seu corpo está se sentindo."

        if any(w in msg_lower for w in ["garota", "mulher", "flerte", "flertar", "conversa", "tinder", "whatsapp", "conquistar", "chegar nela", "mandar mensagem", "ficante"]):
            scenario_key = "dating_text" if any(k in msg_lower for k in ["mensagem", "whatsapp", "direct", "insta", "instagram", "texto"]) else "approach_icebreaker"
            advice = generate_wingman_advice(scenario_key, user_message)
            adv = advice["advice"]
            princs = "\n".join(f"- {p}" for p in adv["principles"])
            exs = "\n".join(f"- {e}" for e in adv["example_templates"])
            return f"⚓ **Visão do Wingman | Ancora AI**\n\n**Princípios-chave:**\n{princs}\n\n**Exemplos Práticos & Ganchos:**\n{exs}\n\nO segredo é manter a naturalidade e não colocar ninguém num pedestal. O que acha de adaptar com as suas próprias palavras?"

        if any(w in msg_lower for w in ["síndrome do impostor", "impostor", "inseguro", "insegurança", "não sou bom", "medo de falhar", "vergonha", "rejeição", "vacuo", "vácuo"]):
            ref = reframe_negative_thought(user_message, "Autossabotagem / Insegurança")
            pills = "\n".join(ref["pillars"])
            return f"⚓ **Ancoragem de Autoconfiança:**\n\nEssa voz de autossabotagem é comum, mas ela não representa a realidade dos fatos.\n\n{pills}\n\nQual é o primeiro pequeno passo que você pode dar hoje sem buscar a perfeição imediata?"

        # 3. AWS Bedrock Runtime invocation if available
        if self.bedrock_client:
            try:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "system": self.system_prompt,
                    "messages": [
                        {"role": "user", "content": user_message}
                    ]
                })
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=body
                )
                response_body = json.loads(response.get("body").read())
                return response_body["content"][0]["text"]
            except Exception as e:
                print(f"Bedrock invocation fallback: {e}")

        # 4. Empathetic Conversational Response Fallback
        return (
            "Te ouço com total atenção. Momentos assim exigem que a gente pare, respire e olhe a situação com clareza.\n\n"
            "Em relação ao que você compartilhou: o primeiro passo é não se cobrar tanto. "
            "Podemos traçar um plano de ação prático ou fazer um exercício de foco se preferir. "
            "Como posso te ajudar a clarear a mente agora?"
        )
