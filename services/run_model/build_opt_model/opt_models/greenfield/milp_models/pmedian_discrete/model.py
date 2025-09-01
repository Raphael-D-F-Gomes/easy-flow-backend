from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.model import MILPModel
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.attributes import (
    PMedianDiscreteAttributePool,
)
from services.common.user_input import GreenfieldUserInput

from pyomo.environ import SolverFactory

SolverFactory()


class PMedianDiscreteModel(MILPModel):
    def __init__(self, name: str) -> None:
        attribute_pool = PMedianDiscreteAttributePool()
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
        self.param.number_of_facilities = data.get_number_of_facilities()
