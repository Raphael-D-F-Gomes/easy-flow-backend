from typing import List

from dataclasses import dataclass

from shared.tables.greenfield_name_registry import GreenfieldSheetNames


@dataclass
class OutputSheet:

    sheet_name: str

    def __iter__(self) -> str:
        for field, value in self.__dict__.items():
            if field != "sheet_name":
                value: str
                yield value

    @property
    def columns(self):
        return self


@dataclass
class OutputCommon:

    origin_latitude: str = "originLatitude"
    origin_longitude: str = "originLongitude"

    origin: str = "origin"
    scenario_name: str = "scenario"
    gap: str = "gap"
    primal_bound: str = "primalBound"
    dual_bound: str = "dualBound"


@dataclass
class OutputGreenfieldSummarySheet(OutputSheet):

    sheet_name: str = GreenfieldSheetNames.summary

    scenario_name: str = OutputCommon.scenario_name
    date_time: str = "dateTime"
    current_number: str = "numberOfIncludedSites"
    new_number: str = "numberOfNewFacilities"
    optimization_time: str = "solverTime"
    optimization_status: str = "status"
    obj_function_value: str = "objectiveFunctionValue"


@dataclass
class OutputFlowSheet(OutputSheet):

    sheet_name: str = GreenfieldSheetNames.flows

    scenario_name: str = OutputCommon.scenario_name
    origin: str = OutputCommon.origin
    origin_latitude: str = OutputCommon.origin_latitude
    origin_longitude: str = OutputCommon.origin_longitude
    destination: str = "destination"
    dest_latitude: str = "destinationLatitude"
    dest_longitude: str = "destinationLongitude"
    distance: str = "distance"
    demand_quantity: str = "demandQuantity"


@dataclass
class OutputGreenfieldSitesSheet(OutputSheet):

    sheet_name: str = GreenfieldSheetNames.sites

    scenario_name: str = OutputCommon.scenario_name
    facility: str = "facility"
    latitude: str = "latitude"
    longitude: str = "longitude"
    demandServed: str = "demandServed"
    average_distance: str = "averageDistanceToCustomer"
    furthest_distance: str = "furthestDistanceToCustomer"
    city: str = "city"
    state: str = "state"
    country: str = "country"
    facility_type: str = "facilityType"

    def all_columns(self) -> List[str]:
        columns = []
        for field, value in self.__dict__.items():
            if field != "sheet_name":
                value: str
                columns += [value]

        return columns

