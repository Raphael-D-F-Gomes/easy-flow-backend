from typing import Tuple, Dict, Callable, Any, Union, List

import logging
import io
import traceback

from data_store_endpoints import API_SAVE_LOG

from shared.logs.logging_messages import LogMessages
from shared.api.api import Client, CustomResponse


class LoggerTryCatch:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.errors_logging: List[Exception] = []

    def info(self, message: str) -> None:
        try:
            self.logger.info(message)
        except Exception as error:
            self.errors_logging.append(error)

    def error(self, message: str) -> None:
        try:
            self.logger.error(message)
        except Exception as error:
            self.errors_logging.append(error)


class LogManager:
    def __init__(self, service: str, scenario_id: int, data_endpoint: Client, auth_headers: Dict[str, str]) -> None:
        self.service = service
        self.scenario_id = scenario_id
        self.log_capture_string = io.StringIO()
        self.data_endpoint = data_endpoint
        self.auth_headers = auth_headers

    def build_logger(self) -> None:
        service = self.service
        scenario_id = self.scenario_id
        logger = logging.getLogger(f"{service}_logger_scenario_{scenario_id}")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(self.log_capture_string)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s:-%(levelname)s:-%(message)s-3nd$l0g-")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def save_and_close_logger(self) -> Tuple[CustomResponse, int]:
        scenario_id = self.scenario_id
        log_content = self.log_capture_string.getvalue()
        self.log_capture_string.close()
        response = self.data_endpoint.post(
            API_SAVE_LOG,
            timeout=120,
            json={"scenario-id": scenario_id, "log-content": log_content},
            headers=self.auth_headers,
        )
        return response, response.status_code

    def get_log_content(self) -> str:
        return self.log_capture_string.getvalue()

    def get_error(self, func: Callable) -> Any:
        service = self.service
        scenario_id = self.scenario_id
        logger = logging.getLogger(f"{service}_logger_scenario_{scenario_id}")

        def inner(*args: Any, **kwargs: Any) -> Union[Any, None]:
            try:
                result = func(*args, **kwargs)
            except Exception as error:
                message = str(error) + ":-" + traceback.format_exc()
                logger.error(LogMessages(scenario_id).error_message(message))
                self.save_and_close_logger()
                raise Exception from error

            return result

        return inner


class BuildLogStructure:
    def __init__(
        self,
        service: str,
        scenario_id: int,
        auth_headers: Union[Dict[str, str], None] = None,
        data_endpoint: Client = Client(),
    ) -> None:
        self.service = service
        self.scenario_id = scenario_id
        self.auth_headers = auth_headers
        self.data_endpoint = data_endpoint

    def build_logger(self) -> Tuple[LogManager, LoggerTryCatch]:
        log_manager = LogManager(self.service, self.scenario_id, self.data_endpoint, self.auth_headers)
        log_manager.build_logger()
        logger_name = f"{self.service}_logger_scenario_{self.scenario_id}"
        logger = LoggerTryCatch(logging.getLogger(logger_name))
        return log_manager, logger
