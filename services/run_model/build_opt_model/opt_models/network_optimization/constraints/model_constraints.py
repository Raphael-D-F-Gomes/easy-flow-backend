from typing import List, Any, Dict, Tuple, Set
from itertools import product as iter_prod

import pandas as pd
from pyomo.core.util import prod, quicksum
from pyomo.core.base.expression import Expression
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
    Step,
    StepID,
)

from shared.tables.global_options import StatusOptions
from shared.tables.network_optimization_name_registry import StepCostSheet
from shared.utils.optimized_dictionary import OptimizedDict


class ModelConstraints:
    @staticmethod
    def site_maximum_capacity_constraint(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:

        flow_variables = optimized_variables.flow_variables
        step_capacity = model.param.step_info_sites
        open_variables = optimized_variables.open_variables
        ratio_by_origin = model.param.capacity_unit_config
        products = set(product for _, _, _, _, product in flow_variables)

        site_maximum_capacity = []

        for origin, period in iter_prod(list(model.set.origins), model.set.periods):

            max_capacity = get_max_capacity(open_variables, step_capacity, (period, origin), model.param.big_m)

            if isinstance(max_capacity, (int, float)):
                continue

            flows_sum = get_flows_sum(ratio_by_origin, (origin, period), flow_variables, products)

            expression: Expression = flows_sum - max_capacity <= 0
            site_maximum_capacity.append(expression)

        return site_maximum_capacity

    @staticmethod
    def production_maximum_capacity_constraint(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:

        total_production = optimized_variables.total_production
        production_step_info = model.param.production_step_info
        production_binary_variables = optimized_variables.production_binary_variables
        production_maximum_capacity = []

        for period, origin, product in total_production:

            max_capacity = get_production_max_capacity(
                production_binary_variables,
                production_step_info,
                (period, origin, product),
                model.param.big_m,
            )

            if isinstance(max_capacity, (int, float)):
                continue

            expression: Expression = total_production[period, origin, product] - max_capacity <= 0
            production_maximum_capacity.append(expression)

        return production_maximum_capacity

    @staticmethod
    def set_production_binary_variables(
            optimized_variables: OptimizedVariables,
            big_m: float,
    ) -> List[Expression]:
        production_binary_variables = optimized_variables.production_binary_variables
        if len(production_binary_variables) == 0:
            return []
        total_production = optimized_variables.total_production
        set_production_binary_variables = []

        for (period, origin, product), production_var in total_production.items():
            binary_var_filter = production_binary_variables[period, origin, product, :, :]
            if binary_var_filter:
                binary_summation = quicksum(binary_var_filter.values())
                if_production_binary_equals_one: Expression = binary_summation * big_m - production_var >= 0
                if_not_production_binary_equals_zero: Expression = production_var - binary_summation >= 0
                binary_var_sum_less_or_equal_than_one: Expression = binary_summation - 1 <= 0
                set_production_binary_variables.append(if_production_binary_equals_one)
                set_production_binary_variables.append(if_not_production_binary_equals_zero)
                set_production_binary_variables.append(binary_var_sum_less_or_equal_than_one)

        return set_production_binary_variables

    @staticmethod
    def compare_flow_with_demand_constraint(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:
        flow_variables = optimized_variables.flow_variables
        demands = model.param.destinations_demand
        compare_flow_with_demand = []

        for (period, destination, product), demand in demands.items():
            flows_sum = quicksum(flow_variables[period, :, destination, :, product].values())
            expression: Expression = flows_sum - demand == 0
            compare_flow_with_demand.append(expression)

        return compare_flow_with_demand

    @staticmethod
    def flow_limitation_constraint(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:

        flow_variables = optimized_variables.flow_variables
        open_variables = optimized_variables.open_variables
        big_m = model.param.big_m
        flow_limitations = []

        for flow, flow_var in flow_variables.items():
            period = flow[0]
            origin = flow[1]

            expression: Expression = (
                flow_var - prod([big_m, quicksum(open_variables[period, origin, :, :].values())]) <= 0
            )
            flow_limitations.append(expression)

        return flow_limitations

    @staticmethod
    def fixed_include_sites(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:
        origins = model.set.origins
        include = StatusOptions.include
        included_origins = [origin for origin, status in origins.items() if status == include]
        periods = model.set.periods
        open_variables = optimized_variables.open_variables
        fixed_included_sites = []

        for origin, period in iter_prod(included_origins, periods):
            expression: Expression = quicksum(open_variables[period, origin, :, :].values()) - 1 == 0
            fixed_included_sites.append(expression)

        return fixed_included_sites

    @staticmethod
    def set_considered_sites(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:
        origins = model.set.origins
        consider = StatusOptions.consider
        considered_origins = [origin for origin, status in origins.items() if status == consider]
        periods = model.set.periods
        open_variables = optimized_variables.open_variables
        set_considered_sites = []

        for origin, period in iter_prod(considered_origins, periods):
            expression: Expression = quicksum(open_variables[period, origin, :, :].values()) - 1 <= 0
            set_considered_sites.append(expression)

        return set_considered_sites

    @staticmethod
    def flow_conservation_constraint(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:
        flow_variables = optimized_variables.flow_variables
        production_variables = optimized_variables.total_production
        production_and_intermediary_nodes = model.set.production_and_intermediary_nodes
        production_policies_by_raw_material = model.param.raw_material_quantity_by_production_policies
        flow_conservation_constraint = []

        for period, site, product in production_and_intermediary_nodes:

            production_from_product = quicksum(
                prod([production_variables[production_policies], quantity])
                for production_policies, quantity in production_policies_by_raw_material.get(
                    (period, site, product), {}
                ).items()
            )
            inbound_sum = quicksum(flow_variables[period, :, site, :, product].values())
            outbound_sum = quicksum(flow_variables[period, site, :, :, product].values())
            product_production = production_variables.get((period, site, product), 0.0)

            expression: Expression = inbound_sum + product_production - outbound_sum - production_from_product == 0
            flow_conservation_constraint.append(expression)

        return flow_conservation_constraint


def get_flows_sum(
    ratio_by_origin: Dict[Origin, Dict[Product, Ratio]],
    origin_and_period: Tuple[Origin, Period],
    flow_variables: OptimizedDict,
    products: Set[Product],
) -> Any:

    origin, period = origin_and_period
    ratio_by_product = ratio_by_origin.get(origin, {})
    flows_sum = quicksum(
        [
            quicksum(flow_variables[period, origin, :, :, product].values()) * ratio_by_product.get(product, 1)
            for product in products
        ]
    )
    return flows_sum


def get_max_capacity(
    open_variables: OptimizedDict,
    sites_step_info: Dict[Tuple[Period, Origin, StepID, Step], Dict[str, float]],
    period_and_origin: Tuple[Period, Origin],
    big_m: float
) -> Any:
    period, origin = period_and_origin
    open_var_filter = open_variables[period, origin, :, :]
    capacities = []
    variables = []
    only_null_capacities = True
    for open_var_indexes, open_var in open_var_filter.items():
        capacity = sites_step_info.get(open_var_indexes, {}).get(StepCostSheet.capacity, pd.NA)
        capacities.append(capacity)
        variables.append(open_var)
        if pd.notna(capacity):
            only_null_capacities = False

    if only_null_capacities:
        return 0.0

    max_capacity = quicksum(
        prod([capacities[i], variables[i]]) if pd.notna(capacities[i]) else prod([big_m, variables[i]])
        for i in range(len(capacities))
    )
    return max_capacity


def get_production_max_capacity(
    production_binary_variables: OptimizedDict,
    production_step_info: Dict[Tuple[Period, Origin, Product, StepID, Step], Dict[str, float]],
    production_indexes: Tuple[Period, Origin, Product],
    big_m: float,
) -> Any:
    period, origin, product = production_indexes
    binary_var_filter = production_binary_variables[period, origin, product, :, :]

    if binary_var_filter:
        capacities = []
        variables = []
        only_null_capacities = True
        for production_index, binary_var in binary_var_filter.items():
            capacity = production_step_info.get(production_index, {}).get(StepCostSheet.capacity, pd.NA)
            capacities.append(capacity)
            variables.append(binary_var)
            if pd.notna(capacity):
                only_null_capacities = False
        if only_null_capacities:
            return 0.0
        max_capacity = quicksum(
            prod([capacities[i], variables[i]]) if pd.notna(capacities[i]) else prod([big_m, variables[i]])
            for i in range(len(capacities))
        )
    else:
        max_capacity = 0.0

    return max_capacity
