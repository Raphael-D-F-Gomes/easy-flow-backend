from typing import Any

import logging
import threading
import os
import tempfile


log_path = tempfile.mkdtemp()


def get_logger_name(scenario_id: int, service_name: str) -> str:
    return f"scenario_log"


class ThreadLogger:
    def __init__(self, scenario_id: int = 0, service_name: str = "") -> None:
        self.thread_service = service_name
        self.thread_scenario = scenario_id

    @property
    def logger_name(self) -> str:
        return threading.current_thread().name

    @property
    def logger(self) -> logging.Logger:
        logger = logging.getLogger(self.logger_name)
        # Add File Handler and Then open
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)
        file_path = self.get_logger_file_handler_path()
        handler = logging.FileHandler(file_path)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s:-%(levelname)s:-%(message)s-3nd$l0g-")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def get_logger_file_handler_path(self) -> str:
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        return os.path.join(log_path, self.logger_name + ".log")

    def log_result(self, result: Any, declare_result: bool, func_name: str) -> None:
        if declare_result:
            self.logger.info(f"{func_name} {repr(result)}")

    def info(self, message: str) -> None:
        message = f"{message}"
        self.logger.info(message)

    def error(self, message: str) -> None:
        message = f"{message}"
        self.logger.error(message)


class ThreadModelLogger:
    def __init__(self, scenario_id: int = 0, service_name: str = "") -> None:
        self.thread_service = service_name
        self.thread_scenario = scenario_id

    @property
    def logger_name(self) -> str:
        return "model-log"

    @property
    def logger(self) -> logging.Logger:
        logger = logging.getLogger(self.logger_name)
        # Add File Handler and Then open
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)
        file_path = self.get_logger_file_handler_path()
        handler = logging.FileHandler(file_path)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s:-%(levelname)s:-%(message)s-3nd$l0g-")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def get_logger_file_handler_path(self) -> str:
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        return os.path.join(log_path, self.logger_name + ".log")

    def log_result(self, result: Any, declare_result: bool, func_name: str) -> None:
        if declare_result:
            self.logger.info(f"{func_name} {repr(result)}")

    def info(self, message: str) -> None:
        message = f"{message}"
        self.logger.info(message)

    def error(self, message: str) -> None:
        message = f"{message}"
        self.logger.error(message)


class ThreadProjectLogger:
    def __init__(self, scenario_id: int = 0, service_name: str = "") -> None:
        self.thread_service = service_name
        self.thread_scenario = scenario_id

    @property
    def logger_name(self) -> str:
        return "project-log"

    @property
    def logger(self) -> logging.Logger:
        logger = logging.getLogger(self.logger_name)
        # Add File Handler and Then open
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)
        file_path = self.get_logger_file_handler_path()
        handler = logging.FileHandler(file_path)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s:-%(levelname)s:-%(message)s-3nd$l0g-")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def get_logger_file_handler_path(self) -> str:
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        return os.path.join(log_path, self.logger_name + ".log")

    def log_result(self, result: Any, declare_result: bool, func_name: str) -> None:
        if declare_result:
            self.logger.info(f"{func_name} {repr(result)}")

    def info(self, message: str) -> None:
        message = f"{message}"
        self.logger.info(message)

    def error(self, message: str) -> None:
        message = f"{message}"
        self.logger.error(message)
