from typing import Dict, Tuple, List
from pyomo.core.base import objective
from pyomo.core.base import minimize
from pyomo.core.base.var import Var
from pyomo.core.util import prod, quicksum


class Objectives:
    @staticmethod
    def total_weighted_distance(
        gfa_flow_variables: Dict[Tuple[str, str], Var],
        distances: Dict[Tuple[str, str], float],
        customers_with_demand: Dict[str, float],
        candidates: List[str],
    ) -> objective.Objective:
        obj = objective.Objective(
            expr=quicksum(
                prod([
                    distances.get((candidate, customer), distances.get((customer, candidate), None)),
                    customers_with_demand[customer],
                    gfa_flow_variables[candidate, customer]
                ])
                for customer in customers_with_demand for candidate in candidates
            ),
            sense=minimize,
        )
        return obj

    @staticmethod
    def total_number_of_facilities_and_total_weighted_distance(
            gfa_flow_variables: Dict[Tuple[str, str], Var],
            distances: Dict[Tuple[str, str], float],
            customers_with_demand: Dict[str, float],
            candidates: List[str],
            opening_variable: Dict[str, Var],
            total_facilities_weight: float,
    ) -> objective.Objective:

        total_weighted_distances = quicksum(
                prod([
                    distances.get((candidate, customer), distances.get((customer, candidate), None)),
                    customers_with_demand[customer],
                    gfa_flow_variables[candidate, customer]
                ])
                for customer in customers_with_demand for candidate in candidates
            )

        total_number_of_facilities = quicksum(opening_variable.values())

        obj = objective.Objective(
            expr=prod([total_number_of_facilities, total_facilities_weight * 0.1]) + total_weighted_distances,
            sense=minimize,
        )
        return obj
