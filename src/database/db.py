import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "data", "ancora.db"))

def init_db(db_path: str = DB_PATH):
    """Initializes SQLite database and creates tables if they do not exist."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Mood & Emotional Logs
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

    # Wingman & Coaching Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coaching_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        category TEXT NOT NULL,
        user_query TEXT NOT NULL,
        advice_summary TEXT NOT NULL
    )
    """)

    # Decompression Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS decompression_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        technique TEXT NOT NULL,
        duration_seconds INTEGER DEFAULT 120,
        notes TEXT
    )
    """)

    # Message Lab Analyses
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

    # Roleplay Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roleplay_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        scenario_key TEXT NOT NULL,
        turns_count INTEGER NOT NULL,
        scorecard_json TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def log_mood(score: int, emotions: List[str], trigger: str, reflection: str, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mood_logs (mood_score, emotion_tags, context_trigger, reflection) VALUES (?, ?, ?, ?)",
        (score, json.dumps(emotions), trigger, reflection)
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def get_recent_moods(limit: int = 15, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, mood_score, emotion_tags, context_trigger, reflection FROM mood_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "timestamp": r[1],
            "mood_score": r[2],
            "emotion_tags": json.loads(r[3]) if r[3] else [],
            "context_trigger": r[4],
            "reflection": r[5]
        })
    return logs

def get_mood_stats(db_path: str = DB_PATH) -> Dict[str, Any]:
    """Calculates mood analytics and emotion distribution."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT mood_score, emotion_tags FROM mood_logs")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"avg_score": 7.0, "total_logs": 0, "emotion_counts": {}}

    scores = [r[0] for r in rows]
    avg_score = sum(scores) / len(scores)

    emotion_counts: Dict[str, int] = {}
    for r in rows:
        if r[1]:
            try:
                tags = json.loads(r[1])
                for t in tags:
                    emotion_counts[t] = emotion_counts.get(t, 0) + 1
            except Exception:
                pass

    return {
        "avg_score": round(avg_score, 1),
        "total_logs": len(rows),
        "emotion_counts": emotion_counts
    }

def log_coaching(category: str, query: str, advice: str, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO coaching_logs (category, user_query, advice_summary) VALUES (?, ?, ?)",
        (category, query, advice)
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def log_message_analysis(original_msg: str, confidence: int, neediness: str, banter: str, rewrites: List[Dict[str, str]], db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO message_analyses (original_message, confidence_score, neediness_level, banter_level, rewrites_json) VALUES (?, ?, ?, ?, ?)",
        (original_msg, confidence, neediness, banter, json.dumps(rewrites))
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def log_roleplay_session(scenario_key: str, turns_count: int, scorecard: Dict[str, Any], db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO roleplay_sessions (scenario_key, turns_count, scorecard_json) VALUES (?, ?, ?)",
        (scenario_key, turns_count, json.dumps(scorecard))
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def log_decompression(technique: str, duration: int = 120, notes: str = "", db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO decompression_sessions (technique, duration_seconds, notes) VALUES (?, ?, ?)",
        (technique, duration, notes)
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id
