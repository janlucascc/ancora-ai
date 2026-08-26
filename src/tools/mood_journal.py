from typing import List, Dict, Any
from src.database.db import log_mood, get_recent_moods

def record_mood_entry(score: int, emotions: List[str], trigger: str, reflection: str) -> Dict[str, Any]:
    """Records a mood rating (1-10), emotion tags, context trigger, and personal reflection."""
    entry_id = log_mood(score=score, emotions=emotions, trigger=trigger, reflection=reflection)
    return {
        "status": "success",
        "entry_id": entry_id,
        "message": f"Humor registrado com nota {score}/10."
    }

def get_mood_history(limit: int = 7) -> List[Dict[str, Any]]:
    """Fetches the recent history of moods for analytics and reflection."""
    return get_recent_moods(limit=limit)
