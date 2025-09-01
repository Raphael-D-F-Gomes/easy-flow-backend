from typing import NewType, Any, Dict
from dataclasses import dataclass

from cvxpy.expressions.variable import Variable

from services.common.tables.network_optimization_name_registry import (
    FlowConstraintsSheet, ProductionConstraintsSheet, SiteConstraintsSheet
)


Product = NewType("Product", str)
Mode = NewType("Mode", str)
Period = NewType("Period", str)
Origin = NewType("Origin", str)
Destination = NewType("Destination", str)
BOMName = NewType("BOMName", Any)
Step = NewType("Step", int)
Unit = NewType("Unit", int)
Ratio = NewType("Ratio", float)
Site = NewType("Site", str)
Status = NewType("Status", str)
StepID = NewType("StepID", str)
ConstraintName = NewType("ConstraintName", str)
ConstraintValue = NewType("ConstraintValue", float)
ConstraintType = NewType("ConstraintType", str)
ExpressionName = NewType("ExpressionName", str)

Customer = NewType("Customer", str)
Facility = NewType("Facility", str)
Demand = NewType("Demand", float)
N_Facilities = NewType("N_Facilities", int)
Distance_Level = NewType("Distance_Level", float)
Demand_Percentage = NewType("Demand_Percentage", float)
GeoInfo = NewType("GeoInfo", Dict[str, float])
City = NewType("City", str)
State = NewType("State", str)
Country = NewType("Country", str)
Distance = NewType("Distance", float)
Latitude = NewType("Latitude", float)
Longitude = NewType("Longitude", float)
Var_GeoInfo = NewType("Var_GeoInfo", Variable)


@dataclass
class IndexesByColumn:
    flow_indexes = {
        FlowConstraintsSheet.period: 0,
        FlowConstraintsSheet.origin: 1,
        FlowConstraintsSheet.destination: 2,
        FlowConstraintsSheet.transportation_mode: 3,
        FlowConstraintsSheet.product: 4,
    }
    production_indexes = {
        ProductionConstraintsSheet.period: 0,
        ProductionConstraintsSheet.site: 1,
        ProductionConstraintsSheet.product: 2,
    }
    open_variables_indexes = {
        SiteConstraintsSheet.period: 0,
        SiteConstraintsSheet.site: 1,
    }
