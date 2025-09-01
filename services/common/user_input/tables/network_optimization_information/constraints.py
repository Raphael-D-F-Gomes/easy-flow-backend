from typing import Dict, Tuple, List

import pandas as pd

from optimization_construction_api.etl.types import (
    ExpressionName,
)

from optimization_construction_api.etl.user_input.tables import NetworkOptimizationTable
from shared.tables.network_optimization_name_registry import FlowConstraintsSheet, ExpressionConstraintsSheet, \
    ExpressionBasedCostSheet, SiteConstraintsSheet, ProductionConstraintsSheet
from shared.tables.network_optimization_options import (
    ConstraintsOptions,
)


class SiteConstraintsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        super(SiteConstraintsTable, self).__init__(SiteConstraintsSheet.sheet_name, SiteConstraintsSheet(), data)
        self.columns: SiteConstraintsSheet = SiteConstraintsSheet()

    def get_defined_site_constraints(self) -> List[ExpressionName]:
        if self.data.empty:
            return []
        defined_site_constraints: List[ExpressionName] = self.data[
            self.data[SiteConstraintsSheet.constraint_type] == ConstraintsOptions.define
            ][SiteConstraintsSheet.site_constraint_name].tolist()
        return defined_site_constraints


class FlowConstraintsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        if not data.empty:
            data = data[FlowConstraintsSheet.obligatory_columns]
        super(FlowConstraintsTable, self).__init__(FlowConstraintsSheet.sheet_name, FlowConstraintsSheet(), data)
        self.columns: FlowConstraintsSheet = FlowConstraintsSheet()

    def get_defined_flow_constraints(self) -> List[ExpressionName]:
        if self.data.empty:
            return []
        defined_flow_constraints: List[ExpressionName] = self.data[
            self.data[FlowConstraintsSheet.constraint_type] == ConstraintsOptions.define
            ][FlowConstraintsSheet.flow_constraint_name].tolist()
        return defined_flow_constraints


class ProductionConstraintsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        super(ProductionConstraintsTable, self).__init__(
            ProductionConstraintsSheet.sheet_name,
            ProductionConstraintsSheet(),
            data,
        )
        self.columns: ProductionConstraintsSheet = ProductionConstraintsSheet()

    def get_defined_production_constraints(self) -> List[ExpressionName]:
        if self.data.empty:
            return []
        defined_production_constraints: List[ExpressionName] = self.data[
            self.data[ProductionConstraintsSheet.constraint_type] == ConstraintsOptions.define
            ][ProductionConstraintsSheet.production_constraint_name].tolist()
        return defined_production_constraints


class ExpressionConstraintsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        super(ExpressionConstraintsTable, self).__init__(
            ExpressionConstraintsSheet.sheet_name, ExpressionConstraintsSheet(), data
        )
        self.columns: ExpressionConstraintsSheet = ExpressionConstraintsSheet()

    def get_cond_min_expression_constraints(self) -> List[ExpressionName]:
        if self.data.empty:
            return []
        cond_min_exp: List[ExpressionName] = self.data[
            self.data[self.columns.constraint_type] == ConstraintsOptions.cond_min
        ][self.columns.expression_constraint_name].tolist()
        return cond_min_exp

    def get_define_expression_constraints(self) -> List[ExpressionName]:
        if self.data.empty:
            return []
        define_exp: List[ExpressionName] = self.data[
            self.data[self.columns.constraint_type] == ConstraintsOptions.define
        ][self.columns.expression_constraint_name].tolist()
        return define_exp


class ExpressionBasedCostsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        super(ExpressionBasedCostsTable, self).__init__(
            ExpressionBasedCostSheet.sheet_name, ExpressionBasedCostSheet(), data
        )
        self.columns: ExpressionBasedCostSheet = ExpressionBasedCostSheet()

    def get_cost_by_expression(self) -> Dict[Tuple[str, ExpressionName], float]:
        if self.data.empty:
            return {}
        cost_by_expression: Dict[Tuple[str, ExpressionName], float] = self.data[
            self.data[self.columns.variable_cost] != 0
        ].set_index(
            [self.columns.name, self.columns.expression]
        )[self.columns.variable_cost].to_dict()
        return cost_by_expression
