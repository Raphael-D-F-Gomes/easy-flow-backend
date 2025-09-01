from typing import Any, Dict, Tuple

import os
import tempfile

from pyomo.core.base import Binary, NonNegativeReals
from pyomo.core.base.var import Var
from pyomo.core.base.constraint import ConstraintList

from optimization_construction_api.opt_construction_function_names import OptConstructionFunctionName
from optimization_construction_api.etl.user_input import NetworkOptimizationUserInput

from optimization_construction_api.etl.mathematical_models.network_optimization.model.model import (
    NetworkOptimizationModel,
)
from optimization_construction_api.etl.mathematical_models.network_optimization.class_parameters import (
    OptimizedVariables,
)
from optimization_construction_api.etl.mathematical_models.network_optimization.objectives.objectives import Objectives
from optimization_construction_api.etl.mathematical_models.network_optimization.constraints import (
    ModelConstraints, UserDefinedConstraints
)


from shared.logs.decorator import thread_log_decorator_function
from shared.utils.optimized_dictionary import optimize_data


class NetworkOptimizationBuilder:
    def __init__(self) -> None:
        self.repr_name = "network optimization"
        self.name = "network_optimization"
        self.model = NetworkOptimizationModel(self.name)

    def __repr__(self) -> str:
        return self.repr_name

    @thread_log_decorator_function(OptConstructionFunctionName().write_model_to_file)
    def write_model_to_file(self, model: NetworkOptimizationModel) -> str:
        name = self.name + ".mps"
        file_path = os.path.join(tempfile.mkdtemp(), name)
        model.write_mps(file_path, io_options={"labeler": AsIsLabeler()})
        return file_path

    def build_model(self, user_input: NetworkOptimizationUserInput) -> str:
        concrete_model = self.create_milp_model(user_input)
        path = self.write_model_to_file(concrete_model)
        return str(path)

    def create_milp_model(self, data: NetworkOptimizationUserInput) -> NetworkOptimizationModel:
        """Parameters must be set before sets"""
        model = self.model
        model.set_parameters(data)
        model.set_sets(data)
        self.declare_variables(model)
        self.build_problem(model)
        return model

    @staticmethod
    @thread_log_decorator_function(OptConstructionFunctionName().declare_variables)
    def declare_variables(model: NetworkOptimizationModel) -> None:
        model.var.flow_variables = Var(list(model.param.flows_cost), domain=NonNegativeReals)
        model.var.open_variables = Var(list(model.param.step_info_sites), domain=Binary)
        model.var.prod_bin_var = Var(list(model.param.production_step_info), domain=Binary)
        model.var.origin_total_production = Var(model.set.production_sites_with_bom, domain=NonNegativeReals)
        model.var.defined_expressions = Var(list(model.set.defined_expression_names), domain=NonNegativeReals)
        model.var.exp_constraints_cond_min_variable = Var(
            list(model.set.cond_min_expression_constraints), domain=Binary
        )

    def build_problem(self, model: NetworkOptimizationModel) -> None:

        flow_variables = optimize_data(model.var.flow_variables)
        open_variables = optimize_data(model.var.open_variables)
        production_variables = optimize_data(model.var.origin_total_production)
        production_binary_variables = optimize_data(model.var.prod_bin_var)

        optimized_variables = OptimizedVariables(
            flow_variables=flow_variables,
            total_production=production_variables,
            production_binary_variables=production_binary_variables,
            open_variables=open_variables,
        )

        self.set_objective(model, optimized_variables)
        self.set_constraints(model, optimized_variables)

    @staticmethod
    @thread_log_decorator_function(OptConstructionFunctionName().set_objective)
    def set_objective(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> None:

        model.obj.minimize_total_cost = Objectives.minimize_total_cost(
            model,
            optimized_variables,
        )

    @staticmethod
    def set_constraints(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
    ) -> None:
        insert_maximum_capacity_constraint(model, optimized_variables)
        insert_production_maximum_capacity_constraint(model, optimized_variables)
        insert_production_binary_variables(model, optimized_variables)
        insert_compare_flow_with_demand_constraint(model, optimized_variables)
        insert_flow_limitation_constraint(model, optimized_variables)
        insert_fixed_include_sites_constraint(model, optimized_variables)
        insert_set_considered_sites_constraint(model, optimized_variables)
        insert_flow_conservation_constraint(model, optimized_variables)
        flow_constraints_cond_min_info = insert_flow_constraints(
            model, optimized_variables
        )
        production_constraints_cond_min_info = insert_production_constraints(
            model, optimized_variables
        )
        insert_conditional_minimum_flow_constraints(model, flow_constraints_cond_min_info)
        insert_conditional_minimum_production_constraints(model, production_constraints_cond_min_info)
        insert_site_constraints(
            model, optimized_variables
        )
        insert_expression_constraints(model)
        insert_site_opening_propagation_constraint(model, optimized_variables)


def insert_conditional_minimum_flow_constraints(
    model: NetworkOptimizationModel,
    cond_min_info: Dict[Tuple[str, int], Dict[str, Any]],
) -> None:

    model.var.flow_constraints_cond_min_variable = Var(list(cond_min_info), domain=Binary)
    constraints_expressions = UserDefinedConstraints.cond_min_flow_constraint(
        cond_min_info, model.var.flow_constraints_cond_min_variable, model.param.big_m
    )
    for expression in constraints_expressions:
        model.const.flow_constraint.add(expression)


def insert_conditional_minimum_production_constraints(
    model: NetworkOptimizationModel,
    cond_min_info: Dict[Tuple[str, int], Dict[str, Any]],
) -> None:

    model.var.production_constraints_cond_min_variable = Var(list(cond_min_info), domain=Binary)
    constraints_expressions = UserDefinedConstraints.cond_min_production_constraint(
        cond_min_info, model.var.production_constraints_cond_min_variable, model.param.big_m
    )
    for expression in constraints_expressions:
        model.const.production_constraint.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_maximum_capacity_constraint)
def insert_maximum_capacity_constraint(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.site_maximum_capacity_constraint = ConstraintList()
    constraints_expressions = ModelConstraints.site_maximum_capacity_constraint(
        model, optimized_variables)
    for expression in constraints_expressions:
        model.const.site_maximum_capacity_constraint.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_production_maximum_capacity_constraint)
def insert_production_maximum_capacity_constraint(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.production_maximum_capacity_constraint = ConstraintList()
    constraints_expressions = ModelConstraints.production_maximum_capacity_constraint(
        model,
        optimized_variables,
    )
    for expression in constraints_expressions:
        model.const.production_maximum_capacity_constraint.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_production_binary_variables)
def insert_production_binary_variables(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.set_production_binary_variables = ConstraintList()
    constraints_expressions = ModelConstraints.set_production_binary_variables(
        optimized_variables,
        model.param.big_m,
    )
    for expression in constraints_expressions:
        model.const.set_production_binary_variables.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_compare_flow_with_demand_constraint)
def insert_compare_flow_with_demand_constraint(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.compare_flow_with_demand_constraint = ConstraintList()
    constraints_expressions = ModelConstraints.compare_flow_with_demand_constraint(model, optimized_variables)
    for expression in constraints_expressions:
        model.const.compare_flow_with_demand_constraint.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_flow_limitation_constraint)
def insert_flow_limitation_constraint(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.flow_limitation_constraint = ConstraintList()
    constraints_expressions = ModelConstraints.flow_limitation_constraint(model, optimized_variables)
    for expression in constraints_expressions:
        model.const.flow_limitation_constraint.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_fixed_include_sites_constraint)
def insert_fixed_include_sites_constraint(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.fixed_include_sites = ConstraintList()
    constraints_expressions = ModelConstraints.fixed_include_sites(model, optimized_variables)
    for expression in constraints_expressions:
        model.const.fixed_include_sites.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_considered_sites_constraint)
def insert_set_considered_sites_constraint(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.set_considered_sites = ConstraintList()
    constraints_expressions = ModelConstraints.set_considered_sites(model, optimized_variables)
    for expression in constraints_expressions:
        model.const.set_considered_sites.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_flow_conservation_constraint)
def insert_flow_conservation_constraint(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.flow_conservation_constraint = ConstraintList()
    constraints_expressions = ModelConstraints.flow_conservation_constraint(model, optimized_variables)
    for expression in constraints_expressions:
        model.const.flow_conservation_constraint.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_site_constraints)
def insert_site_constraints(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.site_constraint = ConstraintList()
    constraints_expressions = UserDefinedConstraints.site_constraints(model, optimized_variables)
    for expression in constraints_expressions:
        model.const.site_constraint.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_flow_constraints)
def insert_flow_constraints(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> Dict[Tuple[str, int], Dict[str, Any]]:
    model.const.flow_constraint = ConstraintList()
    constraints_expressions, cond_min_info = UserDefinedConstraints.flow_constraints(
        model, optimized_variables
    )
    for expression in constraints_expressions:
        model.const.flow_constraint.add(expression)

    return cond_min_info


@thread_log_decorator_function(OptConstructionFunctionName().set_production_constraints)
def insert_production_constraints(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> Dict[Tuple[str, int], Dict[str, Any]]:
    model.const.production_constraint = ConstraintList()
    constraints_expressions, cond_min_info = UserDefinedConstraints.production_constraints(
        model, optimized_variables
    )
    for expression in constraints_expressions:
        model.const.production_constraint.add(expression)

    return cond_min_info


@thread_log_decorator_function(OptConstructionFunctionName().set_expression_constraints)
def insert_expression_constraints(
        model: NetworkOptimizationModel,
) -> None:
    model.const.expression_constraint = ConstraintList()
    constraints_expressions = UserDefinedConstraints.expression_constraints(model)
    for expression in constraints_expressions:
        model.const.expression_constraint.add(expression)


@thread_log_decorator_function(OptConstructionFunctionName().set_site_opening_propagation)
def insert_site_opening_propagation_constraint(
        model: NetworkOptimizationModel,
        optimized_variables: OptimizedVariables,
) -> None:
    model.const.site_opening_propagation = ConstraintList()
    constraints_expressions = UserDefinedConstraints.site_opening_propagation(model, optimized_variables)
    for expression in constraints_expressions:
        model.const.site_opening_propagation.add(expression)


class AsIsLabeler:
    def __call__(self, obj: Any) -> str:
        name: str = obj.getname(True)
        return name
