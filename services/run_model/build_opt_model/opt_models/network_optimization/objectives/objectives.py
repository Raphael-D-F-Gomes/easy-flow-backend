from typing import Any, Dict, Tuple

import pandas as pd
from pyomo.core.base import objective
from pyomo.core.base import minimize, Expression
from pyomo.core.base.var import Var
from pyomo.core.util import prod, quicksum

from optimization_construction_api.etl.mathematical_models.network_optimization.model.model import (
    NetworkOptimizationModel,
)
from optimization_construction_api.etl.mathematical_models.network_optimization.class_parameters import (
   OptimizedVariables
)
from optimization_construction_api.etl.types import (
    Product,
    Period,
    Origin,
    Ratio,
    ExpressionName,
    Destination,
    Mode,
    Step,
    StepID,
)

from shared.tables.network_optimization_name_registry import StepCostSheet
from shared.utils.optimized_dictionary import OptimizedDict


class Objectives:
    @staticmethod
    def minimize_total_cost(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> objective.Objective:

        outbound_total_cost = get_outbound_total_cost(model.param.outbound_cost, optimized_variables.flow_variables)
        production_variable_total_cost = get_production_variable_total_cost(
            model.param.production_variable_cost,
            optimized_variables.total_production,
        )
        variable_total_cost = get_variable_total_cost(
            model.param.sites_variable_cost, optimized_variables.flow_variables, model.param.variable_cost_unit_config
        )
        expressions_total_cost = get_expression_based_costs(
            model.param.expression_based_costs,
            model.var.defined_expressions
        )

        transportation_cost = get_transportation_cost(optimized_variables.flow_variables, model.param.flows_cost)
        sites_fixed_cost = get_sites_fixed_cost(optimized_variables.open_variables, model.param.step_info_sites)
        production_fixed_cost = get_production_fixed_cost(
            optimized_variables.production_binary_variables,
            model.param.production_step_info,
        )

        total_cost: Expression = quicksum(
            [
                transportation_cost,
                sites_fixed_cost,
                outbound_total_cost,
                variable_total_cost,
                expressions_total_cost,
                production_variable_total_cost,
                production_fixed_cost,
            ]
        )

        obj = objective.Objective(expr=total_cost, sense=minimize)

        return obj


def get_transportation_cost(
    flows: Dict[Tuple[Period, Origin, Destination, Mode, Product], Var],
    flows_cost: Dict[Tuple[Period, Origin, Destination, Mode, Product], float],
) -> Any:
    transportation_cost = quicksum(prod([flows[flow], flows_cost[flow]]) for flow in flows.keys())
    return transportation_cost


def get_sites_fixed_cost(
    open_variables: Dict[Tuple[Period, Origin, StepID, Step], Var],
    step_info_site: Dict[Tuple[Period, Origin, StepID, Step], Dict[str, float]],
) -> Any:
    sites_fixed_cost = quicksum(
        prod([open_variables[site], step_info_site[site][StepCostSheet.cost]]) for site in open_variables
        if pd.notna(step_info_site[site][StepCostSheet.cost])
    )
    return sites_fixed_cost


def get_production_fixed_cost(
    production_binary_variables: Dict[Tuple[Period, Origin, Product, StepID, Step], Var],
    step_info_production: Dict[Tuple[Period, Origin, Product, StepID, Step], Dict[str, float]],
) -> Any:
    production_fixed_cost = quicksum(
        prod(
            [
                production_binary_variables[production_indexes],
                step_info_production[production_indexes][StepCostSheet.cost]
            ]
        )
        for production_indexes in production_binary_variables
        if pd.notna(step_info_production[production_indexes][StepCostSheet.cost])
    )
    return production_fixed_cost


def get_outbound_total_cost(
    outbound_cost: Dict[Tuple[Origin, Product], float],
    flow_variables: OptimizedDict,
) -> Any:

    outbound_total_cost = 0.0
    if outbound_cost:
        outbound_total_cost = quicksum(
            prod([quicksum(flow_variables[:, indexes[0], :, :, indexes[1]].values()), cost])
            for indexes, cost in outbound_cost.items()
        )

    return outbound_total_cost


def get_production_variable_total_cost(
    variable_cost: Dict[Tuple[Period, Origin, Product], float],
    production_variables: OptimizedDict,
) -> Any:

    production_total_cost = 0.0
    if variable_cost:
        production_total_cost = quicksum(
            prod([production_variables[indexes], cost])
            for indexes, cost in variable_cost.items()
        )

    return production_total_cost


def get_variable_total_cost(
    variable_cost: Dict[Tuple[Period, Origin], float],
    flow_variables: OptimizedDict,
    ratio_by_product: Dict[Origin, Dict[Product, Ratio]],
) -> Any:

    products = set(product for _, _, _, _, product in flow_variables)
    variable_cost_expr = []
    variable_total_cost = 0.0
    if variable_cost:
        for indexes, cost in variable_cost.items():
            period, origin = indexes
            ratio = ratio_by_product.get(origin, {})
            variable_cost_expr += [
                quicksum(
                    prod(
                        [
                            quicksum(list(flow_variables[period, origin, :, :, product].values())),
                            float(cost * ratio.get(product, 1)),
                        ]
                    )
                    for product in products
                )
            ]
        variable_total_cost = quicksum(variable_cost_expr)

    return variable_total_cost


def get_expression_based_costs(
    expression_based_costs: Dict[Tuple[str, ExpressionName], float],
    expressions: Dict[ExpressionName, Var],
) -> Any:

    if len(expression_based_costs) == 0:
        return 0.0
    expressions_total_cost = 0.0
    for expression_info, expression_cost in expression_based_costs.items():
        expressions_total_cost += prod([expression_cost, expressions[expression_info[1]]])

    return expressions_total_cost
