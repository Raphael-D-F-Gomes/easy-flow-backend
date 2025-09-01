from typing import Type
from dataclasses import dataclass

from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.attribute import GFAGeneralSets


from services.run_model.build_opt_model.opt_models.greenfield.milp_models.set_covering.attributes.attributes import (
    SetCoveringParameters,
    ConstraintsAttribute,
    SetsAttribute,
    VariablesAttribute,
    ObjectivesAttribute
)


@dataclass
class SetCoveringAttributePool:

    set_attr: Type[SetsAttribute] = GFAGeneralSets
    param_attr: Type[SetCoveringParameters] = SetCoveringParameters
    var_attr: Type[VariablesAttribute] = VariablesAttribute
    obj_attr: Type[ObjectivesAttribute] = ObjectivesAttribute
    const_attr: Type[ConstraintsAttribute] = ConstraintsAttribute
