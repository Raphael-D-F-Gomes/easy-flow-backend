from typing import Dict, Any

from optimization_construction_api.opt_construction_function_names import OptConstructionFunctionName
from optimization_construction_api.etl.mathematical_models.network_optimization.model.attributes.pool import (
    NetworkOptimizationAttributePool,
)
from optimization_construction_api.etl.user_input import NetworkOptimizationUserInput
from optimization_construction_api.etl.model_writer import WriterMPS

from pyomo.core.base.PyomoModel import ConcreteModel
from pyomo.environ import SolverFactory

from shared.logs.decorator import thread_log_decorator_function


SolverFactory()


class NetworkOptimizationModel(ConcreteModel):
    def __init__(self, name: str) -> None:
        attribute_pool = NetworkOptimizationAttributePool()
        self.set = attribute_pool.set_attr(self)
        self.param = attribute_pool.param_attr(self)
        self.var = attribute_pool.var_attr(self)
        self.obj = attribute_pool.obj_attr(self)
        self.const = attribute_pool.const_attr(self)
        super().__init__(name)

    @thread_log_decorator_function(OptConstructionFunctionName().set_sets)
    def set_sets(self, data: NetworkOptimizationUserInput) -> None:
        self.set.origins = data.get_origins()
        self.set.periods = data.get_periods()
        self.set.production_sites_with_bom = data.production.production_policies.get_production_sites_with_bom()
        self.set.production_and_intermediary_nodes = data.get_production_and_intermediary_nodes()
        self.set.flow_constraints = data.constraints.flow_constraints.data
        self.set.production_constraints = data.constraints.production_constraints.data
        self.set.site_constraints = data.constraints.site_constraints.data
        self.set.defined_expression_names = data.constraints.get_defined_constraints()
        self.set.expression_constraints_info = data.constraints.expression_constraints.data
        self.set.cond_min_expression_constraints = data.constraints.get_cond_min_expression_constraints()
        self.set.group_members = data.attributes.group_members.get_members_by_group()

    @thread_log_decorator_function(OptConstructionFunctionName().set_parameters)
    def set_parameters(self, data: NetworkOptimizationUserInput) -> None:
        self.param.destinations_demand = data.policies.get_destinations_demand()
        self.param.flows_cost = data.get_flows_cost()
        self.param.production_step_info = data.get_production_step_info()
        self.param.production_variable_cost = data.production.production_policies.get_production_variable_cost()
        self.param.raw_material_quantity_by_production_policies = data.get_production_policies_by_raw_material()
        self.param.step_info_sites = data.get_sites_step_info()
        self.param.sites_variable_cost = data.get_sites_variable_cost()
        self.param.big_m = data.get_big_m()
        self.param.outbound_cost = data.get_outbound_costs()
        self.param.capacity_unit_config = data.get_ratio_by_origin_by_product_capacity_unit_config()
        self.param.variable_cost_unit_config = data.get_ratio_by_origin_by_product_variable_cost_unit_config()
        self.param.expression_based_costs = data.constraints.expression_based_costs.get_cost_by_expression()

    def write_mps(self, filename: str, io_options: Dict[str, Any]) -> None:
        writer = WriterMPS()
        writer(self, filename, True, io_options)
