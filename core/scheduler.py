import time


class Scheduler:
    def __init__(self, agent):
        self.agent = agent

    def run_idle_check(self):
        while True:
            time.sleep(60)
            self.agent.check_idle()