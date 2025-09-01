from typing import Tuple

import os

from shared.logs.thread_logger import ThreadLogger, ThreadModelLogger, ThreadProjectLogger
from shared.api.api import Client, CustomResponse

from data_store_endpoints import API_SAVE_LOG, API_SAVE_MODEL_LOG, API_SAVE_PROJECT_LOG


def save_and_close_logger(
    auth_headers: dict, client: Client, service_name: str, scenario_id: int
) -> Tuple[CustomResponse, int]:
    thread_logger = ThreadLogger(scenario_id, service_name)
    log_path = thread_logger.get_logger_file_handler_path()
    log_exists = os.path.exists(log_path)
    # Todo Log must exist
    if log_exists:
        with open(log_path, "r") as file:
            log_content = file.read()
    else:
        log_content = f"Service {service_name}, ScenarioID {scenario_id} didn't" f"produce logs"

    response = client.post(
        API_SAVE_LOG,
        timeout=120,
        json={"scenario-id": scenario_id, "log-content": log_content, "service-name": service_name},
        headers=auth_headers,
    )
    root_logger = thread_logger.logger
    root_logger.handlers = []
    if log_exists:
        try:
            os.remove(log_path)
        except PermissionError as error:
            print(error)

    return response, response.status_code


def save_and_close_model_logger(
        auth_headers: dict,
        client: Client,
        model_id: int,
) -> Tuple[CustomResponse, int]:
    thread_logger = ThreadModelLogger()
    log_path = thread_logger.get_logger_file_handler_path()
    log_exists = os.path.exists(log_path)

    if log_exists:
        with open(log_path, "r") as file:
            log_content = file.read()
    else:
        log_content = f"There is no logs"

    response = client.post(
        API_SAVE_MODEL_LOG,
        timeout=120,
        json={"model-id": model_id, "log-content": log_content},
        headers=auth_headers,
    )
    root_logger = thread_logger.logger
    root_logger.handlers = []
    if log_exists:
        try:
            os.remove(log_path)
        except PermissionError as error:
            print(error)

    return response, response.status_code


def save_and_close_project_logger(
        auth_headers: dict,
        client: Client,
        project_id: int,
) -> Tuple[CustomResponse, int]:
    thread_logger = ThreadProjectLogger()
    log_path = thread_logger.get_logger_file_handler_path()
    log_exists = os.path.exists(log_path)

    if log_exists:
        with open(log_path, "r") as file:
            log_content = file.read()
    else:
        log_content = f"There is no logs"

    response = client.post(
        API_SAVE_PROJECT_LOG,
        timeout=120,
        json={"project-id": project_id, "log-content": log_content},
        headers=auth_headers,
    )
    root_logger = thread_logger.logger
    root_logger.handlers = []
    if log_exists:
        try:
            os.remove(log_path)
        except PermissionError as error:
            print(error)

    return response, response.status_code
