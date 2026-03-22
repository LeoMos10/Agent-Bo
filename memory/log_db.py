import sqlite3
import json
from datetime import datetime
from pathlib import Path


DB_PATH = Path("memory/agent_logs.db")


class LogDB:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            task TEXT,
            plan TEXT,
            result TEXT,
            success INTEGER,
            error TEXT
        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS terminal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            command TEXT,
            cwd TEXT,
            returncode INTEGER,
            stdout TEXT,
            stderr TEXT,
            success INTEGER
        )
        """)
        self.conn.commit()

    def log_task(self, task, plan, result, success=True, error=None):
        self.conn.execute("""
        INSERT INTO task_logs (timestamp, task, plan, result, success, error)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            task,
            json.dumps(plan, ensure_ascii=False),
            result,
            int(success),
            error
        ))
        self.conn.commit()

    def log_terminal(self, command, cwd, returncode, stdout, stderr, success):
        self.conn.execute("""
        INSERT INTO terminal_logs (timestamp, command, cwd, returncode, stdout, stderr, success)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            command,
            cwd,
            returncode,
            stdout,
            stderr,
            int(success)
        ))
        self.conn.commit()

    def get_last_tasks(self, limit=10):
        cursor = self.conn.execute("""
        SELECT timestamp, task, success FROM task_logs
        ORDER BY id DESC LIMIT ?
        """, (limit,))
        return cursor.fetchall()

    def get_last_terminal(self, limit=10):
        cursor = self.conn.execute("""
        SELECT timestamp, command, returncode, success FROM terminal_logs
        ORDER BY id DESC LIMIT ?
        """, (limit,))
        return cursor.fetchall()