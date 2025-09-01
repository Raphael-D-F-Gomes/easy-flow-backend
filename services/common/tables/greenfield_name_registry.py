from dataclasses import dataclass

from shared.tables.global_name_registry import DemandSheet, SitesSheet, InputSheet


GREENFIELD_REQUIRED_TABLES = [SitesSheet.sheet_name, DemandSheet.sheet_name, "greenfieldSettings"]


@dataclass
class ColumnName:

    candidates_generation_status: str = "candidatesGenerationStatus"

    status: str = "status"
    include: str = "include"
    latitude: str = "latitude"
    longitude: str = "longitude"
    location: str = "siteID"
    volume: str = "quantity"
    product: str = "product"
    period: str = "period"


@dataclass
class GreenfieldSheetNames:
    sites: str = "greenfieldSites"
    flows: str = "greenfieldFlows"
    summary: str = "greenfieldSummary"
    distances: str = "greenfieldDistancesMatrix"
    greenfield_settings: str = "greenfieldSettings"


@dataclass
class DistanceSheet(InputSheet):

    sheet_name: str = GreenfieldSheetNames.distances

    origin: str = "origin"
    destination: str = "destination"
    distance: str = "distance"


@dataclass
class ConfigName:

    scenarios: str = "scenarios"
    greenfield_settings: str = "greenfieldSettings"
    greenfield_distance_constraints: str = "greenfieldDistanceConstraints"
    run_config: str = "runConfig"
    scenario_items: str = "scenarioItems"


@dataclass
class SectionKeyName:

    scenario_name: str = "scenarioName"
    scenario_id: str = "scenarioID"
    objective_type: str = "greenfieldObjective"
    include: str = ColumnName.include
    note: str = "note"

    number_of_facilities = "numberOfFacilities"
    chained_execution_choice = "chainedExecution"
    source_of_candidates_generation = "greenfieldCandidates"


@dataclass
class GreenfieldSettingsSheet(InputSheet):

    sheet_name: str = ConfigName.greenfield_settings

    objective_type: str = "greenfieldObjective"
    number_of_facilities: str = "numberOfNewFacilities"
    chained_execution_choice: str = "chainedExecution"
    greenfield_candidates: str = "greenfieldCandidates"
    distance_choice: str = "distanceType"
    service_distance_aggregation: str = "serviceDistanceAggregation"
    service_distance_constraint: str = "serviceDistanceConstraint"
    note: str = SectionKeyName.note
    exclude_facilities: str = "excludeFacilities"
    exclude_suppliers: str = "excludeSuppliers"
    only_facilities_as_candidates: str = "useOnlyFacilitiesAsGreenfieldLocation"


@dataclass
class GreenfieldDistanceConstraints(InputSheet):

    sheet_name: str = ConfigName.greenfield_distance_constraints

    service_distance: str = "serviceDistance"
    demand_percentage: str = "demandPercentage"
    service_distance_name: str = "serviceDistanceName"
