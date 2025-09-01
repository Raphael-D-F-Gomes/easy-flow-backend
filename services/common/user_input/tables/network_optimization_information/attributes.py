from typing import List, Tuple, Dict, Set

import pandas as pd

from optimization_construction_api.etl.types import Period, StepID, Step, Destination, Product, Unit
from optimization_construction_api.etl.user_input.tables import NetworkOptimizationTable
from shared.tables.global_name_registry import DemandSheet
from shared.tables.network_optimization_name_registry import (
    GroupsSheet,
    GroupMembersSheet,
    StepCostSheet,
    StepCostDefinitionsSheet,
)
from shared.tables.network_optimization_options import UnitOfMeasureOptions


class StepCostTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        self.step_info: Dict[StepID, Dict[Step, Dict[str, float]]] = {}
        super(StepCostTable, self).__init__(StepCostSheet.sheet_name, StepCostSheet(), data)
        self.columns: StepCostSheet = StepCostSheet()

    def get_step_info(self) -> Dict[StepID, Dict[Step, Dict[str, float]]]:
        step_info: Dict[StepID, Dict[Step, Dict[str, float]]] = {}
        if self.data.empty:
            return step_info
        if len(self.step_info) == 0:
            step_info = self.data.groupby(
                self.columns.step_cost_id
            ).apply(lambda x: x.set_index(self.columns.step)[
                [self.columns.cost, self.columns.capacity]
            ].astype(object).to_dict(orient='index')).to_dict()
            self.step_info = step_info
            return self.step_info
        else:
            return self.step_info


class StepCostDefinitionsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(StepCostDefinitionsTable, self).__init__(
            StepCostDefinitionsSheet.sheet_name, StepCostDefinitionsSheet(), data
        )
        self.columns: StepCostDefinitionsSheet = StepCostDefinitionsSheet()

    def get_unit_by_step(self) -> Dict[StepID, Unit]:

        if self.data.empty:
            return {}
        columns = StepCostDefinitionsSheet().columns
        unit_by_step: Dict[StepID, Unit] = (
            self.data[self.data[columns.unit_of_measure].isin(UnitOfMeasureOptions.units_indexes)]
            .set_index(columns.step_cost_id)[columns.unit_of_measure]
            .to_dict()
        )

        return unit_by_step


class GroupMembersTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(GroupMembersTable, self).__init__(GroupMembersSheet.sheet_name, GroupMembersSheet(), data)
        self.columns: GroupMembersSheet = GroupMembersSheet()

    def get_members_by_group(self) -> Dict[str, List[str]]:
        if self.data.empty:
            return {}
        members_by_group: Dict[str, List[str]] = (
            self.data.groupby(GroupMembersSheet.group_id)[GroupMembersSheet.member].apply(list).to_dict()
        )
        return members_by_group


class GroupsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(GroupsTable, self).__init__(GroupsSheet.sheet_name, GroupsSheet(), data)
        self.columns: GroupsSheet = GroupsSheet()


class NetworkOptimizationDemandTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(NetworkOptimizationDemandTable, self).__init__(
            DemandSheet.sheet_name, DemandSheet(), data
        )
        self.columns: DemandSheet = DemandSheet()
        self.destinations_demand: Dict[Tuple[Period, Destination, Product], float] = {}

    def get_destinations_demand(self) -> Dict[Tuple[Period, Destination, Product], float]:
        if self.destinations_demand:
            return self.destinations_demand

        self.destinations_demand = self.data.set_index([
            self.columns.period,
            self.columns.site,
            self.columns.product,
        ])[self.columns.volume].to_dict()

        return self.destinations_demand

    def get_demands_summation(self) -> float:
        return float(self.data[self.columns.volume].sum())

    def get_clients(self) -> Set[Destination]:
        return set(self.data[self.columns.site].unique())
