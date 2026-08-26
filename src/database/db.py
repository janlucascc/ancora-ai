import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "data", "ancora.db"))

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection ensuring parent directory exists."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    return sqlite3.connect(db_path)

def init_db(db_path: str = DB_PATH):
    """Initializes SQLite database with all schema tables safely."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mood_score INTEGER NOT NULL,
            emotion_tags TEXT,
            context_trigger TEXT,
            reflection TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS coaching_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            category TEXT NOT NULL,
            user_query TEXT NOT NULL,
            advice_summary TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS decompression_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            technique TEXT NOT NULL,
            duration_seconds INTEGER DEFAULT 120,
            notes TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            original_message TEXT NOT NULL,
            confidence_score INTEGER NOT NULL,
            neediness_level TEXT NOT NULL,
            banter_level TEXT NOT NULL,
            rewrites_json TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roleplay_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            scenario_key TEXT NOT NULL,
            turns_count INTEGER NOT NULL,
            scorecard_json TEXT NOT NULL
        )
        """)

def log_mood(score: int, emotions: List[str], trigger: str, reflection: str, db_path: str = DB_PATH) -> int:
    """Safely logs a mood entry with score clamped to 1-10."""
    init_db(db_path)
    clamped_score = max(1, min(10, int(score)))
    safe_emotions = emotions if isinstance(emotions, list) else []
    safe_trigger = str(trigger or "").strip()
    safe_reflection = str(reflection or "").strip()

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mood_logs (mood_score, emotion_tags, context_trigger, reflection) VALUES (?, ?, ?, ?)",
            (clamped_score, json.dumps(safe_emotions), safe_trigger, safe_reflection)
        )
        return cursor.lastrowid

def get_recent_moods(limit: int = 15, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves recent mood logs with safe pagination."""
    init_db(db_path)
    safe_limit = max(1, min(100, int(limit)))

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, mood_score, emotion_tags, context_trigger, reflection FROM mood_logs ORDER BY id DESC LIMIT ?",
            (safe_limit,)
        )
        rows = cursor.fetchall()

    logs = []
    for r in rows:
        try:
            tags = json.loads(r[3]) if r[3] else []
        except (json.JSONDecodeError, TypeError):
            tags = []
        logs.append({
            "id": r[0],
            "timestamp": r[1],
            "mood_score": r[2],
            "emotion_tags": tags,
            "context_trigger": r[4] or "",
            "reflection": r[5] or ""
        })
    return logs

def get_mood_stats(db_path: str = DB_PATH) -> Dict[str, Any]:
    """Calculates robust mood analytics and emotion frequency distribution."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT mood_score, emotion_tags FROM mood_logs")
        rows = cursor.fetchall()

    if not rows:
        return {"avg_score": 7.0, "total_logs": 0, "emotion_counts": {}}

    scores = [r[0] for r in rows if isinstance(r[0], (int, float))]
    avg_score = sum(scores) / len(scores) if scores else 7.0

    emotion_counts: Dict[str, int] = {}
    for r in rows:
        if r[1]:
            try:
                tags = json.loads(r[1])
                if isinstance(tags, list):
                    for t in tags:
                        t_clean = str(t).strip()
                        if t_clean:
                            emotion_counts[t_clean] = emotion_counts.get(t_clean, 0) + 1
            except Exception:
                pass

    return {
        "avg_score": round(avg_score, 1),
        "total_logs": len(rows),
        "emotion_counts": emotion_counts
    }

def log_coaching(category: str, query: str, advice: str, db_path: str = DB_PATH) -> int:
    """Logs coaching interactions with parameter sanitation."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO coaching_logs (category, user_query, advice_summary) VALUES (?, ?, ?)",
            (str(category or "general"), str(query or ""), str(advice or ""))
        )
        return cursor.lastrowid

def log_message_analysis(original_msg: str, confidence: int, neediness: str, banter: str, rewrites: List[Dict[str, str]], db_path: str = DB_PATH) -> int:
    """Persists message analysis reports."""
    init_db(db_path)
    clamped_conf = max(0, min(100, int(confidence)))
    safe_rewrites = rewrites if isinstance(rewrites, list) else []

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO message_analyses (original_message, confidence_score, neediness_level, banter_level, rewrites_json) VALUES (?, ?, ?, ?, ?)",
            (str(original_msg or ""), clamped_conf, str(neediness or ""), str(banter or ""), json.dumps(safe_rewrites))
        )
        return cursor.lastrowid

def log_roleplay_session(scenario_key: str, turns_count: int, scorecard: Dict[str, Any], db_path: str = DB_PATH) -> int:
    """Persists completed roleplay simulation evaluations."""
    init_db(db_path)
    safe_scorecard = scorecard if isinstance(scorecard, dict) else {}

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO roleplay_sessions (scenario_key, turns_count, scorecard_json) VALUES (?, ?, ?)",
            (str(scenario_key or "general"), max(1, int(turns_count)), json.dumps(safe_scorecard))
        )
        return cursor.lastrowid

def log_decompression(technique: str, duration: int = 120, notes: str = "", db_path: str = DB_PATH) -> int:
    """Persists decompression sessions."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO decompression_sessions (technique, duration_seconds, notes) VALUES (?, ?, ?)",
            (str(technique or "unspecified"), max(1, int(duration)), str(notes or ""))
        )
        return cursor.lastrowid
