from __future__ import annotations

from typing import Dict, Any


class PolicyEngine:
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings

    def decide(self, step: Dict[str, Any]) -> str:
        """
        Ritorna:
        - 'allow'
        - 'confirm'
        - 'deny'
        """
        action = step.get("action", "").lower()

        if action in {"read_web", "generate_report", "download_file", "safe_terminal"}:
            return "allow"

        if action == "install_software" and self.settings["permissions"]["require_confirmation_install"]:
            return "confirm"

        if action == "modify_system_file" and self.settings["permissions"]["require_confirmation_system_files"]:
            return "confirm"

        if action == "delete_file" and self.settings["permissions"]["require_confirmation_delete"]:
            return "confirm"

        if action == "print_document" and self.settings["permissions"]["require_confirmation_print"]:
            return "confirm"

        if action == "submit_form" and self.settings["permissions"]["require_confirmation_submit"]:
            return "confirm"

        dangerous = {
            "format_disk",
            "disable_defender",
            "edit_registry",
            "kill_critical_process",
        }

        if action in dangerous:
            return "deny"

        return "allow"