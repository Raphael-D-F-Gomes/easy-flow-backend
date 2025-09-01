from dataclasses import dataclass
from typing import Dict, Tuple

import pandas as pd

from shared.tables.greenfield_name_registry import ColumnName
from shared.tables.global_name_registry import DemandSheet


@dataclass
class SitesColumns:
    location = ColumnName.location
    latitude = ColumnName.latitude
    longitude = ColumnName.longitude


class SitesTable:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.columns = SitesColumns()

    def get_name_map_to_latitude_longitude(self) -> Dict[str, Tuple[float, float]]:
        if self.data.empty:
            return {}
        per_column_dic = self.data.set_index(self.columns.location)[
            [self.columns.latitude, self.columns.longitude]
        ].to_dict()

        name_to_lat_lon = {}
        for name in per_column_dic[self.columns.latitude]:
            name_to_lat_lon[name] = (
                per_column_dic[self.columns.latitude][name],
                per_column_dic[self.columns.longitude][name],
            )
        return name_to_lat_lon


@dataclass
class DemandColumns:
    location = DemandSheet.site
    volume = DemandSheet.volume


class DemandTable:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.columns = DemandColumns()

    def get_name_map_to_demand(self) -> Dict[str, float]:
        if self.data.empty:
            return {}
        return dict(self.data.set_index(self.columns.location)[self.columns.volume].to_dict())
