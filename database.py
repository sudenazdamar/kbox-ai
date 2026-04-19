import sqlite3
import json
from datetime import datetime

DB_PATH = "scholar_chatbot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            language TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_search(query: str, answer: str, sources: list, language: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sources_json = json.dumps([{
        "title": s.title,
        "authors": s.authors,
        "year": s.year,
        "link": s.link,
        "citations": s.citations,
    } for s in sources])
    cursor.execute("""
        INSERT INTO search_history (query, answer, sources, language, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (query, answer, sources_json, language, datetime.now().strftime("%d.%m.%Y %H:%M")))
    conn.commit()
    conn.close()

def get_history(limit: int = 20) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, query, answer, sources, language, created_at 
        FROM search_history 
        ORDER BY id DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_search(search_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history WHERE id = ?", (search_id,))
    conn.commit()
    conn.close()

def clear_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history")
    conn.commit()
    conn.close()

init_db()