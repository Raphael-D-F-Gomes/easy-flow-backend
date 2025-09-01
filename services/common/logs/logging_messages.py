class LogMessages:
    def __init__(self, scenario_id: int) -> None:
        self.scenario_id = scenario_id

    def error_message(self, error: str) -> str:
        return f"scenario_{self.scenario_id}:-{error}"
