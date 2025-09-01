from typing import List, Dict, Tuple, Set

import pandas as pd
from pyomo.core import Var, Objective, ConstraintList

from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.attribute import (
    ConcreteModelAttribute,
)

from services.run_model.build_opt_model.types.network_optimization_types  import (
    Product,
    Period,
    Mode,
    Origin,
    Destination,
    Step,
    StepID,
    Site,
    Status,
    Ratio,
    ExpressionName,
)


class SetsAttribute(ConcreteModelAttribute):

    @property
    def origins(self) -> Dict[Origin, Status]:
        origins: Dict[Origin, Status] = self.model.origins
        return origins

    @origins.setter
    def origins(self, value: Dict[Origin, Status]) -> None:
        self.model.origins = value

    @property
    def group_members(self) -> Dict[str, List[str]]:
        group_members: Dict[str, List[str]] = self.model.group_members
        return group_members

    @group_members.setter
    def group_members(self, value: Dict[str, List[str]]) -> None:
        self.model.group_members = value

    @property
    def periods(self) -> List[Period]:
        periods: List[Period] = self.model.periods
        return periods

    @periods.setter
    def periods(self, value: List[Period]) -> None:
        self.model.periods = value

    @property
    def production_sites_with_bom(self) -> Dict[Tuple[Period, Origin, Product], Dict[Product, float]]:
        production_sites_with_bom: Dict[
            Tuple[Period, Origin, Product], Dict[Product, float]
        ] = self.model.production_sites_with_bom
        return production_sites_with_bom

    @production_sites_with_bom.setter
    def production_sites_with_bom(self, value: Dict[Tuple[Period, Origin, Product], Dict[Product, float]]) -> None:
        self.model.production_sites_with_bom = value

    @property
    def production_and_intermediary_nodes(self) -> Set[Tuple[Period, Site, Product]]:
        production_and_intermediary_nodes: Set[
            Tuple[Period, Site, Product]
        ] = self.model.production_and_intermediary_nodes
        return production_and_intermediary_nodes

    @production_and_intermediary_nodes.setter
    def production_and_intermediary_nodes(self, value: Set[Tuple[Period, Site, Product]]) -> None:
        self.model.production_and_intermediary_nodes = value

    @property
    def flow_constraints(self) -> pd.DataFrame:
        flow_constraints: pd.DataFrame = self.model.flow_constraints
        return flow_constraints

    @flow_constraints.setter
    def flow_constraints(self, value: pd.DataFrame) -> None:
        self.model.flow_constraints = value

    @property
    def site_constraints(self) -> pd.DataFrame:
        site_constraints: pd.DataFrame = self.model.site_constraints
        return site_constraints

    @site_constraints.setter
    def site_constraints(self, value: pd.DataFrame) -> None:
        self.model.site_constraints = value

    @property
    def production_constraints(self) -> pd.DataFrame:
        production_constraints: pd.DataFrame = self.model.production_constraints
        return production_constraints

    @production_constraints.setter
    def production_constraints(self, value: pd.DataFrame) -> None:
        self.model.production_constraints = value

    @property
    def defined_expression_names(self) -> List[ExpressionName]:
        expressions: List[ExpressionName] = self.model.defined_expression_names
        return expressions

    @defined_expression_names.setter
    def defined_expression_names(self, value: List[ExpressionName]) -> None:
        self.model.defined_expression_names = value

    @property
    def cond_min_expression_constraints(self) -> List[ExpressionName]:
        cond_min_expression_constraints: List[ExpressionName] = self.model.cond_min_expression_constraints
        return cond_min_expression_constraints

    @cond_min_expression_constraints.setter
    def cond_min_expression_constraints(self, value: List[ExpressionName]) -> None:
        self.model.cond_min_expression_constraints = value

    @property
    def expression_constraints_info(self) -> pd.DataFrame:
        expression_constraints_info: pd.DataFrame = self.model.expression_constraints_info
        return expression_constraints_info

    @expression_constraints_info.setter
    def expression_constraints_info(self, value: pd.DataFrame) -> None:
        self.model.expression_constraints_info = value


class ParametersAttribute(ConcreteModelAttribute):
    @property
    def flows_cost(self) -> Dict[Tuple[Period, Origin, Destination, Mode, Product], float]:
        flows_cost: Dict[Tuple[Period, Origin, Destination, Mode, Product], float] = self.model.flows_cost
        return flows_cost

    @flows_cost.setter
    def flows_cost(self, value: Dict[Tuple[Period, Origin, Destination, Mode, Product], float]) -> None:
        self.model.flows_cost = value

    @property
    def production_variable_cost(self) -> Dict[Tuple[Period, Origin, Product], float]:
        production_variable_cost: Dict[Tuple[Period, Origin, Product], float] = self.model.production_variable_cost
        return production_variable_cost

    @production_variable_cost.setter
    def production_variable_cost(self, value: Dict[Tuple[Period, Origin, Product], float]) -> None:
        self.model.production_variable_cost = value

    @property
    def production_step_info(self) -> Dict[Tuple[Period, Origin, Product, StepID, Step], Dict[str, float]]:
        production_step_info: Dict[
            Tuple[Period, Origin, Product, StepID, Step], Dict[str, float]
        ] = self.model.production_step_info
        return production_step_info

    @production_step_info.setter
    def production_step_info(self, value: Dict[Tuple[Period, Origin, Product, StepID, Step], Dict[str, float]]) -> None:
        self.model.production_step_info = value

    @property
    def step_info_sites(self) -> Dict[Tuple[Period, Origin, StepID, Step], Dict[str, float]]:
        step_info_sites: Dict[Tuple[Period, Origin, StepID, Step], Dict[str, float]] = self.model.step_info_sites
        return step_info_sites

    @step_info_sites.setter
    def step_info_sites(self, value: Dict[Tuple[Period, Origin, StepID, Step], Dict[str, float]]) -> None:
        self.model.step_info_sites = value

    @property
    def raw_material_quantity_by_production_policies(
            self,
    ) -> Dict[Tuple[Period, Origin, Product], Dict[Tuple[Period, Origin, Product], float]]:
        raw_material_quantity_by_production_policies: Dict[
            Tuple[Period, Origin, Product], Dict[Tuple[Period, Origin, Product], float]
        ] = self.model.raw_material_quantity_by_production_policies
        return raw_material_quantity_by_production_policies

    @raw_material_quantity_by_production_policies.setter
    def raw_material_quantity_by_production_policies(
            self,
            value: Dict[Tuple[Period, Origin, Product], Dict[Tuple[Period, Origin, Product], float]],
    ) -> None:
        self.model.raw_material_quantity_by_production_policies = value

    @property
    def sites_variable_cost(self) -> Dict[Tuple[Period, Origin], float]:
        sites_variable_cost: Dict[Tuple[Period, Origin], float] = self.model.sites_variable_cost
        return sites_variable_cost

    @sites_variable_cost.setter
    def sites_variable_cost(self, value: Dict[Tuple[Period, Origin], float]) -> None:
        self.model.sites_variable_cost = value

    @property
    def destinations_demand(self) -> Dict[Tuple[Period, Destination, Product], float]:
        destinations_demand:  Dict[Tuple[Period, Destination, Product], float] = self.model.destinations_demand
        return destinations_demand

    @destinations_demand.setter
    def destinations_demand(self, value:  Dict[Tuple[Period, Destination, Product], float]) -> None:
        self.model.destinations_demand = value

    @property
    def outbound_cost(self) -> Dict[Tuple[Origin, Product], float]:
        outbound_cost: Dict[Tuple[Origin, Product], float] = self.model.outbound_cost
        return outbound_cost

    @outbound_cost.setter
    def outbound_cost(self, value: Dict[Tuple[Origin, Product], float]) -> None:
        self.model.outbound_cost = value

    @property
    def big_m(self) -> float:
        big_m: float = self.model.big_m
        return big_m

    @big_m.setter
    def big_m(self, value: float) -> None:
        self.model.big_m = value

    @property
    def capacity_unit_config(self) -> Dict[Origin, Dict[Product, Ratio]]:
        capacity_unit_config: Dict[Origin, Dict[Product, Ratio]] = self.model.capacity_unit_config
        return capacity_unit_config

    @capacity_unit_config.setter
    def capacity_unit_config(self, value: Dict[Origin, Dict[Product, Ratio]]) -> None:
        self.model.capacity_unit_config = value

    @property
    def variable_cost_unit_config(self) -> Dict[Origin, Dict[Product, Ratio]]:
        variable_cost_unit_config: Dict[Origin, Dict[Product, Ratio]] = self.model.variable_cost_unit_config
        return variable_cost_unit_config

    @variable_cost_unit_config.setter
    def variable_cost_unit_config(self, value: Dict[Origin, Dict[Product, Ratio]]) -> None:
        self.model.variable_cost_unit_config = value

    @property
    def expression_based_costs(self) -> Dict[Tuple[str, ExpressionName], float]:
        expression_based_costs: Dict[Tuple[str, ExpressionName], float] = self.model.expression_based_costs
        return expression_based_costs

    @expression_based_costs.setter
    def expression_based_costs(self, expression_based_costs: Dict[Tuple[str, ExpressionName], float]) -> None:
        self.model.expression_based_costs = expression_based_costs


class VariablesAttribute(ConcreteModelAttribute):
    @property
    def flow_variables(self) -> Dict[Tuple[Period, Origin, Destination, Mode, Product], Var]:
        flow_variables: Dict[Tuple[Period, Origin, Destination, Mode, Product], Var] = self.model.flow_variables
        return flow_variables

    @flow_variables.setter
    def flow_variables(self, value: Dict[Tuple[Period, Origin, Destination, Mode, Product], Var]) -> None:
        self.model.flow_variables = value

    @property
    def open_variables(self) -> Dict[Tuple[Period, Origin, StepID, Step], Var]:
        open_variables: Dict[Tuple[Period, Origin, StepID, Step], Var] = self.model.open_variables
        return open_variables

    @open_variables.setter
    def open_variables(self, value: Dict[Tuple[Period, Origin, StepID, Step], Var]) -> None:
        self.model.open_variables = value

    @property
    def prod_bin_var(self) -> Dict[Tuple[Period, Origin, Product, StepID, Step], Var]:
        prod_bin_var: Dict[
            Tuple[Period, Origin, Product, StepID, Step], Var
        ] = self.model.prod_bin_var
        return prod_bin_var

    @prod_bin_var.setter
    def prod_bin_var(self, value: Dict[Tuple[Period, Origin, Product, StepID, Step], Var]) -> None:
        self.model.prod_bin_var = value

    @property
    def origin_total_production(self) -> Dict[Tuple[Period, Origin, Product], Var]:
        origin_total_production: Dict[Tuple[Period, Origin, Product], Var] = self.model.origin_total_production
        return origin_total_production

    @origin_total_production.setter
    def origin_total_production(self, value: Dict[Tuple[Period, Origin, Product], Var]) -> None:
        self.model.origin_total_production = value

    @property
    def defined_expressions(self) -> Dict[ExpressionName, Var]:
        defined_expressions: Dict[ExpressionName, Var] = self.model.defined_expressions
        return defined_expressions

    @defined_expressions.setter
    def defined_expressions(self, value: Dict[ExpressionName, Var]) -> None:
        self.model.defined_expressions = value

    @property
    def flow_constraints_cond_min_variable(self) -> Dict[Tuple[str, int], Var]:
        flow_constraints_cond_min_variable: Dict[Tuple[str, int], Var] = self.model.flow_constraints_cond_min_variable
        return flow_constraints_cond_min_variable

    @flow_constraints_cond_min_variable.setter
    def flow_constraints_cond_min_variable(self, value: Dict[Tuple[str, int], Var]) -> None:
        self.model.flow_constraints_cond_min_variable = value

    @property
    def exp_constraints_cond_min_variable(self) -> Dict[str, Var]:
        exp_constraints_cond_min_variable: Dict[str, Var] = self.model.exp_constraints_cond_min_variable
        return exp_constraints_cond_min_variable

    @exp_constraints_cond_min_variable.setter
    def exp_constraints_cond_min_variable(self, value: Dict[str, Var]) -> None:
        self.model.exp_constraints_cond_min_variable = value

    @property
    def production_constraints_cond_min_variable(self) -> Dict[str, Var]:
        production_constraints_cond_min_variable: Dict[str, Var] = self.model.production_constraints_cond_min_variable
        return production_constraints_cond_min_variable

    @production_constraints_cond_min_variable.setter
    def production_constraints_cond_min_variable(self, value: Dict[str, Var]) -> None:
        self.model.production_constraints_cond_min_variable = value


class ObjectivesAttribute(ConcreteModelAttribute):
    @property
    def minimize_total_cost(self) -> Objective:
        objective: Objective = self.model.minimize_total_cost
        return objective

    @minimize_total_cost.setter
    def minimize_total_cost(self, value: Objective) -> None:
        self.model.minimize_total_cost = value


class ConstraintsAttribute(ConcreteModelAttribute):
    @property
    def site_maximum_capacity_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.site_maximum_capacity_constraint
        return constraints

    @site_maximum_capacity_constraint.setter
    def site_maximum_capacity_constraint(self, value: ConstraintList) -> None:
        self.model.site_maximum_capacity_constraint = value

    @property
    def production_maximum_capacity_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.production_maximum_capacity_constraint
        return constraints

    @production_maximum_capacity_constraint.setter
    def production_maximum_capacity_constraint(self, value: ConstraintList) -> None:
        self.model.production_maximum_capacity_constraint = value

    @property
    def set_production_binary_variables(self) -> ConstraintList:
        constraints: ConstraintList = self.model.set_production_binary_variables
        return constraints

    @set_production_binary_variables.setter
    def set_production_binary_variables(self, value: ConstraintList) -> None:
        self.model.set_production_binary_variables = value

    @property
    def compare_flow_with_demand_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.compare_flow_with_demand_constraint
        return constraints

    @compare_flow_with_demand_constraint.setter
    def compare_flow_with_demand_constraint(self, constraints: ConstraintList) -> None:
        self.model.compare_flow_with_demand_constraint = constraints

    @property
    def flow_limitation_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.flow_limitation_constraint
        return constraints

    @flow_limitation_constraint.setter
    def flow_limitation_constraint(self, value: ConstraintList) -> None:
        self.model.flow_limitation_constraint = value

    @property
    def fixed_include_sites(self) -> ConstraintList:
        constraints: ConstraintList = self.model.fixed_include_sites
        return constraints

    @fixed_include_sites.setter
    def fixed_include_sites(self, constraints: ConstraintList) -> None:
        self.model.fixed_include_sites = constraints

    @property
    def set_considered_sites(self) -> ConstraintList:
        constraints: ConstraintList = self.model.set_considered_sites
        return constraints

    @set_considered_sites.setter
    def set_considered_sites(self, constraints: ConstraintList) -> None:
        self.model.set_considered_sites = constraints

    @property
    def flow_conservation_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.flow_conservation_constraint
        return constraints

    @flow_conservation_constraint.setter
    def flow_conservation_constraint(self, value: ConstraintList) -> None:
        self.model.flow_conservation_constraint = value

    @property
    def flow_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.flow_constraint
        return constraints

    @flow_constraint.setter
    def flow_constraint(self, value: ConstraintList) -> None:
        self.model.flow_constraint = value

    @property
    def production_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.production_constraint
        return constraints

    @production_constraint.setter
    def production_constraint(self, value: ConstraintList) -> None:
        self.model.production_constraint = value

    @property
    def site_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.site_constraint
        return constraints

    @site_constraint.setter
    def site_constraint(self, value: ConstraintList) -> None:
        self.model.site_constraint = value

    @property
    def expression_constraint(self) -> ConstraintList:
        constraints: ConstraintList = self.model.expression_constraint
        return constraints

    @expression_constraint.setter
    def expression_constraint(self, value: ConstraintList) -> None:
        self.model.expression_constraint = value

    @property
    def site_opening_propagation(self) -> ConstraintList:
        constraints: ConstraintList = self.model.site_opening_propagation
        return constraints

    @site_opening_propagation.setter
    def site_opening_propagation(self, value: ConstraintList) -> None:
        self.model.site_opening_propagation = value
