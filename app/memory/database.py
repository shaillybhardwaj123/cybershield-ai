import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cybershield_db.sqlite")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database with cases, memory bank, and observability tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        input_text TEXT,
        file_name TEXT,
        risk_score INTEGER,
        verdict TEXT,
        scam_type TEXT,
        explanation TEXT,
        evidence TEXT, -- JSON string list
        next_steps TEXT, -- JSON string list
        safe_reply TEXT,
        report_summary TEXT,
        timestamp TEXT
    )
    """)
    
    # 2. Memory Bank (Long-term entity history)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory_bank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT, -- 'domain', 'email', 'phone', 'url', 'phrase'
        entity_value TEXT UNIQUE,
        verdict TEXT, -- 'SAFE', 'SUSPICIOUS', 'HIGH RISK', 'DANGEROUS'
        times_seen INTEGER DEFAULT 1,
        last_seen TEXT
    )
    """)
    
    # 3. Observability traces (agent-by-agent execution trails)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS observability_traces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        agent_name TEXT,
        step TEXT,
        status TEXT,
        output TEXT,
        latency_ms INTEGER,
        timestamp TEXT
    )
    """)
    
    # 4. Tool calls log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tool_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        tool_name TEXT,
        inputs TEXT, -- JSON string
        output TEXT, -- JSON string
        timestamp TEXT
    )
    """)
    
    # 5. Seed initial Threat Intel data
    cursor.execute("SELECT COUNT(*) FROM memory_bank")
    if cursor.fetchone()[0] == 0:
        seed_data = [
            ('domain', 'tcs-career-verification.in', 'DANGEROUS', 15, datetime.now().isoformat()),
            ('domain', 'wipro-hrportal.co.in', 'DANGEROUS', 20, datetime.now().isoformat()),
            ('domain', 'google-job-offers.cc', 'DANGEROUS', 30, datetime.now().isoformat()),
            ('domain', 'telegram-tasks.online', 'HIGH RISK', 45, datetime.now().isoformat()),
            ('phone', '+91 88765 43210', 'DANGEROUS', 12, datetime.now().isoformat()),
            ('phone', '+91 99999 88888', 'HIGH RISK', 8, datetime.now().isoformat()),
            ('email', 'recruiter@gmail.com', 'SUSPICIOUS', 5, datetime.now().isoformat()),
            ('email', 'jobs-tcs-verify@outlook.com', 'HIGH RISK', 18, datetime.now().isoformat()),
            ('url', 'http://shorturl.at/xyzScam', 'DANGEROUS', 9, datetime.now().isoformat()),
            ('url', 'https://verify-account-security.net/login', 'DANGEROUS', 34, datetime.now().isoformat())
        ]
        cursor.executemany("""
        INSERT INTO memory_bank (entity_type, entity_value, verdict, times_seen, last_seen)
        VALUES (?, ?, ?, ?, ?)
        """, seed_data)
        
    conn.commit()
    conn.close()

# Helper methods for Cases
def save_case(case_data: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO cases (id, input_text, file_name, risk_score, verdict, scam_type, explanation, evidence, next_steps, safe_reply, report_summary, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_data['id'],
        case_data.get('input_text', ''),
        case_data.get('file_name', ''),
        case_data.get('risk_score', 0),
        case_data.get('verdict', 'SAFE'),
        case_data.get('scam_type', 'none'),
        case_data.get('explanation', ''),
        json.dumps(case_data.get('evidence', [])),
        json.dumps(case_data.get('next_steps', [])),
        case_data.get('safe_reply', ''),
        case_data.get('report_summary', ''),
        case_data.get('timestamp', datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()

def get_case(case_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        res = dict(row)
        res['evidence'] = json.loads(res['evidence'])
        res['next_steps'] = json.loads(res['next_steps'])
        return res
    return None

def get_all_cases(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        res = dict(r)
        res['evidence'] = json.loads(res['evidence'])
        res['next_steps'] = json.loads(res['next_steps'])
        result.append(res)
    return result

# Helper methods for Memory Bank
def lookup_memory_entity(entity_value: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memory_bank WHERE entity_value = ?", (entity_value.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_or_add_memory_entity(entity_type: str, entity_value: str, verdict: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    val = entity_value.lower().strip()
    cursor.execute("SELECT id, times_seen FROM memory_bank WHERE entity_value = ?", (val,))
    row = cursor.fetchone()
    now_str = datetime.now().isoformat()
    if row:
        cursor.execute("""
        UPDATE memory_bank 
        SET times_seen = times_seen + 1, last_seen = ?, verdict = ?
        WHERE id = ?
        """, (now_str, verdict, row['id']))
    else:
        cursor.execute("""
        INSERT INTO memory_bank (entity_type, entity_value, verdict, times_seen, last_seen)
        VALUES (?, ?, ?, 1, ?)
        """, (entity_type, val, verdict, now_str))
    conn.commit()
    conn.close()

# Helper methods for Traces (Observability)
def log_trace(case_id: str, agent_name: str, step: str, status: str, output: str, latency_ms: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO observability_traces (case_id, agent_name, step, status, output, latency_ms, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (case_id, agent_name, step, status, output, latency_ms, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_traces_for_case(case_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM observability_traces WHERE case_id = ? ORDER BY timestamp ASC", (case_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Helper methods for Tool Calls
def log_tool_call(case_id: str, tool_name: str, inputs: Dict[str, Any], output: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO tool_calls (case_id, tool_name, inputs, output, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (case_id, tool_name, json.dumps(inputs), json.dumps(output), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_tool_calls_for_case(case_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tool_calls WHERE case_id = ? ORDER BY timestamp ASC", (case_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        res = dict(r)
        res['inputs'] = json.loads(res['inputs'])
        res['output'] = json.loads(res['output'])
        result.append(res)
    return result

# Get analytical summary
def get_analytics_summary() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total cases scanned
    cursor.execute("SELECT COUNT(*) FROM cases")
    total_scans = cursor.fetchone()[0]
    
    # 2. Breakdown by verdict
    cursor.execute("SELECT verdict, COUNT(*) as count FROM cases GROUP BY verdict")
    verdict_counts = {r['verdict']: r['count'] for r in cursor.fetchall()}
    
    # 3. Breakdown by scam type
    cursor.execute("SELECT scam_type, COUNT(*) as count FROM cases GROUP BY scam_type ORDER BY count DESC")
    scam_counts = {r['scam_type']: r['count'] for r in cursor.fetchall()}
    
    # 4. Latency
    cursor.execute("SELECT AVG(latency_ms) FROM observability_traces WHERE step = 'complete' OR step = 'final_verdict'")
    row = cursor.fetchone()
    avg_latency = row[0] if row and row[0] else 0.0
    
    # 5. Top memory bank entities seen
    cursor.execute("SELECT entity_type, entity_value, verdict, times_seen FROM memory_bank ORDER BY times_seen DESC LIMIT 5")
    top_threats = [dict(r) for r in cursor.fetchall()]
    
    # 6. Total tool calls
    cursor.execute("SELECT COUNT(*) FROM tool_calls")
    total_tool_calls = cursor.fetchone()[0]
    
    # 7. Breakdown by tool
    cursor.execute("SELECT tool_name, COUNT(*) as count FROM tool_calls GROUP BY tool_name ORDER BY count DESC")
    tool_counts = {r['tool_name']: r['count'] for r in cursor.fetchall()}
    
    conn.close()
    
    return {
        "total_scans": total_scans,
        "verdicts": verdict_counts,
        "scam_types": scam_counts,
        "avg_latency_ms": round(avg_latency, 2),
        "top_threats": top_threats,
        "total_tool_calls": total_tool_calls,
        "tool_counts": tool_counts
    }

# --- Admin Database Operations ---

def delete_case_db(case_id: str):
    """Deletes a scanned case and all its associated traces and tool logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cases WHERE id = ?", (case_id,))
    cursor.execute("DELETE FROM observability_traces WHERE case_id = ?", (case_id,))
    cursor.execute("DELETE FROM tool_calls WHERE case_id = ?", (case_id,))
    conn.commit()
    conn.close()

def clear_all_cases_db():
    """Wipes all scanned cases, traces, and tool call logs completely."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cases")
    cursor.execute("DELETE FROM observability_traces")
    cursor.execute("DELETE FROM tool_calls")
    conn.commit()
    conn.close()

def get_all_memory_entities() -> List[Dict[str, Any]]:
    """Retrieves all memory bank threat indicators, ordered by times seen."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memory_bank ORDER BY times_seen DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_memory_entity_db(entity_id: int):
    """Deletes a specific threat indicator from the memory bank."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memory_bank WHERE id = ?", (entity_id,))
    conn.commit()
    conn.close()

def update_memory_entity_db(entity_id: int, entity_type: str, entity_value: str, verdict: str, times_seen: int):
    """Updates the type, value, verdict status, and counts of a threat indicator."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE memory_bank
    SET entity_type = ?, entity_value = ?, verdict = ?, times_seen = ?, last_seen = ?
    WHERE id = ?
    """, (entity_type, entity_value.lower().strip(), verdict, times_seen, datetime.now().isoformat(), entity_id))
    conn.commit()
    conn.close()

def add_memory_entity_db(entity_type: str, entity_value: str, verdict: str) -> int:
    """Inserts a new custom threat intelligence entity into the memory bank."""
    conn = get_db_connection()
    cursor = conn.cursor()
    val = entity_value.lower().strip()
    cursor.execute("""
    INSERT INTO memory_bank (entity_type, entity_value, verdict, times_seen, last_seen)
    VALUES (?, ?, ?, 1, ?)
    """, (entity_type, val, verdict, datetime.now().isoformat()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def reseed_memory_bank_db():
    """Wipes threat memory and resets it with default baseline rules."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memory_bank")
    seed_data = [
        ('domain', 'tcs-career-verification.in', 'DANGEROUS', 15, datetime.now().isoformat()),
        ('domain', 'wipro-hrportal.co.in', 'DANGEROUS', 20, datetime.now().isoformat()),
        ('domain', 'google-job-offers.cc', 'DANGEROUS', 30, datetime.now().isoformat()),
        ('domain', 'telegram-tasks.online', 'HIGH RISK', 45, datetime.now().isoformat()),
        ('phone', '+91 88765 43210', 'DANGEROUS', 12, datetime.now().isoformat()),
        ('phone', '+91 99999 88888', 'HIGH RISK', 8, datetime.now().isoformat()),
        ('email', 'recruiter@gmail.com', 'SUSPICIOUS', 5, datetime.now().isoformat()),
        ('email', 'jobs-tcs-verify@outlook.com', 'HIGH RISK', 18, datetime.now().isoformat()),
        ('url', 'http://shorturl.at/xyzScam', 'DANGEROUS', 9, datetime.now().isoformat()),
        ('url', 'https://verify-account-security.net/login', 'DANGEROUS', 34, datetime.now().isoformat())
    ]
    cursor.executemany("""
    INSERT INTO memory_bank (entity_type, entity_value, verdict, times_seen, last_seen)
    VALUES (?, ?, ?, ?, ?)
    """, seed_data)
    conn.commit()
    conn.close()

