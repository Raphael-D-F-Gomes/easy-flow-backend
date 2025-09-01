from typing import Tuple, Dict

import os
import tempfile
import json

import time

import cvxpy as cvx
import numpy as np

from solver_broker_api.solver_function_names import SolverFunctionName
from solver_broker_api.solvers.abstract_solver import AbsSolver
from solver_broker_api.solvers.result_writer import ResultWriter

from shared.solver_output import SolverResultsNames, SolverGeneralResults
from shared.logs.decorator import thread_log_decorator_function
from solver_broker_api.configuration.configuration import CONFIGURATION_MAX_NUMBER_ITERATIONS_SOCP


class SOCPWriter(ResultWriter):
    @staticmethod
    def build_variable_results(latitude: float, longitude: float, optimal_value: float) -> Dict[str, Dict[str, float]]:
        return {
            SolverResultsNames.center: {SolverResultsNames.latitude: latitude, SolverResultsNames.longitude: longitude},
            SolverResultsNames.obj_function_value: optimal_value,
        }


class SOCPSolver(AbsSolver):
    """
    Second-Order Cone Programming
    """

    def __init__(self) -> None:
        super(SOCPSolver, self).__init__(SOCPWriter())

    def __repr__(self):
        return SolverFunctionName().socp_solver

    @staticmethod
    @thread_log_decorator_function(function_name=SolverFunctionName().optimize)
    def optimize(coordinates: np.array, weights: np.array) -> Tuple[float, np.array]:
        c_pt = cvx.Variable(2)

        balanced_weights = weights / weights.sum()

        weighted_distance = [cvx.norm(c_pt - coordinates[i, :]) * balanced_weights[i] for i in range(weights.shape[0])]
        objective = cvx.Minimize(cvx.sum(weighted_distance))
        problem = cvx.Problem(objective)
        optimal_value = problem.solve(solver=cvx.ECOS, max_iters=CONFIGURATION_MAX_NUMBER_ITERATIONS_SOCP)
        center = c_pt.value

        return optimal_value, center

    @staticmethod
    def get_coordinates_from_model_data(model_data: dict) -> np.array:
        data_points = model_data["model-data"]
        coordinates = []
        for point in data_points:
            coordinates.append([point["latitude"], point["longitude"]])
        return np.array(coordinates)

    @staticmethod
    def get_weights_from_model_data(model_data: dict) -> np.array:

        data_points = model_data["model-data"]
        weights = []
        for point in data_points:
            weights.append(point["volume"])
        return np.array(weights)

    @thread_log_decorator_function(function_name=SolverFunctionName().reading_input_model_file)
    def get_input_from_model_file(self, model_path: str) -> Tuple[np.array, np.array]:
        with open(model_path, "r", encoding="utf-8") as file:
            model_data = json.load(file)
        coordinates = self.get_coordinates_from_model_data(model_data)
        weights = self.get_weights_from_model_data(model_data)
        return coordinates, weights

    @thread_log_decorator_function(function_name=SolverFunctionName().saving_output)
    def save_output(self, center: np.array, opt_time: float, optimal_value: float) -> str:
        result_path = os.path.join(tempfile.mkdtemp(), "result.json")
        result = self.result_writer.build_variable_results(center[0], center[1], optimal_value)
        stats = self.result_writer.build_stats(opt_time)
        general_results_input = {SolverGeneralResults.gap: np.nan,
                                 SolverGeneralResults.primalbound: np.nan,
                                 SolverGeneralResults.dualbound: np.nan}
        general_results = self.result_writer.build_general_results(general_results_input)
        output = result.copy()
        for key in stats:
            output[key] = stats[key]
        for key_results in general_results:
            output[key_results] = general_results[key_results]

        with open(result_path, "w", encoding="utf-8") as file:
            json.dump(output, file)
        return result_path

    @thread_log_decorator_function(function_name=SolverFunctionName.solve)
    def solve(self, model_path: str, scenario_id: int = 0) -> str:
        coordinates, weights = self.get_input_from_model_file(model_path)
        start = time.time()
        optimal_value, center = self.optimize(coordinates, weights)
        opt_time = time.time() - start
        result_path = self.save_output(center, opt_time, optimal_value)
        return result_path
