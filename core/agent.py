from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from memory.log_db import LogDB
from models.ollama_client import OllamaClient
from core.state_manager import AgentState
from tools.terminal_engine import TerminalEngine


class Agent:
    def __init__(self, settings: Dict[str, Any], policy=None):
        self.settings = settings
        self.policy = policy
        self.log_db = LogDB()
        self.model = OllamaClient(
            model=settings["ollama"]["model"],
            base_url=settings["ollama"]["base_url"],
        )
        self.state = AgentState()
        self.terminal = TerminalEngine(allowed_root="C:\\Leo\\AI-Agent")

    def process_task(self, task: str):
        print(f"\n[Task Received] {task}")

        try:
            lower = task.lower().strip()

            # Comandi terminali espliciti
            if lower.startswith("cmd:"):
                cmd = task[4:].strip()
                self.run_terminal_command(cmd, powershell=False)
                return

            if lower.startswith("ps:"):
                cmd = task[3:].strip()
                self.run_terminal_command(cmd, powershell=True)
                return

            plan = {"strategy": "direct_generate"}
            response = self.model.generate(task)

            self.log_db.log_task(
                task=task,
                plan=plan,
                result=response,
                success=True
            )

            self.state.last_task_time = datetime.now()

            print("\n[Response]")
            print(response)

        except Exception as e:
            self.log_db.log_task(
                task=task,
                plan={},
                result="",
                success=False,
                error=str(e)
            )
            print(f"[ERROR] {e}")

    def run_terminal_command(self, command: str, powershell: bool = False):
        action = "install_software" if "pip install" in command.lower() or "winget install" in command.lower() else "safe_terminal"

        step = {
            "action": action,
            "command": command,
        }

        decision = self.policy.decide(step) if self.policy else "allow"

        if decision == "deny":
            raise PermissionError(f"Azione negata dalla policy: {command}")

        if decision == "confirm":
            print(f"[CONFIRM REQUIRED] Conferma richiesta per: {command}")
            answer = input("Procedo? (y/n): ").strip().lower()
            if answer != "y":
                print("[CANCELLED]")
                return

        result = self.terminal.run(command=command, powershell=powershell)

        self.log_db.log_terminal(
            command=result.command,
            cwd=result.cwd,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            success=(result.returncode == 0),
        )

        print("\n[TERMINAL RESULT]")
        print(f"cwd: {result.cwd}")
        print(f"returncode: {result.returncode}")

        if result.stdout.strip():
            print("\n[stdout]")
            print(result.stdout)

        if result.stderr.strip():
            print("\n[stderr]")
            print(result.stderr)

    def check_idle(self):
        timeout = self.settings["ollama"]["unload_after_idle_seconds"]
        self.model.unload_if_idle(timeout=timeout)

    def run_healthcheck(self):
        print("[HEALTHCHECK] OK")

    def run_reflection_cycle(self):
        print("[REFLECTION] Analisi task precedenti...")
        try:
            last_tasks = self.log_db.get_last_tasks(limit=5)
            for row in last_tasks:
                print(" -", row)
        except Exception as e:
            print(f"[REFLECTION ERROR] {e}")