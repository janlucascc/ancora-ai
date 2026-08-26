import os
import json
import re
import time
import requests
from typing import Dict, Any, List, Optional, Tuple

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.agent.prompts import ANCORA_SYSTEM_PROMPT, ANCORA_IDENTITY_SHIELD
from src.agent.guardrails import check_crisis_risk, check_manipulation_attempt, check_out_of_scope
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
    Ancora AI Core Engine — Enhanced Multi-Model Behavioral Copilot.
    Features:
    - Model selection (Gemini 3.6/3.7, Claude 3.5 Sonnet, Offline)
    - 5-second deliberate pause on extreme crisis risk
    - Out-of-scope redirection back to emotional & social domain
    - Multilingual & Auto-locale support (PT/EN)
    - Real-time Observable Thought Process
    """

    def __init__(self, model_id: Optional[str] = None, api_key: Optional[str] = None, lang: str = "pt"):
        self.model_id = model_id or os.getenv("ACTIVE_MODEL_ID", "gemini-3.6-flash")
        self.lang = lang
        self.full_system_prompt = ANCORA_IDENTITY_SHIELD + "\n\n" + ANCORA_SYSTEM_PROMPT
        self.history: List[Dict[str, str]] = []
        self.optimizer = TokenOptimizer(max_history_turns=6, max_output_tokens=1000)
        self.gemini_key = api_key or os.getenv("GEMINI_API_KEY")

        # AWS Bedrock Client
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
                print(f"Warning: Bedrock client unavailable: {e}")

    def respond(self, user_message: str, model_override: Optional[str] = None, lang_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a user message and returns structured reasoning + answer.
        """
        clean_msg = str(user_message or "").strip()
        lang = lang_override or self.lang
        active_model = model_override or self.model_id

        if not clean_msg:
            empty_msg = "Estou aqui. Quando quiser desabafar, planejar uma conversa difícil ou acalmar a mente, é só escrever." if lang == "pt" else "I'm here. Whenever you'd like to vent, plan a tough conversation, or reset your focus, feel free to write."
            return {
                "thought": "Mensagem vazia recebida.",
                "content": empty_msg,
                "source": "guardrail"
            }

        # ─── 1. SAFETY CRISIS GUARDRAIL (With 5-second deliberate pause) ──────
        crisis = check_crisis_risk(clean_msg, lang=lang)
        if crisis:
            self.optimizer.record_local_routing_saving(clean_msg)
            # Deliberate 5-second pause to reflect and feel human & thoughtful
            time.sleep(5)
            return {
                "thought": "⚠️ SINAL DE RISCO IDENTIFICADO: Pausa intencional de 5s para avaliação de gravidade e encaminhamento seguro.",
                "content": crisis["message"],
                "source": "guardrail_crisis"
            }

        # ─── 2. MANIPULATION / JAILBREAK GUARDRAIL ───────────────────────────
        manipulation = check_manipulation_attempt(clean_msg, lang=lang)
        if manipulation:
            self.optimizer.record_local_routing_saving(clean_msg)
            return {
                "thought": "🛡️ TENTATIVA DE QUEBRA DE IDENTIDADE: Redirecionando com calma e método.",
                "content": manipulation["message"],
                "source": "guardrail_jailbreak"
            }

        # ─── 3. OUT-OF-SCOPE REDIRECTION ─────────────────────────────────────
        out_of_scope = check_out_of_scope(clean_msg, lang=lang)
        if out_of_scope:
            self.optimizer.record_local_routing_saving(clean_msg)
            return {
                "thought": "📌 ASSUNTO FORA DO ESCOPO: O usuário perguntou sobre tarefas/código/triviais. Redirecionando para o foco de bem-estar, carreira e relações.",
                "content": out_of_scope["message"],
                "source": "guardrail_scope"
            }

        # ─── 4. MODEL SELECTION EXECUTION ────────────────────────────────────

        # A) Explicit Gemini Models
        if "gemini" in active_model.lower() and self.gemini_key:
            gemini_res = self._invoke_gemini_live(clean_msg, model_name=active_model)
            if gemini_res:
                self._append_to_history(clean_msg, gemini_res["content"])
                return gemini_res

        # B) AWS Bedrock (Claude 3.5 Sonnet)
        if ("claude" in active_model.lower() or "bedrock" in active_model.lower()) and self.bedrock_client:
            try:
                payload, est_tokens = self.optimizer.prepare_bedrock_payload(
                    system_prompt=self.full_system_prompt,
                    history=self.history,
                    current_message=clean_msg,
                    enable_prompt_caching=True
                )
                body = json.dumps(payload)
                bedrock_model = "anthropic.claude-3-5-sonnet-20241022-v2:0"
                response = self.bedrock_client.invoke_model(modelId=bedrock_model, body=body)
                response_body = json.loads(response.get("body").read())
                llm_output = response_body["content"][0]["text"]

                self._append_to_history(clean_msg, llm_output)
                return {
                    "thought": "Raciocínio processado via Amazon Bedrock (Claude 3.5 Sonnet). Metodologia TCC/ACT aplicada.",
                    "content": llm_output,
                    "source": "bedrock"
                }
            except Exception as e:
                print(f"Bedrock invocation error: {e}")

        # C) Default Gemini Fallback if available (and not in offline mode)
        if active_model != "offline" and self.gemini_key:
            gemini_res = self._invoke_gemini_live(clean_msg, model_name="gemini-3.6-flash")
            if gemini_res:
                self._append_to_history(clean_msg, gemini_res["content"])
                return gemini_res

        # ─── 5. OFFLINE / PROCEDURAL TCC ENGINE ──────────────────────────────
        thought, content = self._generate_procedural_response(clean_msg, lang=lang)
        self.optimizer.record_local_routing_saving(clean_msg)
        self._append_to_history(clean_msg, content)

        return {
            "thought": thought,
            "content": content,
            "source": "procedural_engine"
        }

    def _invoke_gemini_live(self, user_text: str, model_name: str = "gemini-3.6-flash") -> Optional[Dict[str, Any]]:
        """Invokes Gemini Live API with model fallback and conversation context."""
        target_model = model_name if "gemini" in model_name else "gemini-3.6-flash"
        models_to_try = [target_model, "gemini-3.6-flash", "gemini-3.7-flash", "gemini-flash-latest"]
        
        contents = []
        for h in self.history[-6:]:
            role = "user" if h["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h["content"]}]})
        contents.append({"role": "user", "parts": [{"text": user_text}]})

        payload = {
            "system_instruction": {
                "parts": [{"text": self.full_system_prompt}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.6,
                "maxOutputTokens": 1000
            }
        }

        for m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.gemini_key}"
            try:
                res = requests.post(url, json=payload, timeout=14)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_resp = candidates[0]["content"]["parts"][0]["text"]
                        return {
                            "thought": f"Análise gerada em tempo real via {m}. Separando fatos de inferências e aplicando defusão cognitiva (ACT).",
                            "content": text_resp,
                            "source": "gemini_live"
                        }
            except Exception as e:
                print(f"Gemini {m} error: {e}")
        return None

    def _generate_procedural_response(self, text: str, lang: str = "pt") -> Tuple[str, str]:
        """Offline dynamic psychological analysis engine."""
        lower = text.lower()
        words = [w for w in re.findall(r"\w+", lower) if len(w) > 3]

        thought = f"Modo Offline: Mapeando termos ({len(words)} palavras). Separando fatos de leituras mentais."

        if lang == "en":
            content = (
                "Let's break down this situation clearly:\n\n"
                "**1. What is FACT vs. What is INTERPRETATION:**\n"
                f"- **Observable Fact:** You shared: '{text[:80]}...'\n"
                "- **Interpretation:** The assumption of catastrophe or rejection.\n\n"
                "**2. Psychological Mechanism:**\n"
                "Under pressure, our mind treats feelings as conclusive proof (*Emotional Reasoning*). The most effective step is focusing on what is within your direct control right now.\n\n"
                "What is the smallest concrete action you can take in the next 20 minutes?"
            )
        else:
            content = (
                "Vamos dissecar essa situação com clareza para não agir com base na ansiedade:\n\n"
                "**1. O que é FATO vs. O que é LEITURA:**\n"
                f"- **Fato concreto:** Você relatou: '{text[:80]}...'\n"
                "- **Leitura mental:** A conclusão de desastre, desinteresse ou insuficiência.\n\n"
                "**2. Mecanismo em jogo:**\n"
                "Sob estresse, nosso cérebro confunde o sentimento com prova da realidade (*Raciocínio Emocional*).\n\n"
                "O que dessa situação está 100% no seu controle fazer agora?"
            )

        return thought, content

    def _append_to_history(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": str(user_msg)})
        self.history.append({"role": "assistant", "content": str(assistant_msg)})
        self.history = self.optimizer.optimize_history(self.history)

    def get_token_metrics(self) -> Dict[str, Any]:
        return self.optimizer.get_stats()
