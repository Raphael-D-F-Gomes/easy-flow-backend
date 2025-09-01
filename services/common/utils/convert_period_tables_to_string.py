from typing import Dict

import pandas as pd

from shared.logs.sub_service_names import SharedServiceNames
from shared.logs.decorator import thread_log_decorator_function
from shared.tables.network_optimization_name_registry import (
    PeriodsSheet,
    ProductionPoliciesSheet,
    FlowConstraintsSheet,
    SiteConstraintsSheet,

)
from shared.tables.global_name_registry import DemandSheet


@thread_log_decorator_function(function_name=SharedServiceNames.convert_period_tables_to_string)
def convert_period_columns_to_string(tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    tables_with_periods = [
        (FlowConstraintsSheet.sheet_name, FlowConstraintsSheet.period),
        (SiteConstraintsSheet.sheet_name, SiteConstraintsSheet.period),
        (PeriodsSheet.sheet_name, PeriodsSheet.period),
        (DemandSheet.sheet_name, DemandSheet.period),
        (ProductionPoliciesSheet.sheet_name, ProductionPoliciesSheet.period),
    ]

    for table, column in tables_with_periods:
        if table in tables:
            if column in tables[table].columns:
                tables[table].loc[:, column] = tables[table][column].apply(str)

    return tables
