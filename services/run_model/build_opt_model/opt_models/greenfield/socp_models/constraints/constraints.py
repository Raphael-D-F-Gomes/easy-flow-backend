from typing import List, Dict, Tuple, Set
from cvxpy import Variable

from services.run_model.build_opt_model.types.network_optimization_types import (
    Customer, Facility, N_Facilities
)


class Constraints:
    @staticmethod
    def set_fixed_number_of_facilities(
            opening_variable: Dict[Facility, Variable],
            candidates: Set[Facility],
            number_of_new_facilities: N_Facilities
    ) -> List[bool]:
        p_median_constraint = [
            (sum(opening_variable[facility] for facility in candidates) == number_of_new_facilities)
        ]

        return p_median_constraint

    @staticmethod
    def set_linking_constraint(
        gfa_flow_variables: Dict[Tuple[Facility, Customer], Variable],
        opening_variable: Dict[Facility, Variable],
        customers: Set[Customer],
        candidates: Set[Facility],
    ) -> List[bool]:
        """
        The facility must be open to be able to fulfill a customer
        """
        linking = []
        for customer in customers:
            for candidate in candidates:
                flow_variable: Variable = gfa_flow_variables[candidate, customer]
                opening: Variable = opening_variable[candidate]
                expression = flow_variable - opening <= 0
                linking.append(expression)
        return linking

    @staticmethod
    def set_single_sourcing(
            gfa_flow_variables: Dict[Tuple[Facility, Customer], Variable],
            customers: set[Customer],
            candidates: set[Facility],
    ) -> List[bool]:
        single_sourcing = []
        for customer in customers:
            expression = sum(
                gfa_flow_variables[candidate, customer] for candidate in candidates
            ) - 1 == 0
            single_sourcing.append(expression)
        return single_sourcing
