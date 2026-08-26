from typing import Dict, Any
from src.database.db import log_coaching

def generate_wingman_advice(scenario_type: str, context_details: str) -> Dict[str, Any]:
    """
    Provides actionable dating and social wingman advice, conversation icebreakers, or text suggestions.
    Scenarios: 'dating_text', 'approach_icebreaker', 'flirting_banter', 'handling_rejection', 'social_party'.
    """
    scenarios_map = {
        "dating_text": {
            "title": "📱 Sugestão de Mensagem & Dinâmica de Conversa",
            "principles": [
                "Evite perguntas burocráticas ('Tudo bem? Como foi seu dia?'). Seja observador e divertido.",
                "Faça comentários sobre detalhes do perfil, fotos ou algo que ela mencionou.",
                "Mantenha a proporção de investimento emocional equilibrada (não mande 5 parágrafos para uma resposta de 3 palavras)."
            ],
            "example_templates": [
                "Pergunta com gancho: 'Reparei que você gosta de [detalhe]. Isso é bom gosto ou só coincidência?'",
                "Humor leve: 'Preciso de uma opinião sincera: [dilema engraçado/cotidiano]. O que você escolheria?'"
            ]
        },
        "approach_icebreaker": {
            "title": "🤝 Quebrando o Gelo & Ansiedade de Aproximação",
            "principles": [
                "Regra dos 3 Segundos: Quando tiver vontade de falar, vá em até 3 segundos antes do cérebro sabotar.",
                "Linguagem corporal aberta: Ombros relaxados, olhar firme e sorriso leve.",
                "Abertura contextual é sempre melhor que cantadas prontas."
            ],
            "example_templates": [
                "'Oi, reparei na sua vibe e precisei vir te dar um oi antes de ir embora.'",
                "'Licença, uma dúvida rápida: você recomenda o drink/café que você pediu?'"
            ]
        },
        "flirting_banter": {
            "title": "🔥 Flerte & Conexão Autêntica",
            "principles": [
                "Equilíbrio entre elogio sincero e provocação leve (teasing amigável).",
                "Demonstre interesse sem colocar a pessoa em um pedestal inalcançável.",
                "Escute ativamente: use o que ela acabou de falar para puxar a próxima história."
            ],
            "example_templates": [
                "'Você tem cara de quem é perigosa em discussões de cinema... acertei?'",
                "'Ok, você acabou de ganhar pontos comigo por causa disso.'"
            ]
        },
        "handling_rejection": {
            "title": "🛡️ Lidando com Rejeição & Autovalor",
            "principles": [
                "Rejeição é apenas desalinhamento de momento ou preferência, nunca define o seu valor pessoal.",
                "Aja com elegância e maturidade: 'Sem problemas, valeu pelo papo! Tenha uma boa noite!'",
                "O verdadeiro jogo é a abundância e o auto-respeito."
            ],
            "example_templates": [
                "Mentalidade: 'Eu me arrisquei e tive coragem. O resultado é secundário, a postura é primária.'"
            ]
        }
    }

    advice_data = scenarios_map.get(scenario_type, scenarios_map["dating_text"])
    summary = f"{advice_data['title']} for context: {context_details}"
    log_coaching(category=f"wingman_{scenario_type}", query=context_details, advice=summary)

    return {
        "scenario": scenario_type,
        "context": context_details,
        "advice": advice_data
    }
