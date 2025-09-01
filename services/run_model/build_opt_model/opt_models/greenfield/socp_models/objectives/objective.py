from typing import Dict, Tuple
from cvxpy import Variable, Minimize, sum, prod, norm
import numpy as np

from services.run_model.build_opt_model.types.network_optimization_types import (
    Customer, Facility, Demand, Latitude, Longitude, Var_Latitude, Var_Longitude
)


class Objectives:
    @staticmethod
    def total_weighted_distance(
        gfa_flow_variables: Dict[Tuple[Facility, Customer], Variable],
        customers_geolocation: Dict[Customer, Tuple[Latitude, Longitude]],
        customers_demand: Dict[Customer, Demand],
        candidates: Dict[Facility, Tuple[Var_Latitude, Var_Longitude]],
    ) -> Minimize:
        obj = Minimize(
            sum(
                prod([
                    norm(np.array(candidate_geolocation) - np.array(customers_geolocation[customer])),
                    demand,
                    gfa_flow_variables[candidate, customer]
                ])
                for customer, demand in customers_demand.items()
                for candidate, candidate_geolocation in candidates.items()
            )
        )
        return obj
