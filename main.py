from __future__ import annotations

import threading
import yaml

from core.agent import Agent
from core.agent_loop import AgentLoop
from core.policy import PolicyEngine


def load_settings(path: str = "config/settings.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    settings = load_settings()
    policy = PolicyEngine(settings)
    agent = Agent(settings=settings, policy=policy)
    loop = AgentLoop(agent=agent, settings=settings)

    loop_thread = threading.Thread(target=loop.start, daemon=True)
    loop_thread.start()

    print("LeoAgent pronto.")
    print("Comandi: scrivi una richiesta, oppure 'exit' per chiudere.\n")

    while True:
        task = input(">>> ").strip()

        if task.lower() == "exit":
            loop.stop()
            print("Shutting down...")
            break

        if not task:
            continue

        agent.process_task(task)


if __name__ == "__main__":
    main()