import os
import json
import re
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

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


class AncoraAgent:
    """
    Ancora AI Core Engine.
    Delivers deep, non-scripted, methodology-driven responses with:
    - Multi-provider LLM support (AWS Bedrock, Google Gemini, OpenAI, or Smart Procedural Engine)
    - Observable 'Thought Process' (separating Facts vs Interpretation, Biases & Strategy)
    - Anti-manipulation and Crisis Guardrails
    """

    def __init__(self, model_id: Optional[str] = None, api_key: Optional[str] = None):
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.full_system_prompt = ANCORA_IDENTITY_SHIELD + "\n\n" + ANCORA_SYSTEM_PROMPT
        self.history: List[Dict[str, str]] = []
        self.optimizer = TokenOptimizer(max_history_turns=6, max_output_tokens=1000)

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

        # 2. Gemini API Client (Alternative fast provider)
        self.gemini_model = None
        gemini_key = api_key or os.getenv("GEMINI_API_KEY")
        if HAS_GEMINI and gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=self.full_system_prompt
                )
            except Exception as e:
                print(f"Warning: Gemini config: {e}")

    def respond(self, user_message: str) -> Dict[str, Any]:
        """
        Returns a structured dictionary:
        {
            "thought": "Reflexão interna do agente (Fatos, Vieses, Estratégia)",
            "content": "Resposta principal do Ancora AI",
            "source": "bedrock | gemini | procedural_engine | guardrail"
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
                "thought": "🛡️ TENTATIVA DE QUEBRA DE IDENTIDADE DETECTADA: Usuário tentando redefinir persona/filtros. Aplicando protocolo de redirecionamento firme e calmo.",
                "content": manipulation["message"],
                "source": "guardrail"
            }

        # ─── 3. AWS BEDROCK (If configured) ──────────────────────────────────
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
                    "thought": "Raciocínio processado via Amazon Bedrock (Claude 3.5 Sonnet). Metodologia TCC/ACT aplicada ao contexto.",
                    "content": llm_output,
                    "source": "bedrock"
                }
            except Exception as e:
                print(f"Bedrock invocation fallback: {e}")

        # ─── 4. GEMINI API (If configured) ───────────────────────────────────
        if self.gemini_model:
            try:
                chat = self.gemini_model.start_chat(history=[])
                resp = chat.send_message(clean_msg)
                llm_output = resp.text
                self._append_to_history(clean_msg, llm_output)
                return {
                    "thought": "Análise processada via Gemini LLM Engine com foco em separação de fatos e psicologia social.",
                    "content": llm_output,
                    "source": "gemini"
                }
            except Exception as e:
                print(f"Gemini error: {e}")

        # ─── 5. DYNAMIC PROCEDURAL PSYCHOLOGY ENGINE ─────────────────────────
        # When offline or without API keys, generates deeply contextual, dynamic responses
        # adhering strictly to the TCC / ACT methodology (Fact vs Interpretation, Biases).
        thought, content = self._generate_procedural_response(clean_msg)
        self.optimizer.record_local_routing_saving(clean_msg)
        self._append_to_history(clean_msg, content)

        return {
            "thought": thought,
            "content": content,
            "source": "procedural_engine"
        }

    def _generate_procedural_response(self, text: str) -> Tuple[str, str]:
        """
        Dynamic psychological analysis engine that dissects the user's exact words,
        detects cognitive biases, separates facts from inferences, and provides actionable guidance.
        """
        lower = text.lower()
        words = [w for w in re.findall(r"\w+", lower) if len(w) > 3]
        
        # Analyze themes
        is_dating = any(k in lower for k in ["ela", "garota", "menina", "mulher", "tinder", "insta", "whatsapp", "conversa", "vácuo", "vacuo", "sumiu", "flerte", "ficante", "date"])
        is_work = any(k in lower for k in ["chefe", "trabalho", "empresa", "reunião", "demissão", "aumento", "cobrança", "meta", "carreira", "projeto", "colega"])
        is_anxiety = any(k in lower for k in ["ansiedade", "pânico", "panico", "medo", "coração", "respira", "nervoso", "desespero", "travado"])
        is_self_doubt = any(k in lower for k in ["impostor", "inseguro", "não consigo", "fracasso", "burro", "incapaz", "vergonha", "feio", "rejeição"])

        # Detect specific cognitive distortions
        detected_biases = []
        if any(k in lower for k in ["sempre", "nunca", "tudo", "nada", "todo mundo", "ninguém"]):
            detected_biases.append("Generalização Excessiva (transformar um evento em regra universal)")
        if any(k in lower for k in ["certeza que", "ela pensa", "ele acha", "eles acham", "vai achar que"]):
            detected_biases.append("Leitura Mental (assumir a intenção alheia sem evidência empírica)")
        if any(k in lower for k in ["vai dar errado", "arruinado", "fim do mundo", "desastre", "não tem jeito"]):
            detected_biases.append("Catastrofização (antecipar o pior desfecho como se fosse inevitável)")
        if any(k in lower for k in ["sinto que", "tenho a sensação", "parece que sou"]):
            detected_biases.append("Raciocínio Emocional (tratar o sentimento atual como prova da realidade)")

        bias_str = "; ".join(detected_biases) if detected_biases else "Análise de foco atencional e linha de base"

        thought = (
            f"1. Fatos Extraídos: Relato de situação contendo {len(words)} termos-chave relevantes.\n"
            f"2. Vieses Mapeados: {bias_str}.\n"
            f"3. Estratégia de Resposta: Separar fato vs leitura, nomear mecanismo psicológico e entregar ação em micro-passo."
        )

        if is_dating:
            content = (
                "Vamos dissecar essa situação com frieza para não agir com base na ansiedade:\n\n"
                "**1. O que é FATO vs. O que é LEITURA:**\n"
                f"- **Fato concreto:** Houve uma interação recente ('{text[:80]}...').\n"
                "- **Leitura mental:** A conclusão de que isso significa desinteresse, rejeição ou desastre.\n"
                "*(Lembre-se: comportamento isolado não é linha de base. O que importa é a trajetória ao longo do tempo).*\n\n"
                "**2. Mecanismo em jogo:**\n"
                "Quando nos importamos, nosso cérebro ativa o *Viés de Confirmação* — qualquer atraso ou palavra vira 'prova' de que algo deu errado. Isso aumenta a carência percebida e a vontade de hiper-investir.\n\n"
                "**3. Postura Recomendada:**\n"
                "- **Não envie mensagens em duplicidade.** Deixe o espaço da conversa respirar.\n"
                "- Mantenha a proporcionalidade: se a resposta foi curta, sua próxima interação deve ser leve e focada em uma ação real, não em cobrança de atenção.\n\n"
                "Qual é o próximo passo prático que você quer dar agora?"
            )
        elif is_work:
            content = (
                "No ambiente profissional, quando a pressão sobe, misturar fato com julgamento é o que mais drena energia. Vamos estruturar isso:\n\n"
                "**1. Separando os Dados da Emoção:**\n"
                f"- **Fato:** Uma demanda, cobrança ou conflito ocorreu no seu ambiente de trabalho.\n"
                "- **Leitura:** 'Não sou bom o suficiente' ou 'estou prestes a falhar' (Raciocínio Emocional).\n\n"
                "**2. Princípio da Atribuição & Foco de Controle:**\n"
                "Você não controla o humor do seu gestor, prazos impostos de fora ou o comportamento dos colegas. Você controla 100% da sua **organização dos próximos 30 minutos** e da **clareza da sua comunicação escrita**.\n\n"
                "**3. Ação Concreta para Agora:**\n"
                "1. Liste em tópicos apenas os dados objetivos do que precisa ser entregue.\n"
                "2. Se for necessária uma conversa difícil, alinhe: *'Para garantir a qualidade dentro do prazo X, sugiro priorizarmos Y. Podemos seguir assim?'*\n\n"
                "O que dessa situação está exatamente sob o seu controle neste momento?"
            )
        elif is_anxiety:
            routine = get_decompression_routine("physiological_sigh")
            content = (
                "Antes de qualquer análise intelectual — seu sistema nervoso simpático está ativado e precisa de regulação somática imediata.\n\n"
                f"### {routine['name']}\n"
                f"**Mecanismo:** {routine['duration']}\n\n"
                + "\n".join(routine["steps"]) + "\n\n"
                "Execute 3 ciclos completos agora. Quando o ritmo cardíaco baixar, podemos olhar para os pensamentos com mais clareza."
            )
        elif is_self_doubt:
            content = (
                "Essa sensação de insuficiência é um processo cognitivo previsível, não um diagnóstico da sua competência:\n\n"
                "**1. Defusão Cognitiva (ACT):**\n"
                "Você não *é* o seu pensamento de incapacidade. O pensamento é apenas um evento verbal transitório produzido pelo cérebro quando você se importa com o resultado.\n\n"
                "**2. O Efeito Holofote (Spotlight Effect):**\n"
                "Temos a ilusão de que todas as pessoas estão hiper-focadas nos nossos deslizes. Na realidade, cada um está ocupado demais lidando com as próprias inseguranças.\n\n"
                "**3. Princípio da Ativação Comportamental:**\n"
                "A confiança **não vem antes** da ação — ela é consequência da repetição de comportamentos mesmo na presença de desconforto.\n\n"
                "Qual é a menor ação possível de 2 minutos que você pode executar agora?"
            )
        else:
            content = (
                f"Entendido o que você trouxe.\n\n"
                "Para trabalharmos isso com eficácia, me responda de forma direta:\n"
                "1. **O que aconteceu exatamente** (a cena que uma câmera filmaria)?\n"
                "2. **Qual é a conclusão** que a sua cabeça tirou disso?\n\n"
                "Separando essas duas coisas, encontramos o caminho prático."
            )

        return thought, content

    def _append_to_history(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": str(user_msg)})
        self.history.append({"role": "assistant", "content": str(assistant_msg)})
        self.history = self.optimizer.optimize_history(self.history)

    def get_token_metrics(self) -> Dict[str, Any]:
        return self.optimizer.get_stats()
