from typing import Dict, Any

from collections import OrderedDict

import pandas as pd

from services.common.user_input.tables.greenfield_table_abstraction import GreenfieldTable

from services.common.tables.greenfield_name_registry import GreenfieldSettingsSheet
from services.common.tables.greenfield_name_registry import GreenfieldDistanceConstraints
from services.common.tables.greenfield_options import CandidatesGenerationOptions
from services.common.tables.greenfield_options import ServDistOptions
from services.common.tables.greenfield_options import GFAObjectiveOptions

from services.run_model.build_opt_model.types.network_optimization_types import (
    Customer, Facility, Distance_Level, Demand_Percentage, Demand, N_Facilities
)


class GreenfieldSettingsTable(GreenfieldTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        shared_table = GreenfieldSettingsSheet()
        super(GreenfieldSettingsTable, self).__init__(shared_table.sheet_name, shared_table.columns, data)
        self.columns = shared_table.columns

        self.dict_data: Dict[str, Any] = {}

    def set_dict_data(self) -> None:
        if not self.data.empty:
            self.dict_data = self.data.to_dict(orient="records")[0]

    def are_candidates_registered(self) -> bool:
        from_existing_nodes = CandidatesGenerationOptions.from_existing_nodes
        answer: bool = self.data[GreenfieldSettingsSheet.greenfield_candidates][0] == from_existing_nodes
        return bool(answer)

    def get_number_of_facilities(self) -> N_Facilities:
        return N_Facilities(self.data[GreenfieldSettingsSheet.number_of_facilities][0])

    def get_distance_option(self) -> str:
        distance: str = self.data[GreenfieldSettingsSheet.distance_choice][0]
        return distance

    def is_service_type_absolute(self) -> bool:
        return bool(
            self.data[GreenfieldSettingsSheet.service_distance_aggregation][0] == ServDistOptions.absolute
        )

    def get_service_distance_constraint(self) -> str:
        return str(self.data[GreenfieldSettingsSheet.service_distance_constraint][0])

    def is_type_two(self) -> bool:
        return bool(
            self.data[GreenfieldSettingsSheet.objective_type][0] ==
            GFAObjectiveOptions.min_total_weighted_distances_and_n_facilities
        )


class DistanceConstraintsTable(GreenfieldTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        shared_table = GreenfieldDistanceConstraints()
        super(DistanceConstraintsTable, self).__init__(shared_table.sheet_name, shared_table.columns, data)
        self.columns: GreenfieldDistanceConstraints = shared_table

    def get_demand_percentage_by_service_distance(
            self,
            service_distance_name: str,
    ) -> Dict[Distance_Level, Demand_Percentage]:
        self.data = self.data[self.data[self.columns.service_distance_name] == service_distance_name]
        self.data = self.data.sort_values(by=self.columns.service_distance)
        distance_and_percentage: Dict[Distance_Level, Demand_Percentage] = OrderedDict(self.data.set_index(
            self.columns.service_distance
        )[self.columns.demand_percentage].to_dict())
        return distance_and_percentage
