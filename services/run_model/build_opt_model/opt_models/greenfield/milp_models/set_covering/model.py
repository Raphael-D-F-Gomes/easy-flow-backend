import numpy as np

from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.model import MILPModel
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.set_covering.attributes.pool import (
    SetCoveringAttributePool,
)
from services.common.user_input import GreenfieldUserInput

from pyomo.environ import SolverFactory

SolverFactory()


class SetCoveringModel(MILPModel):
    def __init__(self, name: str) -> None:
        attribute_pool = SetCoveringAttributePool()
        self.set = attribute_pool.set_attr(self)
        self.param = attribute_pool.param_attr(self)
        self.var = attribute_pool.var_attr(self)
        self.obj = attribute_pool.obj_attr(self)
        self.const = attribute_pool.const_attr(self)
        super().__init__(name)

    def set_sets(self, data: GreenfieldUserInput) -> None:
        self.set.customers = data.get_customers()
        self.set.included_facilities = data.get_included_facilities()
        self.set.candidates = data.get_considering_candidates()

    def set_parameters(self, data: GreenfieldUserInput) -> None:
        self.param.distances = data.get_flow_distances()
        self.param.demand = data.get_demand()
        self.param.demand_share_per_distance = data.get_demand_percentage_per_distance_level()
        self.param.serv_distance = data.get()
        self.param.total_number_of_facilities_weight = (np.mean(list(self.param.distances.values())) *
                                                        np.sum(list(self.param.demand.values())))
