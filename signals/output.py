import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List

# Using dataclasses for simple schema (could also use pydantic)
from dataclasses import dataclass, asdict

@dataclass
class SignalRecord:
    company: str
    signal_type: str
    source_url: str
    matched_keywords: List[str]
    signal_score: int
    detected_at: str  # ISO timestamp
    reason: str

def write_json(records: List[SignalRecord], output_path: Path) -> None:
    """Write list of SignalRecord to JSON file (pretty printed)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as f:
        json.dump([asdict(rec) for rec in records], f, ensure_ascii=False, indent=2)

def write_sqlite(records: List[SignalRecord], db_path: Path) -> None:
    """Write records into a SQLite database with a simple schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            signal_type TEXT,
            source_url TEXT,
            matched_keywords TEXT,
            signal_score INTEGER,
            detected_at TEXT,
            reason TEXT
        )
    ''')
    insert_sql = '''
        INSERT INTO signals (
            company, signal_type, source_url, matched_keywords,
            signal_score, detected_at, reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    for rec in records:
        cur.execute(insert_sql, (
            rec.company,
            rec.signal_type,
            rec.source_url,
            json.dumps(rec.matched_keywords),
            rec.signal_score,
            rec.detected_at,
            rec.reason,
        ))
    conn.commit()
    conn.close()

# Exported symbols
__all__ = [
    'SignalRecord',
    'write_json',
    'write_sqlite',
]
