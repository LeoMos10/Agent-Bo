from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Dict, Any


class AgentLoop:
    def __init__(self, agent, settings: Dict[str, Any]):
        self.agent = agent
        self.settings = settings
        self.running = False
        self.last_reflection = datetime.now()
        self.last_healthcheck = datetime.now()

    def start(self):
        self.running = True
        print("[BOOT] LeoAgent avviato in modalità semi-autonoma")

        while self.running:
            now = datetime.now()

            try:
                self.agent.check_idle()

                if now - self.last_healthcheck >= timedelta(
                    minutes=self.settings["agent"]["healthcheck_minutes"]
                ):
                    self.agent.run_healthcheck()
                    self.last_healthcheck = now

                if now - self.last_reflection >= timedelta(
                    minutes=self.settings["agent"]["idle_reflection_minutes"]
                ):
                    self.agent.run_reflection_cycle()
                    self.last_reflection = now

            except Exception as e:
                print(f"[LOOP ERROR] {e}")

            time.sleep(self.settings["agent"]["loop_sleep_seconds"])

    def stop(self):
        self.running = False