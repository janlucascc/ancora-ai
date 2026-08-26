import os
import json
import re
import requests
from typing import Dict, Any, List, Optional, Tuple

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
    Ancora AI Core Engine.
    Delivers deep, live, intelligent, non-scripted responses powered by:
    - Google Gemini Live Engine (gemini-3.6-flash / gemini-3.7-flash)
    - AWS Bedrock (Claude 3.5 Sonnet / AWS Nova)
    - Real-time Observable Thought Process (Separating Facts vs Inferences & Biases)
    - Anti-manipulation and Crisis Guardrails
    """

    def __init__(self, model_id: Optional[str] = None, api_key: Optional[str] = None):
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.full_system_prompt = ANCORA_IDENTITY_SHIELD + "\n\n" + ANCORA_SYSTEM_PROMPT
        self.history: List[Dict[str, str]] = []
        self.optimizer = TokenOptimizer(max_history_turns=6, max_output_tokens=1000)
        self.gemini_key = api_key or os.getenv("GEMINI_API_KEY")

        # 1. AWS Bedrock Client
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

    def respond(self, user_message: str) -> Dict[str, Any]:
        """
        Processes message and returns:
        {
            "thought": "Reflexão interna do agente (Fatos, Vieses, Estratégia)",
            "content": "Resposta principal do Ancora AI",
            "source": "gemini_live | bedrock | procedural_engine | guardrail"
        }
        """
        clean_msg = str(user_message or "").strip()
        if not clean_msg:
            return {
                "thought": "Mensagem vazia recebida. Nenhuma ação requerida.",
                "content": "Estou aqui. Quando quiser desabafar, planejar uma conversa difícil ou acalmar a mente, é só escrever.",
                "source": "guardrail"
            }

        # ─── 1. SAFETY CRISIS GUARDRAIL ──────────────────────────────────────
        crisis = check_crisis_risk(clean_msg)
        if crisis:
            self.optimizer.record_local_routing_saving(clean_msg)
            return {
                "thought": "⚠️ SINAL DE CRISE DETECTADO: Ideação de autoflagelo / sofrimento agudo. Acionando protocolo de emergência imediata.",
                "content": crisis["message"],
                "source": "guardrail"
            }

        # ─── 2. MANIPULATION / JAILBREAK GUARDRAIL ───────────────────────────
        manipulation = check_manipulation_attempt(clean_msg)
        if manipulation:
            self.optimizer.record_local_routing_saving(clean_msg)
            return {
                "thought": "🛡️ TENTATIVA DE QUEBRA DE IDENTIDADE: Usuário tentando redefinir persona/filtros. Aplicando protocolo firme e calmo.",
                "content": manipulation["message"],
                "source": "guardrail"
            }

        # ─── 3. LIVE GEMINI ENGINE (Ultra-Fast & Deep Live Completions) ───────
        if self.gemini_key:
            gemini_res = self._invoke_gemini_live(clean_msg)
            if gemini_res:
                self._append_to_history(clean_msg, gemini_res["content"])
                return gemini_res

        # ─── 4. AWS BEDROCK (If configured) ──────────────────────────────────
        if self.bedrock_client:
            try:
                payload, est_tokens = self.optimizer.prepare_bedrock_payload(
                    system_prompt=self.full_system_prompt,
                    history=self.history,
                    current_message=clean_msg,
                    enable_prompt_caching=True
                )
                body = json.dumps(payload)
                response = self.bedrock_client.invoke_model(modelId=self.model_id, body=body)
                response_body = json.loads(response.get("body").read())
                llm_output = response_body["content"][0]["text"]

                self._append_to_history(clean_msg, llm_output)
                return {
                    "thought": "Raciocínio processado ao vivo via Amazon Bedrock (Claude 3.5 Sonnet). Metodologia TCC/ACT aplicada.",
                    "content": llm_output,
                    "source": "bedrock"
                }
            except Exception as e:
                print(f"Bedrock fallback triggered: {e}")

        # ─── 5. DYNAMIC PROCEDURAL PSYCHOLOGY ENGINE (Offline Fallback) ──────
        thought, content = self._generate_procedural_response(clean_msg)
        self.optimizer.record_local_routing_saving(clean_msg)
        self._append_to_history(clean_msg, content)

        return {
            "thought": thought,
            "content": content,
            "source": "procedural_engine"
        }

    def _invoke_gemini_live(self, user_text: str) -> Optional[Dict[str, Any]]:
        """Invokes Gemini Live API with verified model fallbacks and conversational history."""
        models = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-flash-latest"]
        
        # Build conversational contents
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

        for m in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.gemini_key}"
            try:
                res = requests.post(url, json=payload, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_resp = candidates[0]["content"]["parts"][0]["text"]
                        
                        # Generate brief observable thought
                        thought_summary = f"Análise ao vivo via {m}. Separando fatos observáveis de inferências e aplicando defusão cognitiva (ACT)."
                        return {
                            "thought": thought_summary,
                            "content": text_resp,
                            "source": "gemini_live"
                        }
            except Exception as e:
                print(f"Gemini {m} error: {e}")
        return None

    def _generate_procedural_response(self, text: str) -> Tuple[str, str]:
        """Offline dynamic psychological analysis engine."""
        lower = text.lower()
        words = [w for w in re.findall(r"\w+", lower) if len(w) > 3]
        
        is_dating = any(k in lower for k in ["ela", "garota", "menina", "mulher", "tinder", "insta", "whatsapp", "conversa", "vácuo", "vacuo", "sumiu", "flerte", "ficante", "date"])
        is_work = any(k in lower for k in ["chefe", "trabalho", "empresa", "reunião", "demissão", "aumento", "cobrança", "meta", "carreira", "projeto", "colega"])
        is_anxiety = any(k in lower for k in ["ansiedade", "pânico", "panico", "medo", "coração", "respira", "nervoso", "desespero", "travado"])
        is_self_doubt = any(k in lower for k in ["impostor", "inseguro", "não consigo", "fracasso", "burro", "incapaz", "vergonha", "feio", "rejeição"])

        thought = f"Modo Offline: Mapeando relato ({len(words)} termos). Separando fatos de leituras mentais e definindo micro-passo comportamental."

        if is_dating:
            content = (
                "Vamos dissecar essa situação com frieza para não agir com base na ansiedade:\n\n"
                "**1. O que é FATO vs. O que é LEITURA:**\n"
                f"- **Fato concreto:** Houve uma interação recente ('{text[:80]}...').\n"
                "- **Leitura mental:** A conclusão de que isso significa desinteresse ou rejeição.\n"
                "*(Lembre-se: comportamento isolado não é linha de base. Trajetória no tempo pesa mais que um gesto único).*\n\n"
                "**2. Mecanismo em jogo:**\n"
                "O cérebro busca ativamente evidências de rejeição (*Viés de Confirmação*). A melhor resposta agora é não hiper-investir nem cobrar.\n\n"
                "Qual é o próximo passo concreto que você deseja dar?"
            )
        elif is_work:
            content = (
                "No ambiente profissional, separar o dado objetivo do sentimento é o que evita o desgaste desnecessário:\n\n"
                "**1. Separando os Dados:**\n"
                f"- **Fato:** Uma demanda ou cobrança aconteceu.\n"
                "- **Leitura:** 'Vou falhar' ou 'não sou capaz'.\n\n"
                "**2. Foco de Controle:**\n"
                "Foque exclusivamente na sua próxima entrega de 30 minutos e na clareza da sua resposta por escrito.\n\n"
                "O que dessa situação está 100% no seu controle agora?"
            )
        elif is_anxiety:
            routine = get_decompression_routine("physiological_sigh")
            content = (
                "Seu sistema nervoso está em alerta. Vamos desacelerar a fisiologia primeiro:\n\n"
                f"### {routine['name']}\n"
                + "\n".join(routine["steps"]) + "\n\n"
                "Faça 3 repetições agora e me diga quando o ritmo cardíaco estabilizar."
            )
        else:
            content = (
                "Te ouço com total atenção.\n\n"
                "Para trabalharmos isso com eficácia:\n"
                "1. **O que aconteceu exatamente** (os fatos sem interpretação)?\n"
                "2. **Qual foi a leitura** que sua cabeça fez a partir disso?\n\n"
                "Me conta para traçarmos o próximo passo."
            )

        return thought, content

    def _append_to_history(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": str(user_msg)})
        self.history.append({"role": "assistant", "content": str(assistant_msg)})
        self.history = self.optimizer.optimize_history(self.history)

    def get_token_metrics(self) -> Dict[str, Any]:
        return self.optimizer.get_stats()
