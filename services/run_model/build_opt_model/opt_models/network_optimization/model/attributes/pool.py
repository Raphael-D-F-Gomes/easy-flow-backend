from typing import Type
from dataclasses import dataclass

from services.run_model.build_opt_model.opt_models.network_optimization.model.attributes.attributes import\
    SetsAttribute
from services.run_model.build_opt_model.opt_models.network_optimization.model.attributes.attributes import\
    ParametersAttribute
from services.run_model.build_opt_model.opt_models.network_optimization.model.attributes.attributes import\
    VariablesAttribute
from services.run_model.build_opt_model.opt_models.network_optimization.model.attributes.attributes import\
    ObjectivesAttribute
from services.run_model.build_opt_model.opt_models.network_optimization.model.attributes.attributes import\
    ConstraintsAttribute


@dataclass
class NetworkOptimizationAttributePool:

    set_attr: Type[SetsAttribute] = SetsAttribute
    param_attr: Type[ParametersAttribute] = ParametersAttribute
    var_attr: Type[VariablesAttribute] = VariablesAttribute
    obj_attr: Type[ObjectivesAttribute] = ObjectivesAttribute
    const_attr: Type[ConstraintsAttribute] = ConstraintsAttribute
