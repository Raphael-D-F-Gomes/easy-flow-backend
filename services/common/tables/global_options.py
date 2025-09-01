from dataclasses import dataclass


@dataclass
class StatusOptions:
    include: str = "Include"
    exclude: str = "Exclude"
    consider: str = "Consider"


@dataclass
class ScenarioItemConditionOptions:
    begins_with = "beginswith"
    ends_with = "endswith"
    contains = "contains"
    greater_than = "greaterthan"
    less_than = "lessthan"
    equals = "equalsto"
    greater_or_equal = "greaterthanorequalsto"
    less_or_equal = "lessthanorequalsto"
    different = "different"
    does_not_contain = "doesnotcontain"


@dataclass
class ScenarioItemActionOptions:
    replace_with = "replacewith"
    multiply_by = "multiplyby"
    add = "add"
    subtract = "subtract"
    divide_by = "divideby"


@dataclass
class ScenarioItemProcessType:
    action = "action"
    condition = "condition"


@dataclass
class EngineOptions:
    greenfield = "greenfield"
    network_optimization = "networkoptimization"
    gfa = "gfa"
    no_opt = "noopt"


@dataclass
class GreenfieldModelTypes:
    set_covering_weighted_distance = "Minimize the quantity of facilities and the total weighted distance based in service bands"
    p_median_discrete = "Minimize the total weighted distance based in a fixed number of facilities, considering existent nodes"
    p_median_continuos = "Minimize the total weighted distance based in a fixed number of facilities, considering new nodes"


@dataclass
class SiteCategoryOptions:
    customer: str = "customer"
    supplier: str = "supplier"
    facility: str = "facility"
