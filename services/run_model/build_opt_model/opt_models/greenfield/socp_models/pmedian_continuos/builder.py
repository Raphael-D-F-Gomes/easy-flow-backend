from typing import List

from . import Parameters, Variables

from services.run_model.build_opt_model.opt_models.greenfield.socp_models import Constraints, Objectives
from services.run_model.build_opt_model.user_input.greenfield_user_input import GreenfieldUserInput

from cvxpy import Problem, Variable

from services.run_model.build_opt_model.types.network_optimization_types import (
    Customer, Facility, Var_GeoInfo
)


class PMedianContinuosBuilder:

    def __init__(self, data: GreenfieldUserInput):
        self.data = data
        self.constraints = Constraints()
        self.objectives = Objectives()

    def build_model(self) -> Problem:
        parameters = self.set_parameters()
        constraints = self.set_constraints(parameters)
        pass

    def set_parameters(self) -> Parameters:
        return Parameters(
            number_of_new_facilities=self.data.get_number_of_facilities(),
            demand=self.data.get_demand(),
            facilities_geolocation=self.data.get_included_facilities_with_geolocation(),
            customers_geolocation=self.data.get_customers_with_geolocation(),
        )

    @staticmethod
    def set_variables(parameters: Parameters) -> Variables:
        opening_variables = {
            Facility(f"Candidate_{i+1}"): Variable(1, name=f"Candidate_{i+1}", boolean=True)
            for i in range(parameters.number_of_new_facilities)
        }
        candidates = {candidate: Var_GeoInfo(Variable((1, 2))) for i, candidate in enumerate(opening_variables)}
        gfa_flow_variables = {
            (candidate, customer): Variable(1, boolean=True)
            for i, candidate in enumerate(opening_variables) for customer in parameters.customers_geolocation
        }
        return Variables(opening_variables, gfa_flow_variables, candidates)

    def set_constraints(self, parameters: Parameters, variables: Variables) -> List[bool]:

        customers = set(parameters.customers_geolocation)
        candidates = set(variables.candidates)

        constraint_list = []
        constraint_list += (self.constraints.set_linking_constraint(
            gfa_flow_variables=variables.gfa_flow_variables,
            opening_variable=variables.opening_variable,
            customers=customers,
            candidates=candidates,
        ))
        constraint_list += (self.constraints.set_fixed_number_of_facilities(
            opening_variable=variables.opening_variable,
            candidates=candidates,
            number_of_new_facilities=parameters.number_of_new_facilities,
        ))
        constraint_list += (self.constraints.set_single_sourcing(
            gfa_flow_variables=variables.gfa_flow_variables,
            customers=customers,
            candidates=candidates,
        ))

        return constraint_list

    def
