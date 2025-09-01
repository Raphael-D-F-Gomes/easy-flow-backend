import pandas as pd

from shared.tables.global_name_registry import InputSheet


class NetworkOptimizationTable:
    def __init__(self, table_name: str, columns: InputSheet, data: pd.DataFrame = pd.DataFrame()):
        self.table_name = table_name
        self.data = data
        self.columns = columns
