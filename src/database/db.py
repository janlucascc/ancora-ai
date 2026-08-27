import sqlite3
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "data", "ancora.db"))

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Returns a thread-safe SQLite connection."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    # check_same_thread=False is CRITICAL for Streamlit's multithreaded environment
    return sqlite3.connect(db_path, check_same_thread=False)

def init_db(db_path: str = DB_PATH):
    """Initializes SQLite database with all schema tables safely."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # User Preferences & Settings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ─── NEW: CHAT PERSISTENCE ──────────────────────────────
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            thought TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
        )
        """)

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

# ══════════════════════════════════════════════════════════════
# CHAT PERSISTENCE API (Fixes loss of chat on F5)
# ══════════════════════════════════════════════════════════════

def get_all_chat_sessions(db_path: str = DB_PATH) -> Dict[str, Any]:
    """Loads all chat sessions and their messages."""
    init_db(db_path)
    sessions = {}
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Load Sessions (ASC so that dict preserves insertion order; sidebar reverses it for display)
        cursor.execute("SELECT session_id, title FROM chat_sessions ORDER BY updated_at ASC")
        for row in cursor.fetchall():
            s_id, title = row
            sessions[s_id] = {"title": title, "messages": []}

        # Load Messages
        cursor.execute("SELECT session_id, role, content, thought FROM chat_messages ORDER BY timestamp ASC, id ASC")
        for row in cursor.fetchall():
            s_id, role, content, thought = row
            if s_id in sessions:
                sessions[s_id]["messages"].append({
                    "role": role,
                    "content": content,
                    "thought": thought or ""
                })
    return sessions

def save_chat_session(session_id: str, title: str, db_path: str = DB_PATH):
    """Creates or updates a chat session title."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_sessions (session_id, title, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(session_id) DO UPDATE SET title=excluded.title, updated_at=CURRENT_TIMESTAMP",
            (str(session_id), str(title))
        )
        conn.commit()

def save_chat_message(session_id: str, role: str, content: str, thought: str = "", db_path: str = DB_PATH):
    """Saves a single message to a session."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Ensure session exists first
        cursor.execute("INSERT OR IGNORE INTO chat_sessions (session_id, title) VALUES (?, ?)", (session_id, "Conversa"))
        cursor.execute(
            "INSERT INTO chat_messages (session_id, role, content, thought) VALUES (?, ?, ?, ?)",
            (str(session_id), str(role), str(content), str(thought))
        )
        # Update session timestamp
        cursor.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
        conn.commit()

# ══════════════════════════════════════════════════════════════
# USER SETTINGS PERSISTENCE
# ══════════════════════════════════════════════════════════════
def save_preference(key: str, value: str, db_path: str = DB_PATH):
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
            (str(key), str(value))
        )
        conn.commit()

def get_preference(key: str, default: str = "", db_path: str = DB_PATH) -> str:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM user_settings WHERE key = ?", (str(key),))
        row = cursor.fetchone()
        return str(row[0]) if row else default

def get_all_preferences(db_path: str = DB_PATH) -> Dict[str, str]:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM user_settings")
        return {r[0]: r[1] for r in cursor.fetchall()}

# ══════════════════════════════════════════════════════════════
# LGPD COMPLIANCE TOOLS
# ══════════════════════════════════════════════════════════════
def export_user_data_lgpd(db_path: str = DB_PATH) -> Dict[str, Any]:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mood_logs")
        moods = cursor.fetchall()
        cursor.execute("SELECT * FROM coaching_logs")
        coaching = cursor.fetchall()
        cursor.execute("SELECT * FROM decompression_sessions")
        decompression = cursor.fetchall()
        cursor.execute("SELECT * FROM message_analyses")
        analyses = cursor.fetchall()
        cursor.execute("SELECT * FROM roleplay_sessions")
        roleplays = cursor.fetchall()
        cursor.execute("SELECT * FROM user_settings")
        settings = cursor.fetchall()
        
        # Also export chats
        cursor.execute("SELECT * FROM chat_sessions")
        sessions = cursor.fetchall()
        cursor.execute("SELECT * FROM chat_messages")
        messages = cursor.fetchall()

    return {
        "lgpd_compliance": {
            "law": "LGPD (Lei Geral de Proteção de Dados - Brasil / Lei 13.709/2018)",
            "data_controller": "Usuário Local (Armazenamento 100% Descentralizado)",
            "pii_collected": False,
            "export_timestamp": datetime.now().isoformat()
        },
        "preferences": settings,
        "chat_sessions": sessions,
        "chat_messages": messages,
        "mood_logs": moods,
        "coaching_logs": coaching,
        "decompression_sessions": decompression,
        "message_analyses": analyses,
        "roleplay_sessions": roleplays
    }

def delete_all_user_data_lgpd(db_path: str = DB_PATH) -> bool:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages")
        cursor.execute("DELETE FROM chat_sessions")
        cursor.execute("DELETE FROM mood_logs")
        cursor.execute("DELETE FROM coaching_logs")
        cursor.execute("DELETE FROM decompression_sessions")
        cursor.execute("DELETE FROM message_analyses")
        cursor.execute("DELETE FROM roleplay_sessions")
        cursor.execute("DELETE FROM user_settings")
        conn.commit()
    return True

# ══════════════════════════════════════════════════════════════
# DOMAIN LOGGING FUNCTIONS
# ══════════════════════════════════════════════════════════════
def log_mood(score: int, emotions: List[str], trigger: str, reflection: str, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    clamped_score = max(1, min(10, int(score)))
    safe_emotions = emotions if isinstance(emotions, list) else []
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mood_logs (mood_score, emotion_tags, context_trigger, reflection) VALUES (?, ?, ?, ?)",
            (clamped_score, json.dumps(safe_emotions), str(trigger or ""), str(reflection or ""))
        )
        conn.commit()
        return cursor.lastrowid

def get_recent_moods(limit: int = 15, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, mood_score, emotion_tags, context_trigger, reflection FROM mood_logs ORDER BY id DESC LIMIT ?",
            (max(1, int(limit)),)
        )
        rows = cursor.fetchall()
        
    logs = []
    for r in rows:
        tags = []
        if r[3]:
            try: tags = json.loads(r[3])
            except: pass
        logs.append({
            "id": r[0], "timestamp": r[1], "mood_score": r[2],
            "emotion_tags": tags, "context_trigger": r[4], "reflection": r[5]
        })
    return logs

def get_mood_stats(db_path: str = DB_PATH) -> Dict[str, Any]:
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
                for t in tags:
                    tc = str(t).strip()
                    if tc: emotion_counts[tc] = emotion_counts.get(tc, 0) + 1
            except: pass

    return {"avg_score": round(avg_score, 1), "total_logs": len(rows), "emotion_counts": emotion_counts}

def log_coaching(category: str, query: str, advice: str, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO coaching_logs (category, user_query, advice_summary) VALUES (?, ?, ?)",
            (str(category or ""), str(query or ""), str(advice or "")))
        conn.commit()
        return cursor.lastrowid

def log_message_analysis(original_msg: str, confidence: int, neediness: str, banter: str, rewrites: List[Dict[str, str]], db_path: str = DB_PATH) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO message_analyses (original_message, confidence_score, neediness_level, banter_level, rewrites_json) VALUES (?, ?, ?, ?, ?)",
            (str(original_msg or ""), max(0, min(100, int(confidence))), str(neediness or ""), str(banter or ""), json.dumps(rewrites if isinstance(rewrites, list) else [])))
        conn.commit()
        return cursor.lastrowid

def log_roleplay_session(scenario_key: str, turns_count: int, scorecard: Dict[str, Any], db_path: str = DB_PATH) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO roleplay_sessions (scenario_key, turns_count, scorecard_json) VALUES (?, ?, ?)",
            (str(scenario_key or ""), max(1, int(turns_count)), json.dumps(scorecard if isinstance(scorecard, dict) else {})))
        conn.commit()
        return cursor.lastrowid

def log_decompression(technique: str, duration: int = 120, notes: str = "", db_path: str = DB_PATH) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO decompression_sessions (technique, duration_seconds, notes) VALUES (?, ?, ?)",
            (str(technique or ""), max(1, int(duration)), str(notes or "")))
        conn.commit()
        return cursor.lastrowid
