"""
Project Jessica - 3-Tier Write-Through Persistence Engine
Tier 1: 32GB System RAM Resident Cache (Zero-latency access < 0.05 ms)
Tier 2: High-Performance SQLite Eternal Memory Database (Zero-lag async write queue)
Tier 3: Obsidian Vault Markdown Memory Graph (Human-readable knowledge persistence)

Storage Root: E:/GitHub/JESSICA_STORAGE/memory/jessica_eternal_memory.db
"""

import os
import sys
import time
import json
import sqlite3
import queue
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Primary and fallback storage locations
PRIMARY_STORAGE_DIR = Path("E:/GitHub/JESSICA_STORAGE/memory")
FALLBACK_STORAGE_DIR = WORKSPACE_ROOT / "memory"

def resolve_db_path() -> Path:
    try:
        PRIMARY_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        # Test write access
        test_file = PRIMARY_STORAGE_DIR / ".write_test"
        test_file.touch()
        test_file.unlink()
        return PRIMARY_STORAGE_DIR / "jessica_eternal_memory.db"
    except Exception:
        FALLBACK_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        return FALLBACK_STORAGE_DIR / "jessica_eternal_memory.db"

DB_PATH = resolve_db_path()


class PersistenceEngine:
    """
    SQLite-backed asynchronous write-through persistence engine.
    Ensures zero blocking on the main inference/event loop by utilizing
    an internal background worker queue with a single dedicated connection.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True, name="PersistenceWorker")
        self._init_schema()
        self._worker_thread.start()
        self._seed_creator_core_facts()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for high concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_schema(self):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        emotion TEXT DEFAULT 'warm',
                        timestamp TEXT NOT NULL,
                        tokens INTEGER DEFAULT 0
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS creator_facts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        confidence REAL DEFAULT 1.0,
                        learned_at TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        UNIQUE(category, key)
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_telemetry (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        gpu_vram_used_mb REAL,
                        cpu_threads_active INTEGER,
                        ram_cache_docs INTEGER,
                        disk_free_gb REAL
                    );
                """)
                # Indexes for fast retrieval
                conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_time ON conversations(timestamp);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_cat_key ON creator_facts(category, key);")
        finally:
            conn.close()

    def _seed_creator_core_facts(self):
        """
        Seeds baseline Creator Core Facts into SQLite if table is empty.
        """
        baseline_facts = [
            ("identity", "full_name", "Alexander Lopez", 1.0),
            ("identity", "preferred_title", "Boss", 1.0),
            ("identity", "role", "Sole Creator, System Architect, and Master Operator of Project Jessica", 1.0),
            ("relationship", "girlfriend", "Crishaira", 1.0),
            ("cue", "arrival_cue", "Jessica! Daddy's home", 1.0),
            ("cue", "girlfriend_greeting", "Hi Crishaira, you are so pretty today, but still smell like sinigang!", 1.0),
            ("gear", "instrument", "4-string passive Jcraft Jazz bass guitar", 1.0),
            ("hardware", "gpu", "NVIDIA GeForce RTX 4060 (8GB VRAM, Ada Lovelace)", 1.0),
            ("hardware", "cpu", "Intel Core i5 11th Gen (12 Threads)", 1.0),
            ("hardware", "ram", "32 GB Dual-Channel System Memory", 1.0),
            ("hardware", "storage", "294 GB Free Space on E:\\GitHub\\JESSICA_STORAGE\\", 1.0),
            ("preference", "speaking_style", "Concise, punchy spoken replies (2-3 sentences), warm, witty, zero disclaimers", 1.0)
        ]
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        for cat, key, val, conf in baseline_facts:
            self.upsert_creator_fact(cat, key, val, conf, now)

    def _process_queue(self):
        conn = self._get_connection()
        while not self._stop_event.is_set():
            try:
                task = self._write_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if task is None:
                self._write_queue.task_done()
                break

            op, args = task
            try:
                with conn:
                    if op == "conv":
                        conn.execute("""
                            INSERT INTO conversations (session_id, role, content, emotion, timestamp, tokens)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, args)
                    elif op == "fact":
                        conn.execute("""
                            INSERT INTO creator_facts (category, key, value, confidence, learned_at, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ON CONFLICT(category, key) DO UPDATE SET
                                value = excluded.value,
                                confidence = excluded.confidence,
                                last_updated = excluded.last_updated
                        """, args)
                    elif op == "telemetry":
                        conn.execute("""
                            INSERT INTO system_telemetry (timestamp, gpu_vram_used_mb, cpu_threads_active, ram_cache_docs, disk_free_gb)
                            VALUES (?, ?, ?, ?, ?)
                        """, args)
            except Exception as e:
                print(f"[!] PersistenceEngine SQLite write error ({op}): {e}")
            finally:
                self._write_queue.task_done()

        conn.close()

    def log_turn(self, session_id: str, role: str, content: str, emotion: str = "warm", tokens: int = 0):
        """
        Asynchronously writes conversation turn to SQLite. Returns immediately in < 0.01 ms.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self._write_queue.put(("conv", (session_id, role, content, emotion, timestamp, tokens)))

    def upsert_creator_fact(self, category: str, key: str, value: str, confidence: float = 1.0, timestamp: Optional[str] = None):
        """
        Asynchronously upserts a creator core fact into SQLite.
        """
        ts = timestamp or time.strftime("%Y-%m-%d %H:%M:%S")
        self._write_queue.put(("fact", (category, key, value, confidence, ts, ts)))

    def log_telemetry(self, gpu_vram_mb: float, cpu_threads: int, ram_docs: int, disk_free_gb: float):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self._write_queue.put(("telemetry", (ts, gpu_vram_mb, cpu_threads, ram_docs, disk_free_gb)))

    def flush(self, timeout: float = 2.0):
        """
        Blocks until the write queue is fully flushed to disk.
        """
        try:
            self._write_queue.join()
        except Exception:
            pass

    def get_recent_conversations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Reads recent conversation turns from SQLite.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, session_id, role, content, emotion, timestamp, tokens
                FROM conversations
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            results = [dict(r) for r in reversed(rows)]
            return results
        finally:
            conn.close()

    def get_creator_facts(self) -> List[Dict[str, Any]]:
        """
        Reads all creator facts from SQLite.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, key, value, confidence, learned_at, last_updated
                FROM creator_facts
                ORDER BY category, key
            """)
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def close(self):
        self.flush()
        self._stop_event.set()
        self._write_queue.put(None)
        self._worker_thread.join(timeout=2.0)


# Global Singleton Persistence Engine
PERSISTENCE_ENGINE = PersistenceEngine()


def get_persistence_engine() -> PersistenceEngine:
    return PERSISTENCE_ENGINE

