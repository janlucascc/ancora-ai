import random
import re
from typing import List, Dict

THOUGHT_PHRASES = {
    "pt": [
        "Examinando separação radical entre fatos observados e leituras mentais...",
        "Mapeando distorções cognitivas e identificando viés de confirmação...",
        "Avaliando linha de base comportamental e trajetória da interação...",
        "Desarmando padrões de catastrofização e raciocínio emocional...",
        "Estruturando intervenção prática com base em defusão cognitiva (ACT)...",
        "Checando se há necessidade de regulação do sistema nervoso simpático...",
        "Identificando padrões de reforço intermitente e dependência emocional...",
        "Calculando métricas de assertividade sem agressão ou submissão...",
        "Separando intenção de implementação para os próximos passos...",
        "Desconstruindo efeito holofote e ilusão de transparência...",
        "Mapeando locus de controle interno vs. fatores externos incontroláveis...",
        "Analisando contingências de autovalor na situação descrita...",
        "Detectando se há ativação de triângulo dramático na dinâmica social...",
        "Avaliando investimento emocional desproporcional e carência percebida...",
        "Calibrando tom direto, honesto e focado em autonomia do adulto...",
        "Filtrando ruídos emocionais e isolando a variável comportamental real...",
        "Identificando se o pedido envolve manipulação para converter em autenticidade...",
        "Mapeando crença nuclear ativada pelo gatilho recente...",
        "Estruturando micro-passo comportamental de 2 minutos para ação imediata...",
        "Checando janela de tolerância emocional e prontidão para ação...",
        "Avaliando sinais de adaptação hedônica ou comparação social tóxica...",
        "Calculando resposta de alto valor focada em presença e segurança...",
        "Analisando linguagem corporal e subtexto da conversa relatada...",
        "Verificando se a ansiedade está gerando impulso de hiper-comunicação...",
        "Separando o que uma câmera filmaria do que o cérebro concluiu...",
        "Testando hipótese de autossabotagem e esquiva experiencial...",
        "Configurando reenquadramento cognitivo com evidências empíricas...",
        "Validando a emoção sentida sem validar a crença distorcida...",
        "Planejando comunicação não-violenta e limites interpessoais...",
        "Preparando reflexão estruturada sem jargões desnecessários...",
        "Mapeando se há padrão de resgate ou busca compulsiva por validação...",
        "Identificando o custo de oportunidade de continuar no mesmo ciclo...",
        "Sintetizando princípios de psicologia social aplicada à situação...",
        "Verificando segurança e ausência de risco antes da devolutiva...",
        "Finalizando estruturação da resposta com clareza e honestidade..."
    ],
    "en": [
        "Separating observable facts from cognitive mental readings...",
        "Mapping cognitive distortions and confirmation bias...",
        "Evaluating behavioral baseline and interaction trajectory...",
        "Defusing catastrophizing patterns and emotional reasoning...",
        "Structuring actionable intervention via Acceptance & Commitment (ACT)...",
        "Checking sympathetic nervous system activation and grounding need...",
        "Identifying intermittent reinforcement and attachment dynamics...",
        "Formulating assertive boundaries without passivity or aggression...",
        "Designing implementation intentions for immediate next steps...",
        "Deconstructing spotlight effect and illusion of transparency...",
        "Mapping internal locus of control vs. uncontrollable external noise...",
        "Analyzing self-worth contingencies in the reported situation...",
        "Evaluating drama triangle patterns in interpersonal dynamics...",
        "Detecting perceived neediness vs. authentic high-value presence...",
        "Calibrating direct, mature, and brotherly tone without fluff...",
        "Isolating the core behavioral variable from emotional turbulence...",
        "Translating social anxiety into grounded situational clarity...",
        "Mapping core beliefs triggered by the current stressor...",
        "Structuring a concrete 2-minute micro-action for immediate execution...",
        "Assessing window of emotional tolerance and action readiness...",
        "Evaluating toxic social comparison and hedonic baseline resets...",
        "Calculating clear, high-value communication for social dynamics...",
        "Analyzing subtext, conversational momentum, and underlying cues...",
        "Preventing anxious double-messaging and conversational over-investment...",
        "Distinguishing raw reality from internal catastrophizing scripts...",
        "Testing for experiential avoidance and self-sabotage loops...",
        "Constructing evidence-based cognitive reframing (CBT)...",
        "Validating emotional experience while challenging distorted premises...",
        "Formulating boundary-setting scripts with tactical poise...",
        "Preparing structured reflection with zero empty platitudes...",
        "Mapping savior complex and chronic validation-seeking habits...",
        "Calculating the opportunity cost of ruminative inaction...",
        "Synthesizing social psychology principles tailored to the context...",
        "Verifying safety protocols and emotional containment...",
        "Finalizing grounded response with precision and radical honesty..."
    ]
}

def get_dynamic_thinking_steps(user_text: str, lang: str = "pt") -> List[str]:
    """
    Selects 3-4 tailored, context-relevant thought states based on the user's input.
    """
    selected_lang = lang if lang in THOUGHT_PHRASES else "pt"
    pool = THOUGHT_PHRASES[selected_lang]
    lower = user_text.lower()

    thoughts = []
    # 1. First step: fact vs inference
    thoughts.append(pool[0] if selected_lang == "pt" else pool[0])

    # 2. Contextual middle steps
    if any(k in lower for k in ["ela", "garota", "flerte", "tinder", "mensagem", "date", "conversa", "her", "girl"]):
        if selected_lang == "pt":
            thoughts.append("Avaliando linha de base comportamental e trajetória da interação...")
            thoughts.append("Avaliando investimento emocional desproporcional e carência percebida...")
        else:
            thoughts.append("Evaluating behavioral baseline and interaction trajectory...")
            thoughts.append("Detecting perceived neediness vs. authentic high-value presence...")
    elif any(k in lower for k in ["trabalho", "chefe", "empresa", "reunião", "demissão", "work", "boss", "career"]):
        if selected_lang == "pt":
            thoughts.append("Mapeando locus de controle interno vs. fatores externos incontroláveis...")
            thoughts.append("Calculando métricas de assertividade sem agressão ou submissão...")
        else:
            thoughts.append("Mapping internal locus of control vs. uncontrollable external noise...")
            thoughts.append("Formulating assertive boundaries without passivity or aggression...")
    elif any(k in lower for k in ["ansiedade", "pânico", "medo", "coração", "respira", "anxiety", "panic", "breath"]):
        if selected_lang == "pt":
            thoughts.append("Checando se há necessidade de regulação do sistema nervoso simpático...")
            thoughts.append("Desarmando padrões de catastrofização e raciocínio emocional...")
        else:
            thoughts.append("Checking sympathetic nervous system activation and grounding need...")
            thoughts.append("Defusing catastrophizing patterns and emotional reasoning...")
    else:
        # Pick 2 randomized unique thoughts from the pool
        sampled = random.sample(pool[1:-2], 2)
        thoughts.extend(sampled)

    # 3. Final step — always from the correct language pool
    thoughts.append(pool[-1])
    return thoughts
