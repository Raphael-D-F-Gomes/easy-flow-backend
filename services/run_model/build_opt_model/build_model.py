from typing import Dict, List, Any

from dataclasses import dataclass, field

import pandas as pd
import json

from services.run_model.build_opt_model.opt_construction_function_names import OptConstructionFunctionName
from services.common.user_input import GreenfieldUserInput, NetworkOptimizationUserInput

from services.run_model.build_opt_model.opt_models import ModelBuilder
from services.run_model.build_opt_model.opt_models import PMedianDiscreteBuilder
from services.run_model.build_opt_model.opt_models import PMedianContinuousBuilder
from services.run_model.build_opt_model.opt_models import SetCoveringBuilder
from services.run_model.build_opt_model.opt_models import NetworkOptimizationBuilder


from services.common.logs.decorator import thread_log_decorator_function
from services.common.tables.global_name_registry import RunConfigSheet
from services.common.tables.global_options import EngineOptions
from services.common.tables.greenfield_options import GFAObjectiveOptions
from services.common.tables.global_options import EngineOptions, GreenfieldModelTypes
from services.common.utils.convert_period_tables_to_string import convert_period_columns_to_string


@dataclass
class Optimizer:

    input_path: str
    engine: str
    model_type: str
    tables: Dict[str, pd.DataFrame] = field(init=False)

    def __post_init__(self):
        self.tables = self.get_tables_from_json_file(self.input_path)

    def construct_model(self):
        pass

    @thread_log_decorator_function(OptConstructionFunctionName().get_input)
    def get_tables_from_json_file(self) -> Dict[str, pd.DataFrame]:
        tables: Dict[str, pd.DataFrame] = {}
        with open(self.input_path, "r") as file:
            result: Dict[str, Dict[str, List[Any]]] = json.load(file)

        for sheet, table in result.items():
            tables[sheet] = pd.DataFrame(table)

        return tables


class BuildModel:

    def __init__(self, engine: str, model_type: str, tables: pd.DataFrame[str, pd.DataFrame]):
        self.engine = engine
        self.tables = tables
        self.model_type = model_type

    def choose_model_builder(self):
        pass

    def build_model(self) -> str:

        if self.engine == EngineOptions.network_optimization:
            user_input = NetworkOptimizationUserInput(self.tables)
            model = NetworkOptimizationBuilder().build_model(user_input)
        else:
            user_input = GreenfieldUserInput(self.tables)
            model = self.choose_greenfield_model(user_input).build_model(user_input)

        return model

    @staticmethod
    @thread_log_decorator_function(OptConstructionFunctionName().choose_model, declare_result=True)
    def choose_greenfield_model(user_input: GreenfieldUserInput) -> ModelBuilder:

        if user_input.greenfield_objective == GFAObjectiveOptions.min_total_weighted_distances_and_n_facilities:
            return SetCoveringBuilder()

        if user_input.candidates_generation_from_existing_nodes():
            return PMedianDiscreteBuilder()

        return PMedianContinuousBuilder()





@thread_log_decorator_function(OptConstructionFunctionName().checking_module)
def is_network_optimization_module(tables: Dict[str, pd.DataFrame]) -> bool:
    engine = tables[RunConfigSheet.sheet_name][RunConfigSheet.engine][0]
    return engine in {EngineOptions.network_optimization, EngineOptions.no_opt}
