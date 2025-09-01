from types import MethodType
from typing import Callable, Any

import traceback

from shared.logs.thread_logger import ThreadLogger, ThreadModelLogger, ThreadProjectLogger


def thread_log_decorator_function(function_name: str, declare_result: bool = False) -> Callable:
    def first_inner(func: MethodType) -> Callable:
        def inner(*args, **kwargs) -> Any:
            thread_logger = ThreadLogger()
            thread_logger.info(f"Start {function_name}")
            try:
                result = func(*args, **kwargs)
                thread_logger.log_result(result, declare_result, function_name)
                thread_logger.info(f"End {function_name}")
                return result
            except Exception as error:
                message = str(error) + ":-" + traceback.format_exc()
                thread_logger.error(message)
                raise Exception(error) from error

        return inner

    return first_inner


def thread_model_log_decorator_function(function_name: Any, declare_result: bool = False) -> Callable:
    def first_inner(func: MethodType) -> Callable:
        def inner(*args, **kwargs) -> Any:
            thread_logger = ThreadModelLogger()
            if callable(function_name):
                message = function_name(*args)
            else:
                message = function_name
            thread_logger.info(f"Start {message}")
            try:
                result = func(*args, **kwargs)
                thread_logger.log_result(result, declare_result, function_name)
                thread_logger.info(f"End {message}")
                return result
            except Exception as error:
                message = str(error) + ":-" + traceback.format_exc()
                thread_logger.error(message)
                raise Exception(error) from error

        return inner

    return first_inner


def thread_project_log_decorator_function(function_name: Any, declare_result: bool = False) -> Callable:
    def first_inner(func: MethodType) -> Callable:
        def inner(*args, **kwargs) -> Any:
            thread_logger = ThreadProjectLogger()
            if callable(function_name):
                message = function_name(*args)
            else:
                message = function_name
            thread_logger.info(f"Start {message}")
            try:
                result = func(*args, **kwargs)
                thread_logger.log_result(result, declare_result, function_name)
                thread_logger.info(f"End {message}")
                return result
            except Exception as error:
                message = str(error) + ":-" + traceback.format_exc()
                thread_logger.error(message)
                raise Exception(error) from error

        return inner

    return first_inner
