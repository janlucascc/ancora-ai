from typing import Dict, Any
from src.database.db import log_decompression

DECOMPRESSION_ROUTINES: Dict[str, Dict[str, Any]] = {
    "physiological_sigh": {
        "name": "⚡ Suspiro Fisiológico (Dr. Andrew Huberman)",
        "duration": "1 minuto (O método neurocientífico mais rápido de relaxamento)",
        "steps": [
            "1. Faça uma inspiração profunda pelo nariz.",
            "2. Sem soltar o ar, dê uma segunda inspiração curta no topo para inflar ao máximo os alvéolos pulmonares.",
            "3. Solte todo o ar pela boca lentamente com um suspiro suave e longo.",
            "Repita de 2 a 3 vezes. Isso desinfla o estresse e ativa o nervo vago instantaneamente."
        ]
    },
    "box_breathing": {
        "name": "🫁 Respiração Quadrada (Box Breathing - Navy SEALs)",
        "duration": "2 minutos",
        "steps": [
            "1. Inspire pelo nariz contando mentalmente até 4.",
            "2. Segure o ar nos pulmões por 4 segundos.",
            "3. Expire suavemente pela boca contando até 4.",
            "4. Mantenha os pulmões vazios por 4 segundos.",
            "Repita o ciclo 4 a 6 vezes para desacelerar o ritmo cardíaco."
        ]
    },
    "grounding_54321": {
        "name": "⚓ Ancoragem Tátil 5-4-3-2-1",
        "duration": "2 minutos",
        "steps": [
            "👁️ 5 coisas que você pode VER ao seu redor agora.",
            "✋ 4 coisas que você pode TOCAR (sua roupa, a mesa, o celular).",
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

def get_decompression_routine(technique: str) -> Dict[str, Any]:
    """
    Returns the decompression routine data AND logs the session to the database.
    Call this only when the user actively initiates a session (not on every render).
    """
    routine = DECOMPRESSION_ROUTINES.get(technique, DECOMPRESSION_ROUTINES["physiological_sigh"])
    try:
        log_decompression(technique=routine["name"], duration=120, notes=f"Triggered technique: {technique}")
    except Exception as e:
        print(f"Non-critical decompression logging warning: {e}")
    return routine

