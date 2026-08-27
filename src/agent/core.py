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

LANGUAGE_PROFILES = {
    "pt": {
        "name": "Português (Brasil)",
        "instruction": "Você DEVE responder e formular todas as suas reflexões e orientações rigorosamente em PORTUGUÊS (Brasil)."
    },
    "en": {
        "name": "English (US)",
        "instruction": "You MUST communicate, analyze, and formulate your entire response strictly in ENGLISH (US)."
    },
    "es": {
        "name": "Español",
        "instruction": "DEBES comunicarte, analizar y formular toda tu respuesta estrictamente en ESPAÑOL."
    },
    "fr": {
        "name": "Français",
        "instruction": "Vous DEVEZ communiquer, analyser et formuler l'intégralité de votre réponse strictement en FRANÇAIS."
    },
    "zh": {
        "name": "中文 (Chinese)",
        "instruction": "你必须完全使用中文（简体）进行所有的心理分析、对话与指导。"
    },
    "hi": {
        "name": "हिन्दी (Hindi)",
        "instruction": "आपको अपने सभी उत्तर और मनोवैज्ञानिक मार्गदर्शन पूरी तरह से हिन्दी (Hindi) में ही देने होंगे।"
    },
    "ar": {
        "name": "العربية (Arabic)",
        "instruction": "يجب عليك صياغة جميع الردود والتحليلات النفسية والتوجيهات السلوكية باللغة العربية الفصحى حصريًا."
    },
    "bn": {
        "name": "বাংলা (Bengali)",
        "instruction": "আপনাকে অবশ্যই সমস্ত আচরণগত বিশ্লেষণ এবং পরামর্শ সম্পূর্ণ বাংলায় প্রদান করতে হবে।"
    }
}


class AncoraAgent:
    """
    Ancora AI Core Engine — Enhanced Multi-Model Behavioral Copilot.
    Features:
    - Model selection (Gemini 3.6/3.7, Claude 3.5 Sonnet, Offline)
    - Multilingual & Auto-locale integration across 8 major languages
    - 5-second deliberate pause on extreme crisis risk
    - Out-of-scope redirection back to emotional & social domain
    - Real-time Observable Thought Process
    """

    def __init__(self, model_id: Optional[str] = None, api_key: Optional[str] = None, lang: str = "pt"):
        self.model_id = model_id or os.getenv("ACTIVE_MODEL_ID", "gemini-3.7-flash")
        self.lang = lang
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

    def _get_system_prompt_for_lang(self, lang: str = "pt") -> str:
        """Injects explicit language enforcement into the core identity shield."""
        lang_info = LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES["pt"])
        lang_directive = f"""
════════════════════════════════════════════════════════
CRITICAL LANGUAGE DIRECTIVE / REGRA OBRIGATÓRIA DE IDIOMA:
Target Language: {lang_info['name']} ({lang})
{lang_info['instruction']}
Never reply in any other language unless the user explicitly commands a switch.
════════════════════════════════════════════════════════
"""
        return ANCORA_IDENTITY_SHIELD + "\n\n" + lang_directive + "\n\n" + ANCORA_SYSTEM_PROMPT

    def respond(self, user_message: str, model_override: Optional[str] = None, lang_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a user message and returns structured reasoning + answer in the target language.
        """
        clean_msg = str(user_message or "").strip()
        lang = lang_override or self.lang
        active_model = model_override or self.model_id
        system_prompt = self._get_system_prompt_for_lang(lang)

        if not clean_msg:
            empty_messages = {
                "pt": "Estou aqui. Quando quiser desabafar, planejar uma conversa difícil ou acalmar a mente, é só escrever.",
                "en": "I'm here. Whenever you'd like to vent, plan a tough conversation, or reset your focus, feel free to write.",
                "es": "Estoy aquí. Cuando quieras desahogarte o planificar una conversación difícil, escribe con tranquilidad.",
                "fr": "Je suis là. Dès que vous souhaitez vous exprimer ou préparer une conversation difficile, écrivez simplement.",
                "zh": "我在这里。随时可以向我倾诉、梳理难题或平复思绪。",
                "hi": "मैं यहीं हूँ। जब भी आप बात करना चाहें या मन शांत करना चाहें, यहाँ लिखें।",
                "ar": "أنا هنا. عندما تود التعبير عما في داخلك أو التخطيط لموقف صعب، تفضل بالكتابة.",
                "bn": "আমি এখানে আছি। আপনি যখনই কথা বলতে চান বা মানসিক চাপ কমাতে চান, নির্দ্বিধায় লিখুন।"
            }
            return {
                "thought": "Mensagem vazia recebida.",
                "content": empty_messages.get(lang, empty_messages["pt"]),
                "source": "guardrail"
            }

        # ─── 1. SAFETY CRISIS GUARDRAIL (With 5-second deliberate pause) ──────
        crisis = check_crisis_risk(clean_msg, lang=lang)
        if crisis:
            self.optimizer.record_local_routing_saving(clean_msg)
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
                "thought": "📌 ASSUNTO FORA DO ESCOPO: Redirecionando para o foco de bem-estar, carreira e relações.",
                "content": out_of_scope["message"],
                "source": "guardrail_scope"
            }

        # ─── 4. MODEL SELECTION EXECUTION ────────────────────────────────────

        # A) Gemini Live (Flash 3.7 / Pro 3.1 / Flash 3.6)
        if "gemini" in active_model.lower() and self.gemini_key:
            gemini_res = self._invoke_gemini_live(clean_msg, model_name=active_model, lang=lang)
            if gemini_res:
                self._append_to_history(clean_msg, gemini_res["content"])
                return gemini_res

        # B) AWS Bedrock (Claude 3.5 Sonnet)
        if ("claude" in active_model.lower() or "bedrock" in active_model.lower()) and self.bedrock_client:
            try:
                payload, est_tokens = self.optimizer.prepare_bedrock_payload(
                    system_prompt=system_prompt,
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
                    "thought": f"Raciocínio processado via Amazon Bedrock (Claude 3.5 Sonnet) no idioma '{lang}'.",
                    "content": llm_output,
                    "source": "bedrock"
                }
            except Exception as e:
                print(f"Bedrock invocation error: {e}")

        # C) Default Gemini Fallback if key is available and model isn't offline
        # NOTE: _invoke_gemini_live already cascades through all Gemini models,
        # so section A above covers all gemini cases. This section handles the case
        # where active_model was claude/bedrock but bedrock is unavailable.
        if active_model not in ("offline",) and "gemini" not in active_model.lower() and self.gemini_key:
            gemini_res = self._invoke_gemini_live(clean_msg, model_name="gemini-3.7-flash", lang=lang)
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

    def generate_chat_title(self, user_message: str) -> str:
        """Procedural 3-4 word title generation for new chats."""
        clean = user_message.strip().lower()
        if not clean:
            return "Nova Conversa"
        words = [w for w in clean.replace("?", "").replace("!", "").replace(",", "").split() if len(w) > 3]
        if not words:
            return clean[:20].capitalize()
        title = " ".join(words[:3]).capitalize()
        return f"{title}..."

    def _invoke_gemini_live(self, user_text: str, model_name: str = "gemini-3.7-flash", lang: str = "pt") -> Optional[Dict[str, Any]]:
        """Invokes Gemini Live API with enforced language instruction and history context."""
        target_model = model_name if "gemini" in model_name else "gemini-3.7-flash"
        models_to_try = [target_model, "gemini-3.7-flash", "gemini-3.1-pro", "gemini-3.6-flash", "gemini-flash-latest"]
        system_prompt = self._get_system_prompt_for_lang(lang)
        
        contents = []
        for h in self.history[-6:]:
            role = "user" if h["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h["content"]}]})
        contents.append({"role": "user", "parts": [{"text": user_text}]})

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
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
                            "thought": f"Análise comportamental via {m} no idioma [{LANGUAGE_PROFILES.get(lang, {}).get('name', lang)}]. Fatos separados de interpretações com TCC/ACT.",
                            "content": text_resp,
                            "source": "gemini_live"
                        }
            except Exception as e:
                print(f"Gemini {m} error: {e}")
        return None

    def _generate_procedural_response(self, text: str, lang: str = "pt") -> Tuple[str, str]:
        """Offline dynamic psychological analysis engine supporting all 8 languages."""
        snippet = text[:80] + "..." if len(text) > 80 else text
        
        responses = {
            "pt": (
                "Modo Offline: Mapeando cognição. Separando fatos de leituras mentais (TCC/ACT).",
                f"Vamos dissecar essa situação com clareza para não agir com base na ansiedade:\n\n"
                f"**1. O que é FATO vs. O que é LEITURA:**\n"
                f"- **Fato concreto:** Você relatou: '{snippet}'\n"
                f"- **Leitura mental:** A conclusão de desastre, rejeição ou insuficiência.\n\n"
                f"**2. Mecanismo em jogo:**\n"
                f"Sob estresse, nosso cérebro confunde o sentimento com prova da realidade (*Raciocínio Emocional*).\n\n"
                f"O que dessa situação está 100% no seu controle fazer agora?"
            ),
            "en": (
                "Offline Mode: Cognitive mapping active. Separating facts from assumptions (CBT/ACT).",
                f"Let's break down this situation clearly to avoid reacting from pure anxiety:\n\n"
                f"**1. FACT vs. INTERPRETATION:**\n"
                f"- **Observable Fact:** You shared: '{snippet}'\n"
                f"- **Mental Projection:** The assumption of catastrophe, rejection, or inadequacy.\n\n"
                f"**2. Psychological Mechanism:**\n"
                f"Under stress, the mind treats emotions as evidence (*Emotional Reasoning*).\n\n"
                f"What part of this situation is 100% within your direct control right now?"
            ),
            "es": (
                "Modo Offline: Mapeo cognitivo activo. Separando hechos de interpretaciones (TCC/ACT).",
                f"Analicemos esta situación con total claridad para no actuar desde la ansiedad:\n\n"
                f"**1. HECHO vs. INTERPRETACIÓN:**\n"
                f"- **Hecho observable:** Has compartido: '{snippet}'\n"
                f"- **Lectura mental:** La conclusión de rechazo, catástrofe o insuficiencia.\n\n"
                f"**2. Mecanismo psicológico:**\n"
                f"Bajo estrés, el cerebro confunde las emociones con hechos (*Razonamiento Emocional*).\n\n"
                f"¿Qué parte de esta situación está 100% bajo tu control en este momento?"
            ),
            "fr": (
                "Mode Hors-Ligne: Cartographie cognitive active. Séparation des faits et des interprétations (TCC/ACT).",
                f"Analysons cette situation avec lucidité pour éviter de réagir sous le coup de l'anxiété:\n\n"
                f"**1. FAITS vs. INTERPRÉTATION:**\n"
                f"- **Fait observable:** Vous avez exprimé: '{snippet}'\n"
                f"- **Projection mentale:** L'hypothèse de catastrophe ou de rejet.\n\n"
                f"**2. Mécanisme en jeu:**\n"
                f"Sous stress, notre esprit prend ses émotions pour des preuves réelles (*Raisonnement Émotionnel*).\n\n"
                f"Que pouvez-vous contrôler à 100% dès maintenant?"
            ),
            "zh": (
                "离线模式：正在进行认知重构，区分事实与主观臆断（CBT/ACT）。",
                f"让我们清晰客观地梳理当前情况，避免受焦虑驱使：\n\n"
                f"**1. 客观事实 vs. 主观解读：**\n"
                f"- **事实记录：** 您提到：'{snippet}'\n"
                f"- **思维投射：** 对灾难化后果、排斥或不足的假设。\n\n"
                f"**2. 心理机制：**\n"
                f"在压力下，大脑常将感受误当成事实（*情绪化推理*）。\n\n"
                f"面对此情况，此时此刻完全在您掌控范围内的一件具体行动是什么？"
            ),
            "hi": (
                "ऑफ़लाइन मोड: संज्ञानात्मक मानचित्रण सक्रिय। तथ्यों और व्याख्याओं को अलग करना।",
                f"आइए इस स्थिति को स्पष्ट रूप से समझें ताकि चिंता के आधार पर निर्णय न लें:\n\n"
                f"**1. तथ्य बनाम व्याख्या:**\n"
                f"- **प्रत्यक्ष तथ्य:** आपने बताया: '{snippet}'\n"
                f"- **मानसिक अनुमान:** असफलता या अस्वीकृति का डर।\n\n"
                f"**2. मनोवैज्ञानिक तंत्र:**\n"
                f"तनाव में मन भावनाओं को ही वास्तविकता मान लेता है (*इमोशनल रीजनिंग*)।\n\n"
                f"इस स्थिति में अभी आपके सीधे नियंत्रण में क्या है?"
            ),
            "ar": (
                "الوضع المحلي: جاري الفصل بين الحقائق والاستنتاجات الذهنية (CBT/ACT).",
                f"دعنا نحلل هذا الموقف بوضوح تام لتجنب التصرف بدافع القلق:\n\n"
                f"**1. الحقيقة مقابل التفسير:**\n"
                f"- **الواقع الملاحظ:** ذكرت: '{snippet}'\n"
                f"- **القراءة الذهنية:** افتراض الرفض أو الكارثة.\n\n"
                f"**2. الآلية النفسية:**\n"
                f"تحت وطأة الضغط، يعتبر العقل المشاعر دليلاً قاطعًا (*التفكير العاطفي*).\n\n"
                f"ما الذي يقع بالكامل تحت سيطرتك المباشرة الآن؟"
            ),
            "bn": (
                "অফলাইন মোড: জ্ঞানীয় পুনর্বিন্যাস সক্রিয়। বাস্তব তথ্য ও অনুমানের পার্থক্য (CBT/ACT)।",
                f"উদ্বেগের বশবর্তী না হয়ে পরিস্থিতিটি স্বচ্ছভাবে বিচার করা যাক:\n\n"
                f"**১. বাস্তব তথ্য বনাম অনুমান:**\n"
                f"- **পর্যবেক্ষণযোগ্য তথ্য:** আপনি জানিয়েছেন: '{snippet}'\n"
                f"- **মানসিক ব্যাখ্যা:** প্রত্যাখ্যান বা বিপর্যয়ের ভয়।\n\n"
                f"**২. মনস্তাত্ত্বিক কারণ:**\n"
                f"মানসিক চাপে মস্তিষ্ক অনুভূতিকেই সত্য বলে ধরে নেয় (*আবেগীয় যুক্তি*)।\n\n"
                f"এই পরিস্থিতিতে এখন আপনার সম্পূর্ণ নিয়ন্ত্রণে কী রয়েছে?"
            )
        }

        return responses.get(lang, responses["pt"])

    def _append_to_history(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": str(user_msg)})
        self.history.append({"role": "assistant", "content": str(assistant_msg)})
        self.history = self.optimizer.optimize_history(self.history)

    def get_token_metrics(self) -> Dict[str, Any]:
        return self.optimizer.get_stats()
