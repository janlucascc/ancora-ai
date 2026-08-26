import os
import json
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.agent.prompts import ANCORA_SYSTEM_PROMPT, ANCORA_IDENTITY_SHIELD
from src.agent.guardrails import check_crisis_risk, check_manipulation_attempt
from src.agent.token_optimizer import TokenOptimizer
from src.tools.social_wingman import generate_wingman_advice
from src.tools.message_analyzer import analyze_message_and_rewrite
from src.tools.roleplay_arena import generate_roleplay_turn
from src.tools.stress_decompress import get_decompression_routine
from src.tools.confidence_anchor import reframe_negative_thought
from src.tools.mood_journal import record_mood_entry, get_mood_history

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


class AncoraAgent:
    """
    Ancora AI Core Agent — Hardened Identity, Behavioral Psychology Framework & Token Optimizer.
    Orchestrates LLM (Bedrock / Local fallback), Guardrails, Token Savings and Custom Tools.
    """

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.full_system_prompt = ANCORA_IDENTITY_SHIELD + "\n\n" + ANCORA_SYSTEM_PROMPT
        self.history: List[Dict[str, str]] = []
        self.bedrock_client = None
        self.optimizer = TokenOptimizer(max_history_turns=6, max_output_tokens=800)

        if HAS_BOTO3 and os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            try:
                self.bedrock_client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                )
            except Exception as e:
                print(f"Warning: Bedrock client unavailable: {e}")

    def respond(self, user_message: str) -> str:
        """
        Processes a user message through the full Ancora AI pipeline with token optimization:
        1. Crisis Guardrail (0 tokens - local early exit)
        2. Manipulation / Jailbreak Detection (0 tokens - local early exit)
        3. Contextual Tool Routing (0 tokens - local early exit)
        4. AWS Bedrock LLM with Prompt Caching & Sliding Window
        5. Principled Local Fallback
        """

        # ─── 1. SAFETY CRISIS — ZERO-TOKEN LOCAL EXIT ────────────────────────
        crisis = check_crisis_risk(user_message)
        if crisis:
            self.optimizer.record_local_routing_saving(user_message)
            self._append_to_history(user_message, crisis["message"])
            return crisis["message"]

        # ─── 2. MANIPULATION / JAILBREAK — ZERO-TOKEN LOCAL EXIT ─────────────
        manipulation = check_manipulation_attempt(user_message)
        if manipulation:
            self.optimizer.record_local_routing_saving(user_message)
            self._append_to_history(user_message, manipulation["message"])
            return manipulation["message"]

        msg_lower = user_message.lower()

        # ─── 3. CONTEXTUAL TOOL ROUTING (Zero-Token Local Execution) ─────────

        # 3a. Somatic Grounding — Physiological Sigh (Huberman)
        if any(w in msg_lower for w in ["suspiro", "huberman", "nervovago", "nervo vago"]):
            routine = get_decompression_routine("physiological_sigh")
            steps = "\n".join(routine["steps"])
            response = (
                f"Vamos usar o método mais rápido que a neurociência tem pra isso.\n\n"
                f"### {routine['name']}\n"
                f"**Tempo:** {routine['duration']}\n\n"
                f"{steps}\n\n"
                f"Faça esses ciclos agora. Quando o ritmo respiratório normalizar, me conta como você está."
            )
            self.optimizer.record_local_routing_saving(user_message)
            self._append_to_history(user_message, response)
            return response

        # 3b. Somatic Grounding — Box Breathing / 5-4-3-2-1
        if any(w in msg_lower for w in ["respira", "respiração", "ansiedade", "pânico", "panico",
                                         "grounding", "acalmar", "calma", "coração acelerado"]):
            technique = "box_breathing" if any(k in msg_lower for k in ["respira", "respiração", "box"]) else "grounding_54321"
            routine = get_decompression_routine(technique)
            steps = "\n".join(routine["steps"])
            response = (
                f"Antes de qualquer análise — vamos regular o sistema nervoso primeiro.\n\n"
                f"### {routine['name']}\n"
                f"**Tempo sugerido:** {routine['duration']}\n\n"
                f"{steps}\n\n"
                f"Quando terminar, me conta o que está acontecendo. Com o sistema mais calmo, "
                f"a conversa vai ser mais produtiva."
            )
            self.optimizer.record_local_routing_saving(user_message)
            self._append_to_history(user_message, response)
            return response

        # 3c. Social Wingman — Dating & Conversation
        if any(w in msg_lower for w in ["garota", "menina", "flerte", "flertar", "tinder", "match",
                                         "direct", "dm", "instagram", "conquistar", "conversa com ela",
                                         "chegar nela", "puxar assunto", "como falar com"]):
            is_text = any(k in msg_lower for k in ["mensagem", "whatsapp", "texto", "resposta", "reply"])
            advice = generate_wingman_advice("dating_text" if is_text else "approach_icebreaker", user_message)
            adv = advice["advice"]
            principles = "\n".join(f"- {p}" for p in adv["principles"])
            examples = "\n".join(f"- {e}" for e in adv["example_templates"])
            response = (
                f"Vamos separar o que é fato do que é ansiedade aqui primeiro — porque a maioria "
                f"das dificuldades sociais começa com a leitura, não com a situação em si.\n\n"
                f"**Princípios do método (com mecanismo):**\n{principles}\n\n"
                f"**Modelos de entrada práticos:**\n{examples}\n\n"
                f"O que importa não é o script perfeito — é você fazendo sentido dentro do seu contexto. "
                f"O que está mais trancando agora: a abordagem inicial ou saber o que continuar falando?"
            )
            self.optimizer.record_local_routing_saving(user_message)
            self._append_to_history(user_message, response)
            return response

        # 3d. Message Lab — Wingman Analysis
        if any(w in msg_lower for w in ["analisar essa mensagem", "analisa essa mensagem",
                                         "o que acha dessa mensagem", "avaliar mensagem", "review essa msg"]):
            result = analyze_message_and_rewrite(user_message, "romantic")
            rewrites = "\n".join(
                f"**{r['style']}**\n> {r['text']}\n*{r['rationale']}*"
                for r in result["rewrites"]
            )
            response = (
                f"Diagnóstico da mensagem:\n\n"
                f"- **Confiança:** {result['confidence_score']}/100\n"
                f"- **Pressão/Carência:** {result['neediness_level']}\n"
                f"- **Banter/Engajamento:** {result['banter_level']}\n\n"
                f"---\n\n**3 versões com base no que funciona melhor:**\n\n{rewrites}\n\n"
                f"Adapta com as suas palavras — a autenticidade é o que vai fazer diferença, não o template."
            )
            self.optimizer.record_local_routing_saving(user_message)
            self._append_to_history(user_message, response)
            return response

        # 3e. Confidence & Cognitive Reframing
        if any(w in msg_lower for w in ["impostor", "inseguro", "insegurança", "me sinto burro",
                                         "não sirvo", "não sou bom", "fracasso", "falhar",
                                         "vergonha", "me julgam", "todo mundo percebeu"]):
            ref = reframe_negative_thought(user_message, "Autossabotagem / Insegurança")
            pillars = "\n".join(ref["pillars"])
            response = (
                f"O que você descreveu tem nome — é um padrão cognitivo bem documentado, não uma avaliação "
                f"realista da sua capacidade.\n\n{pillars}\n\n"
                f"A pergunta mais útil agora não é 'como me sentir melhor' — é "
                f"'qual é o próximo comportamento concreto que posso executar, independente do ânimo?'"
            )
            self.optimizer.record_local_routing_saving(user_message)
            self._append_to_history(user_message, response)
            return response

        # ─── 4. AWS BEDROCK — Optimized LLM Invocation with Caching ──────────
        if self.bedrock_client:
            try:
                payload, est_tokens = self.optimizer.prepare_bedrock_payload(
                    system_prompt=self.full_system_prompt,
                    history=self.history,
                    current_message=user_message,
                    enable_prompt_caching=True
                )
                
                body = json.dumps(payload)
                response = self.bedrock_client.invoke_model(modelId=self.model_id, body=body)
                response_body = json.loads(response.get("body").read())
                llm_output = response_body["content"][0]["text"]

                # Track actual tokens from Bedrock response if available
                usage = response_body.get("usage", {})
                in_tokens = usage.get("input_tokens", est_tokens)
                out_tokens = usage.get("output_tokens", self.optimizer.estimate_tokens(llm_output))
                self.optimizer.record_llm_usage(in_tokens, out_tokens)

                self._append_to_history(user_message, llm_output)
                return llm_output
            except Exception as e:
                print(f"Bedrock fallback triggered: {e}")

        # ─── 5. PRINCIPLED LOCAL FALLBACK ────────────────────────────────────
        fallback = (
            "Escuta — antes de qualquer análise, deixa eu entender melhor o que você trouxe.\n\n"
            "O que mais está pesando nisso que você descreveu: a situação em si, "
            "ou o que você está concluindo a partir dela? "
            "Essa separação costuma mudar bastante o que faz sentido fazer a seguir."
        )
        self.optimizer.record_local_routing_saving(user_message)
        self._append_to_history(user_message, fallback)
        return fallback

    def _append_to_history(self, user_msg: str, assistant_msg: str):
        """Appends turn and trims to maximum sliding window."""
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        self.history = self.optimizer.optimize_history(self.history)

    def get_token_metrics(self) -> Dict[str, Any]:
        """Exposes token optimization metrics for UI & analytics."""
        return self.optimizer.get_stats()
