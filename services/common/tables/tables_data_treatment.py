from typing import List, Dict

from dataclasses import dataclass

import pandas as pd

from shared.tables.global_name_registry import DemandSheet, RunConfigSheet, CommonColumnNames
from shared.tables.global_options import EngineOptions


@dataclass
class SumFloatDuplicateRows:
    column_to_sum: str
    sheet_name: str
    duplicate_indexes: List[str]


@dataclass
class SumNetworkOptimizationDemandVolumeDuplicateRows(SumFloatDuplicateRows):

    column_to_sum = DemandSheet.volume
    sheet_name = DemandSheet.sheet_name
    duplicate_indexes = [
        DemandSheet.site,
        DemandSheet.product,
        DemandSheet.period,
    ]


@dataclass
class SumGreenfieldDemandVolumeDuplicateRows(SumFloatDuplicateRows):

    column_to_sum = DemandSheet.volume
    sheet_name = DemandSheet.sheet_name
    duplicate_indexes = [DemandSheet.site]


NETWORK_OPTIMIZATION_TABLES_TO_SUM_FLOATS: List = [SumNetworkOptimizationDemandVolumeDuplicateRows]
GREENFIELD_TABLES_TO_SUM_FLOATS: List = [SumGreenfieldDemandVolumeDuplicateRows]


def sum_floats_in_duplicate_rows(tables: Dict[str, pd.DataFrame]) -> None:
    engine = tables[RunConfigSheet.sheet_name][RunConfigSheet.engine][0]
    tables_to_sum = get_tables_allowed_to_have_duplicates(engine)

    for config in tables_to_sum:
        table = tables.get(config.sheet_name, pd.DataFrame())
        if len(table) == 0 or any(column not in table.columns for column in config.duplicate_indexes):
            continue
        table = table.groupby(config.duplicate_indexes + [CommonColumnNames.status], as_index=False).sum(
            numeric_only=True
        )
        tables[config.sheet_name] = table


def get_tables_allowed_to_have_duplicates(engine: str) -> List:
    if engine.lower().replace(" ", "") in [EngineOptions.no_opt, EngineOptions.network_optimization]:
        return NETWORK_OPTIMIZATION_TABLES_TO_SUM_FLOATS
    return GREENFIELD_TABLES_TO_SUM_FLOATS
