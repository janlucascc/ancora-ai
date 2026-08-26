from typing import Dict, Any
from src.database.db import log_coaching

def reframe_negative_thought(negative_thought: str, situation: str) -> Dict[str, Any]:
    """
    Cognitive reframing tool to combat imposter syndrome, social overthinking, and self-doubt.
    """
    reframing_guide = {
        "analysis": f"Identificando distorções cognitivas em: '{negative_thought}'",
        "pillars": [
            "1. Descatastrofização: Qual é o cenário mais provável e realista?",
            "2. Evidências Reais: O que prova que esse pensamento negativo é 100% verdade?",
            "3. Nova Afirmação Âncora: 'Eu sou capaz de lidar com os desafios passo a passo.'"
        ]
    }
    log_coaching(category="confidence_reframing", query=f"{situation} -> {negative_thought}", advice="Applied cognitive reframing")
    return reframing_guide
