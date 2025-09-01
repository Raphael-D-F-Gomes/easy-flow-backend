from typing import Dict, Tuple, List

from pyomo.core import Var, Objective, ConstraintList

from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.attribute import (
    ConcreteModelAttribute, GFAGeneralParameters, GFAGeneralConstraints
)

from services.run_model.build_opt_model.types.network_optimization_types import Customer, Facility


class ParametersAttribute(GFAGeneralParameters):
    @property
    def number_of_facilities(self) -> int:
        number_of_facilities: int = self.model.number_of_facilities
        return number_of_facilities

    @number_of_facilities.setter
    def number_of_facilities(self, value: int) -> None:
        self.model.number_of_facilities = value


class ConstraintsAttribute(GFAGeneralConstraints):
    @property
    def fixed_number_of_facilities(self) -> ConstraintList:
        return self.model.fixed_number_of_facilities

    @fixed_number_of_facilities.setter
    def fixed_number_of_facilities(self, value: ConstraintList) -> None:
        self.model.fixed_number_of_facilities = value


class SetsAttribute(ConcreteModelAttribute):
    @property
    def customers(self) -> List[Customer]:
        return self.model.customers

    @customers.setter
    def customers(self, value: List[Customer]) -> None:
        self.model.customers = value

    @property
    def included_facilities(self) -> List[Facility]:
        return self.model.included_facilities

    @included_facilities.setter
    def included_facilities(self, value: List[Facility]) -> None:
        self.model.included_facilities = value

    @property
    def candidates(self) -> List[Facility]:
        return self.model.candidates

    @candidates.setter
    def candidates(self, value: List[Facility]) -> None:
        self.model.candidates = value


class VariablesAttribute(ConcreteModelAttribute):
    @property
    def flow_variables(self) -> Dict[Tuple[Facility, Customer], Var]:
        flow_variables: Dict[Tuple[Facility, Customer], Var] = self.model.flow_variables
        return flow_variables

    @flow_variables.setter
    def flow_variables(self, value: Dict[Tuple[Facility, Customer], Var]) -> None:
        self.model.flow_variables = value

    @property
    def open_variables(self) -> Dict[Tuple[Facility], Var]:
        open_variables: Dict[Tuple[Facility], Var] = self.model.open_variables
        return open_variables

    @open_variables.setter
    def open_variables(self, value: Dict[Tuple[Facility], Var]) -> None:
        self.model.open_variables = value


class ObjectivesAttribute(ConcreteModelAttribute):
    @property
    def total_weighted_distance(self) -> Objective:
        objective: Objective = self.model.total_weighted_distance
        return objective

    @total_weighted_distance.setter
    def total_weighted_distance(self, value: Objective) -> None:
        self.model.total_weighted_distance = value
