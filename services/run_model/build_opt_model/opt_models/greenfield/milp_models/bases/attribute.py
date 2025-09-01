from pyomo.core.base.PyomoModel import ConcreteModel
from typing import Dict, Tuple, List
from pyomo.core import Var, Objective, ConstraintList
from services.run_model.build_opt_model.types.network_optimization_types import Customer, Facility


class ConcreteModelAttribute:
    def __init__(self, model: ConcreteModel):
        self.model = model


class GFAGeneralParameters(ConcreteModelAttribute):
    @property
    def distances(self) -> Dict[Dict[Facility, Customer], float]:
        distances: Dict[Dict[Facility, Customer], float] = self.model.distances
        return distances

    @distances.setter
    def distances(self, value: Dict[Dict[Facility, Customer], float]) -> None:
        self.model.distances = value

    @property
    def demand(self) -> Dict[Customer, float]:
        demand: Dict[Customer, float] = self.model.demand
        return demand

    @demand.setter
    def demand(self, value: Dict[Customer, float]) -> None:
        self.model.demand = value


class GFAGeneralConstraints(ConcreteModelAttribute):
    @property
    def fixed_included_sites(self) -> ConstraintList:
        return self.model.fixed_included_sites

    @fixed_included_sites.setter
    def fixed_included_sites(self, value: ConstraintList) -> None:
        self.model.fixed_included_sites = value

    @property
    def limit_flow_from_only_open_facilities(self) -> ConstraintList:
        return self.model.limit_flow_from_only_open_facilities

    @limit_flow_from_only_open_facilities.setter
    def limit_flow_from_only_open_facilities(self, value: ConstraintList) -> None:
        self.model.limit_flow_from_only_open_facilities = value

    @property
    def set_single_sourcing(self) -> ConstraintList:
        return self.model.set_single_sourcing

    @set_single_sourcing.setter
    def set_single_sourcing(self, value: ConstraintList) -> None:
        self.model.set_single_sourcing = value


class GFAGeneralSets(ConcreteModelAttribute):
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


class GFAGeneralVariables(ConcreteModelAttribute):
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
