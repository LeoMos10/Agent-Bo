from __future__ import annotations

import requests
import time


class OllamaClient:
    def __init__(self, model="qwen2.5:7b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.last_used = time.time()

    def generate(self, prompt: str) -> str:
        self.last_used = time.time()

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "5m",
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"]

    def unload_if_idle(self, timeout=300):
        if time.time() - self.last_used > timeout:
            try:
                requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": "",
                        "keep_alive": 0,
                        "stream": False,
                    },
                    timeout=30,
                )
                print(f"[MODEL] {self.model} scaricato dalla memoria")
                self.last_used = time.time()
            except Exception as e:
                print(f"[MODEL UNLOAD ERROR] {e}")