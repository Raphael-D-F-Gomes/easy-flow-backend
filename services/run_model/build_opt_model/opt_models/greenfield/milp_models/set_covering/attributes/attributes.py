from typing import Dict, Tuple, List

from pyomo.core import Var, Objective, ConstraintList

from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.attribute import (
    ConcreteModelAttribute, GFAGeneralParameters, GFAGeneralConstraints, GFAGeneralSets
)

from services.run_model.build_opt_model.types.network_optimization_types import Customer, Facility


class SetCoveringParameters(GFAGeneralParameters):
    @property
    def serv_distance(self) -> Dict[float, Dict[Tuple[str, str], float]]:
        service_distance: Dict[float, Dict[Tuple[str, str], float]] = self.model.param_serv_distance
        return service_distance

    @serv_distance.setter
    def serv_distance(self, value: Dict[float, Dict[Tuple[str, str], float]]) -> None:
        self.model.param_serv_distance = value

    @property
    def demand_share_per_distance(self) -> Dict[float, float]:
        demand_share_per_distance: Dict[float, float] = self.model.demand_share_per_distance
        return demand_share_per_distance

    @demand_share_per_distance.setter
    def demand_share_per_distance(self, value: Dict[float, float]) -> None:
        self.model.demand_share_per_distance = value


class ConstraintsAttribute(GFAGeneralConstraints):
    @property
    def limit_flow_volume_by_service_distances(self) -> ConstraintList:
        return self.model.serv_distance

    @limit_flow_volume_by_service_distances.setter
    def limit_flow_volume_by_service_distances(self, value: ConstraintList) -> None:
        self.model.serv_distance = value


class ObjectivesAttribute(ConcreteModelAttribute):
    @property
    def minimize_total_number_of_facilities_and_total_weighted_distance(self) -> Objective:
        objective: Objective = self.model.minimize_total_number_of_facilities_and_total_weighted_distance
        return objective

    @minimize_total_number_of_facilities_and_total_weighted_distance.setter
    def minimize_total_number_of_facilities_and_total_weighted_distance(self, value: Objective) -> None:
        self.model.minimize_total_number_of_facilities_and_total_weighted_distance = value

    @property
    def minimize_total_number_of_facilities(self) -> Objective:
        objective: Objective = self.model.minimize_total_number_of_facilities
        return objective

    @minimize_total_number_of_facilities.setter
    def minimize_total_number_of_facilities(self, value: Objective) -> None:
        self.model.minimize_total_number_of_facilities = value
