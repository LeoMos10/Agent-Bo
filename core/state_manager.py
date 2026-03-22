class AgentState:
    def __init__(self):
        self.active = True
        self.mode = "ACTIVE"  # ACTIVE / IDLE
        self.last_task_time = None

    def set_idle(self):
        self.mode = "IDLE"

    def set_active(self):
        self.mode = "ACTIVE"