from dataclasses import dataclass
from typing import Dict, Set, Tuple

from cvxpy import Variable

from services.run_model.build_opt_model.types.network_optimization_types import (
    Customer, Facility, N_Facilities, GeoInfo, Demand, Var_GeoInfo)


@dataclass
class Parameters:
    number_of_new_facilities: N_Facilities
    demand: Dict[Customer, Demand]
    facilities_geolocation: Dict[Facility, GeoInfo]
    customers_geolocation: Dict[Customer, GeoInfo]


@dataclass
class Variables:
    opening_variable: Dict[Facility, Variable]
    gfa_flow_variables: Dict[Tuple[Facility, Customer], Variable]
    candidates: Dict[Facility, Var_GeoInfo]
