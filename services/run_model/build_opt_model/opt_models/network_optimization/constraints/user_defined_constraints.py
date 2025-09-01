from typing import List, Any, Dict, Tuple, Set, Union
from itertools import product as iter_prod
from collections import OrderedDict

import pandas as pd
from pyomo.core.util import prod, quicksum
from pyomo.core.base.expression import Expression
from pyomo.core.base.var import Var

from optimization_construction_api.etl.mathematical_models.network_optimization.model.model import (
    NetworkOptimizationModel,
)
from optimization_construction_api.etl.mathematical_models.network_optimization.class_parameters import (
   OptimizedVariables
)

from optimization_construction_api.etl.types import (
    Product,
    Period,
    Mode,
    Origin,
    Destination,
    IndexesByColumn,
)
from shared.tables.network_optimization_name_registry import (
    ExpressionConstraintsSheet,
    FlowConstraintsSheet,
    SiteConstraintsSheet,
    StepCostSheet,
    ProductionConstraintsSheet,
)
from shared.tables.global_options import StatusOptions
from shared.tables.network_optimization_options import (
    ConstraintsOptions,
    ConstraintIndexTreatmentOptions,
    GenericGroupsOptions,
)
from shared.utils.optimized_dictionary import OptimizedDict


class UserDefinedConstraints:
    @staticmethod
    def flow_constraints(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> Tuple[List[Expression], Dict[Tuple[str, int], Dict[str, Any]]]:

        cond_min_info: Dict[Tuple[str, int], Dict[str, Any]] = {}
        if len(model.set.flow_constraints) == 0:
            return [], cond_min_info
        flow_constraints: List[Expression] = []

        flow_variables = optimized_variables.flow_variables

        for _, row in model.set.flow_constraints.iterrows():

            individual_indexes, all_indexes = get_indexes_info(
                row,
                model.set.group_members,
                FlowConstraintsSheet.treatment_columns,
            )
            filtered_flows = flow_variables[tuple(all_indexes.values())]

            if (
                isinstance(filtered_flows, dict)
                and len(filtered_flows) == 0
                and row[FlowConstraintsSheet.constraint_type] != ConstraintsOptions.define
            ):
                continue

            if individual_indexes and any(
                isinstance(value, (list, set)) or value == GenericGroupsOptions.any
                for value in list(individual_indexes.values())
            ):

                individual_combinations, filtered_flows = get_individual_combinations(
                    filtered_flows,
                    individual_indexes,
                    all_indexes,
                    IndexesByColumn.flow_indexes,
                )

                for cond_min_count, combination in enumerate(individual_combinations):

                    expression, cond_min_to_add = get_flow_constraint_expression(
                        filtered_flows[combination], row, cond_min_count, model.var.defined_expressions
                    )
                    flow_constraints += expression
                    cond_min_info.update(cond_min_to_add)

            else:

                expression, cond_min_to_add = get_flow_constraint_expression(
                    filtered_flows,
                    row,
                    0,
                    model.var.defined_expressions
                )
                flow_constraints += expression
                cond_min_info.update(cond_min_to_add)

        return flow_constraints, cond_min_info

    @staticmethod
    def cond_min_flow_constraint(
        cond_min_info: Dict[Tuple[str, int], Dict[str, Any]],
        cond_min_var: Any,
        big_m: float,
    ) -> List[Expression]:

        cond_min_constraints: List[Expression] = []

        for keys, values in cond_min_info.items():
            exp_greater_than_value: Expression = (
                values["flows_summation"] - prod([values["constraint_value"], cond_min_var[keys]]) >= 0
            )
            exp_lower_than_big_m: Expression = values["flows_summation"] - prod([big_m, cond_min_var[keys]]) <= 0
            cond_min_constraints += [exp_lower_than_big_m] + [exp_greater_than_value]

        return cond_min_constraints

    @staticmethod
    def cond_min_production_constraint(
            cond_min_info: Dict[Tuple[str, int], Dict[str, Any]],
            cond_min_var: Any,
            big_m: float,
    ) -> List[Expression]:

        cond_min_constraints: List[Expression] = []

        for keys, values in cond_min_info.items():
            exp_greater_than_value: Expression = (
                    values["production_summation"] - prod([values["constraint_value"], cond_min_var[keys]]) >= 0
            )
            exp_lower_than_big_m: Expression = values["production_summation"] - prod([big_m, cond_min_var[keys]]) <= 0
            cond_min_constraints += [exp_lower_than_big_m] + [exp_greater_than_value]

        return cond_min_constraints

    @staticmethod
    def expression_constraints(model: NetworkOptimizationModel) -> List[Expression]:
        if model.set.expression_constraints_info.empty:
            return []
        exp_constraints: List[Expression] = []
        columns = ExpressionConstraintsSheet().columns

        cond_min_var = model.var.exp_constraints_cond_min_variable
        expressions = model.var.defined_expressions
        for _, row in model.set.expression_constraints_info.iterrows():
            exp1 = expressions[row[columns.expression1]]
            exp2 = expressions[row[columns.expression2]]
            coefficient1 = row[columns.coefficient1]
            coefficient2 = row[columns.coefficient2]
            exp: Expression = quicksum([prod([exp1, coefficient1]), prod([exp2, coefficient2])])
            if row[columns.constraint_type] == ConstraintsOptions.define:
                exp_constraints += [expressions[row[columns.expression_constraint_name]] == exp]
            elif row[columns.constraint_type] == ConstraintsOptions.cond_min:
                exp_constraints += adding_cond_min_constraint(
                    exp,
                    row[columns.value],
                    cond_min_var[row[columns.expression_constraint_name]],
                    model.param.big_m,
                )
            elif row[columns.constraint_type] in [
                ConstraintsOptions.min,
                ConstraintsOptions.max,
                ConstraintsOptions.fixed
            ]:
                exp_constraints += adding_constraint_min_max_or_fixed(
                    row[columns.constraint_type], exp, row[columns.value]
                )

        return exp_constraints

    @staticmethod
    def site_constraints(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:

        if len(model.set.site_constraints) == 0:
            return []
        site_constraints: List[Expression] = []

        open_variables = optimized_variables.open_variables

        for _, row in model.set.site_constraints.iterrows():

            steps_as_index = OrderedDict()
            steps_as_index[StepCostSheet.step_cost_id, ConstraintIndexTreatmentOptions.group] = slice(None, None, None)
            steps_as_index[StepCostSheet.step, ConstraintIndexTreatmentOptions.group] = slice(None, None, None)
            individual_indexes, all_indexes = get_indexes_info(
                row, model.set.group_members, SiteConstraintsSheet.treatment_columns, steps_as_index
            )
            filtered_open_variables = open_variables[tuple(all_indexes.values())]

            if (
                isinstance(filtered_open_variables, dict)
                and len(filtered_open_variables) == 0
                and row[FlowConstraintsSheet.constraint_type] != ConstraintsOptions.define
            ):
                continue

            if individual_indexes and any(
                isinstance(value, (list, set)) or value == GenericGroupsOptions.any
                for value in individual_indexes.values()
            ):

                individual_combinations, filtered_open_variables = get_individual_combinations(
                    filtered_open_variables,
                    individual_indexes,
                    all_indexes,
                    IndexesByColumn.open_variables_indexes,
                )

                for combination in individual_combinations:
                    individuals_open_var = filtered_open_variables[combination]

                    site_constraints += get_site_constraint_expression(
                        individuals_open_var, row, model.var.defined_expressions
                    )

            else:

                site_constraints += get_site_constraint_expression(
                    filtered_open_variables, row, model.var.defined_expressions
                )

        return site_constraints

    @staticmethod
    def site_opening_propagation(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> List[Expression]:

        opening_propagation_expressions: List[Expression] = []

        open_variables = optimized_variables.open_variables
        periods = model.set.periods
        origins = model.set.origins

        if len(periods) == 1:
            return []

        for site, status in origins.items():
            if status == StatusOptions.consider:
                for i, post_period in enumerate(periods[1::]):
                    filtered_post_period = open_variables[post_period, site, :, :]
                    filtered_period = open_variables[periods[i], site, :, :]
                    post_period_sum = sum(filtered_post_period.values())
                    period_sum = sum(filtered_period.values())
                    expression: Expression = period_sum <= post_period_sum
                    opening_propagation_expressions.append(expression)

        return opening_propagation_expressions

    @staticmethod
    def production_constraints(
            model: NetworkOptimizationModel,
            optimized_variables: OptimizedVariables,
    ) -> Tuple[List[Expression], Dict[Tuple[str, int], Dict[str, Any]]]:

        cond_min_info: Dict[Tuple[str, int], Dict[str, Any]] = {}
        if len(model.set.production_constraints) == 0:
            return [], cond_min_info
        production_constraints: List[Expression] = []

        production_variables = optimized_variables.total_production

        for _, row in model.set.production_constraints.iterrows():

            individual_indexes, all_indexes = get_indexes_info(
                row,
                model.set.group_members,
                ProductionConstraintsSheet.treatment_columns,
            )
            filtered_production = production_variables[tuple(all_indexes.values())]

            if (
                    isinstance(filtered_production, dict)
                    and len(filtered_production) == 0
                    and row[ProductionConstraintsSheet.constraint_type] != ConstraintsOptions.define
            ):
                continue

            if individual_indexes and any(
                    isinstance(value, (list, set)) or value == GenericGroupsOptions.any
                    for value in list(individual_indexes.values())
            ):

                individual_combinations, filtered_production = get_individual_combinations(
                    filtered_production,
                    individual_indexes,
                    all_indexes,
                    IndexesByColumn.production_indexes,
                )

                for cond_min_count, combination in enumerate(individual_combinations):
                    expression, cond_min_to_add = get_production_constraint_expression(
                        filtered_production[combination], row, cond_min_count, model.var.defined_expressions
                    )
                    production_constraints += expression
                    cond_min_info.update(cond_min_to_add)

            else:

                expression, cond_min_to_add = get_production_constraint_expression(
                    filtered_production,
                    row,
                    0,
                    model.var.defined_expressions,
                )
                production_constraints += expression
                cond_min_info.update(cond_min_to_add)

        return production_constraints, cond_min_info


def adding_constraint_min_max_or_fixed(constraint_type: str, linear_expression: Any, value: float) -> List[Expression]:

    if constraint_type == ConstraintsOptions.max:
        expression_max: Expression = linear_expression <= value
        return [expression_max]
    if constraint_type == ConstraintsOptions.min:
        expression_min: Expression = linear_expression >= value
        return [expression_min]
    if constraint_type == ConstraintsOptions.fixed:
        expression_fixed: Expression = linear_expression == value
        return [expression_fixed]

    return []


def adding_cond_min_constraint(
    linear_expression: Any, value: float, cond_min_var: Var, big_m: float
) -> List[Expression]:

    exp_greater_than_value: Expression = linear_expression - prod([value, cond_min_var]) >= 0
    exp_lower_than_big_m: Expression = linear_expression - prod([big_m, cond_min_var]) <= 0

    return [exp_greater_than_value, exp_lower_than_big_m]


def if_any_return_slice(value: Any) -> Any:
    if value == GenericGroupsOptions.any:
        return slice(None, None, None)
    return value


def if_any_return_set(value: Any, index_set: Set[str]) -> Any:
    if value == GenericGroupsOptions.any:
        return index_set
    if isinstance(value, (list, set)):
        return value
    return [value]


def get_individual_combinations(
    filtered_variables: Dict[Tuple[Any, ...], Var],
    individual_indexes: Dict[str, Any],
    all_indexes: Dict[Tuple[str, str], Any],
    indexes_relation: Dict[str, int],
) -> Tuple[List[Tuple[Any, ...]], OptimizedDict]:

    filtered_variables_optimized = OptimizedDict(filtered_variables)
    index_sets = filtered_variables_optimized.optimize()
    individual_indexes = {
        index: (
            if_any_return_set(
                individual_indexes[index],
                index_sets[indexes_relation[index]],
            )
            if treatment == ConstraintIndexTreatmentOptions.individual
            else [slice(None, None, None)]
        )
        for index, treatment in all_indexes
    }
    individual_combinations = list(iter_prod(*tuple(individual_indexes.values())))

    return individual_combinations, filtered_variables_optimized


def get_flow_constraint_expression(
    filtered_flows: Union[Dict[Tuple[Period, Origin, Destination, Mode, Product], Var], Var],
    row: pd.Series,
    cond_min_count: int,
    expressions: Dict[str, Var],
) -> Tuple[List[Expression], Dict[Tuple[str, int], Dict[str, Any]]]:

    flow_constraint: List[Expression] = []
    cond_min_info: Dict[Tuple[str, int], Dict[str, Any]] = {}

    if not isinstance(filtered_flows, dict):
        filtered_flows = {"key": filtered_flows}

    if len(filtered_flows) == 0 and row[FlowConstraintsSheet.constraint_type] != ConstraintsOptions.define:
        return [], {}

    flows_summation = quicksum(list(filtered_flows.values()))
    if row[FlowConstraintsSheet.constraint_type] in [
        ConstraintsOptions.min,
        ConstraintsOptions.max,
        ConstraintsOptions.fixed,
    ]:
        flow_constraint = adding_constraint_min_max_or_fixed(
            str(row[FlowConstraintsSheet.constraint_type]),
            flows_summation,
            float(row[FlowConstraintsSheet.value]),
        )
    elif row[FlowConstraintsSheet.constraint_type] == ConstraintsOptions.cond_min:
        cond_min_info[row[FlowConstraintsSheet.flow_constraint_name], cond_min_count] = {
            "flows_summation": flows_summation,
            "constraint_value": float(row[FlowConstraintsSheet.value]),
        }

    elif row[FlowConstraintsSheet.constraint_type] == ConstraintsOptions.define:
        flow_constraint = [expressions[row[FlowConstraintsSheet.flow_constraint_name]] == flows_summation]

    return flow_constraint, cond_min_info


def get_production_constraint_expression(
    filtered_production: Union[Dict[Tuple[Period, Origin, Product], Var], Var],
    row: pd.Series,
    cond_min_count: int,
    expressions: Dict[str, Var],
) -> Tuple[List[Expression], Dict[Tuple[str, int], Dict[str, Any]]]:

    production_constraint: List[Expression] = []
    cond_min_info: Dict[Tuple[str, int], Dict[str, Any]] = {}

    if not isinstance(filtered_production, dict):
        filtered_production = {"key": filtered_production}

    if len(filtered_production) == 0 and row[ProductionConstraintsSheet.constraint_type] != ConstraintsOptions.define:
        return [], {}

    production_summation = quicksum(list(filtered_production.values()))
    if row[ProductionConstraintsSheet.constraint_type] in [
        ConstraintsOptions.min,
        ConstraintsOptions.max,
        ConstraintsOptions.fixed,
    ]:
        production_constraint = adding_constraint_min_max_or_fixed(
            str(row[ProductionConstraintsSheet.constraint_type]),
            production_summation,
            float(row[ProductionConstraintsSheet.value]),
        )
    elif row[ProductionConstraintsSheet.constraint_type] == ConstraintsOptions.cond_min:
        cond_min_info[row[ProductionConstraintsSheet.production_constraint_name], cond_min_count] = {
            "production_summation": production_summation,
            "constraint_value": float(row[ProductionConstraintsSheet.value]),
        }

    elif row[ProductionConstraintsSheet.constraint_type] == ConstraintsOptions.define:
        production_constraint = [expressions[
                                     row[ProductionConstraintsSheet.production_constraint_name]
                                 ] == production_summation]

    return production_constraint, cond_min_info


def get_site_constraint_expression(
    filtered_open_var: Union[Dict[Tuple[Period, Origin, Destination, Mode, Product], Var], Var],
    row: pd.Series,
    expressions: Dict[str, Var],
) -> List[Expression]:

    site_constraint: List[Expression] = []

    if not isinstance(filtered_open_var, dict):
        filtered_open_var = {"key": filtered_open_var}

    if len(filtered_open_var) == 0 and row[FlowConstraintsSheet.constraint_type] != ConstraintsOptions.define:
        return []

    open_var_summation = quicksum(list(filtered_open_var.values()))
    if row[FlowConstraintsSheet.constraint_type] in [
        ConstraintsOptions.min,
        ConstraintsOptions.max,
        ConstraintsOptions.fixed,
    ]:
        site_constraint = adding_constraint_min_max_or_fixed(
            str(row[FlowConstraintsSheet.constraint_type]),
            open_var_summation,
            int(row[FlowConstraintsSheet.value]),
        )
    elif row[FlowConstraintsSheet.constraint_type] == ConstraintsOptions.define:
        site_constraint = [expressions[row[SiteConstraintsSheet.site_constraint_name]] == open_var_summation]

    return site_constraint


def get_indexes_info(
    row: pd.Series,
    group_members: Dict[str, List[str]],
    treatment_columns: Dict[str, str],
    insert_indexes: Union[OrderedDict[Tuple[str, str], slice], None] = None,
) -> Tuple[OrderedDict[str, Any], OrderedDict[Tuple[str, str], Any]]:
    individual_indexes: OrderedDict[str, Any] = OrderedDict()
    all_indexes: OrderedDict[Tuple[str, str], Any] = OrderedDict()
    for treatment, index in treatment_columns.items():
        all_indexes[index, row[treatment]] = if_any_return_slice(group_members.get(row[index], row[index]))
        if row[treatment] == ConstraintIndexTreatmentOptions.individual:
            individual_indexes[index] = group_members.get(row[index], row[index])

    if insert_indexes is not None:
        for key, value in insert_indexes.items():
            all_indexes[key] = value

    return individual_indexes, all_indexes
