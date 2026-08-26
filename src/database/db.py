import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "data", "ancora.db"))

def init_db(db_path: str = DB_PATH):
    """Initializes SQLite database and creates tables if they do not exist."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
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

def get_recent_moods(limit: int = 10, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
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

def get_recent_coachings(limit: int = 10, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, category, user_query, advice_summary FROM coaching_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "timestamp": r[1], "category": r[2], "user_query": r[3], "advice_summary": r[4]} for r in rows]

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
