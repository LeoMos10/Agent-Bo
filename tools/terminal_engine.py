from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TerminalResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    cwd: str


class TerminalEngine:
    def __init__(self, allowed_root: str | None = None):
        self.allowed_root = Path(allowed_root).resolve() if allowed_root else None

        self.blocked_patterns = {
            "format",
            "diskpart",
            "del /f /s /q c:\\",
            "rd /s /q c:\\",
            "shutdown /s",
            "shutdown /r",
            "reg delete",
            "bcdedit",
            "cipher /w",
            "takeown /f c:\\windows",
            "icacls c:\\windows",
        }

    def _is_dangerous(self, command: str) -> bool:
        lower = command.lower()
        return any(pattern in lower for pattern in self.blocked_patterns)

    def _resolve_cwd(self, cwd: Optional[str]) -> str:
        if cwd is None:
            cwd = os.getcwd()

        resolved = Path(cwd).resolve()

        if self.allowed_root:
            if resolved != self.allowed_root and self.allowed_root not in resolved.parents:
                raise PermissionError(f"CWD fuori area consentita: {resolved}")

        return str(resolved)

    def run(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 120,
        powershell: bool = False,
    ) -> TerminalResult:
        if self._is_dangerous(command):
            raise PermissionError(f"Comando bloccato dalla policy: {command}")

        safe_cwd = self._resolve_cwd(cwd)

        if powershell:
            full_cmd = ["powershell", "-NoProfile", "-Command", command]
        else:
            # Usa cmd.exe così funzionano anche comandi interni come:
            # dir, echo, copy, type, del, cd, ecc.
            full_cmd = ["cmd", "/c", command]

        completed = subprocess.run(
            full_cmd,
            cwd=safe_cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )

        return TerminalResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            cwd=safe_cwd,
        )