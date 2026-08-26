from typing import Dict, Any
from src.database.db import log_decompression

def get_decompression_routine(technique: str) -> Dict[str, Any]:
    """
    Provides guided, science-backed 2-minute decompression routines for workplace stress and overstimulation.
    Techniques: 'box_breathing', 'grounding_54321', 'perspective_reset', 'physical_shakeout'.
    """
    routines = {
        "box_breathing": {
            "name": "🫁 Respiração Quadrada (Box Breathing)",
            "duration": "2 minutos",
            "steps": [
                "1. Inspire pelo nariz contando mentalmente até 4.",
                "2. Segure o ar nos pulmões por 4 segundos.",
                "3. Expire suavemente pela boca contando até 4.",
                "4. Mantenha os pulmões vazios por 4 segundos.",
                "Repita o ciclo 4 a 6 vezes para desacelerar o sistema nervoso autônomo."
            ]
        },
        "grounding_54321": {
            "name": "⚓ Ancoragem Tátil 5-4-3-2-1",
            "duration": "2 minutos",
            "steps": [
                "👁️ 5 coisas que você pode VER ao seu redor agora.",
                "✋ 4 coisas que você pode TOCAR (sua roupa, a mesa, a cadeira).",
                "👂 3 sons que você pode OUVIR no ambiente.",
                "👃 2 aromas que você pode SENTIR.",
                "👅 1 sabor presente na sua boca agora."
            ]
        },
        "perspective_reset": {
            "name": "🧠 Reset de Perspectiva Pré-Reunião / Pós-Estresse",
            "duration": "1 minuto",
            "steps": [
                "1. Pergunta de choque: 'Isso terá alguma relevância daqui a 1 ano? E daqui a 5 anos?'",
                "2. Separação de controle: 'O que está 100% no meu controle agora? O que é ruído externo?'",
                "3. Foco na próxima ação simples: Execute apenas o próximo passo de 5 minutos."
            ]
        }
    }

    routine = routines.get(technique, routines["box_breathing"])
    log_decompression(technique=routine["name"], duration=120, notes=f"Triggered technique: {technique}")
    return routine
