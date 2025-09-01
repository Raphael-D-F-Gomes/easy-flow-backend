from typing import List, Dict, Tuple
from pyomo.core.base.constraint import Constraint
from pyomo.core.base.expression import Expression
from pyomo.core.base.var import Var
from pyomo.core.util import quicksum, prod


class Constraints:
    @staticmethod
    def set_fixed_number_of_facilities(
        opening_variable: Dict[str, Var], considering_candidates_sites: List[str], number_of_facilities: int
    ) -> Constraint:
        p_median_constraint = Constraint(
            rule=sum(opening_variable[j] for j in considering_candidates_sites) == number_of_facilities
        )
        return p_median_constraint

    @staticmethod
    def set_linking_constraint(
        gfa_flow_variables: Dict[Tuple[str, str], Var],
        opening_variable: Dict[str, Var],
        demand_sites: List[str],
        candidate_sites: List[str],
    ) -> List[Expression]:
        linking = []
        for customer in demand_sites:
            for candidate in candidate_sites:
                flow_variable: Var = gfa_flow_variables[candidate, customer]
                opening: Var = opening_variable[candidate]
                expression: Expression = flow_variable - opening <= 0
                linking.append(expression)
        return linking

    @staticmethod
    def set_single_sourcing(
        gfa_flow_variables: Dict[Tuple[str, str], Var], demand_sites: List[str], candidate_sites: List[str]
    ) -> List[Expression]:
        single_sourcing = []
        for customer in demand_sites:
            expression: Expression = quicksum(
                gfa_flow_variables[candidate, customer] for candidate in candidate_sites
            ) - 1 == 0
            single_sourcing.append(expression)
        return single_sourcing

    @staticmethod
    def set_forced_candidates(
        opening_variable: Dict[str, Var], candidate_sites: List[str], considering_sites: List[str]
    ) -> List[Expression]:
        fixed_include_sites = []
        for candidate in candidate_sites:
            if candidate not in considering_sites:
                expression: Expression = quicksum([opening_variable[candidate], -1]) == 0
                fixed_include_sites.append(expression)
        return fixed_include_sites

    @staticmethod
    def set_service_distance(
        gfa_flow_var: Dict[Tuple[str, str], Var],
        service_distance: Dict[str, Dict[Tuple[str, str], int]],
        distance_demand_percentage: Dict[str, float],
        demand: Dict[str, float],
    ) -> List[Expression]:
        constraints = []
        total_demand = sum(demand.values())
        for distance, demand_percentage in distance_demand_percentage.items():
            distance_restrictions = service_distance[distance]
            lhs = quicksum(
                prod([
                    gfa_flow_var[origin, dest],
                    demand[dest],
                    activation,
                ])
                for (origin, dest), activation in distance_restrictions.items()
            )

            rhs = demand_percentage * total_demand
            expression: Expression = lhs >= rhs
            if not isinstance(expression, bool):
                constraints.append(expression)
        return constraints
