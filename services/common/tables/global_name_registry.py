from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass
class GlobalSheetNames:
    scenario_items: str = "scenarioItems"
    scenarios: str = "scenarios"
    run_config: str = "runConfig"
    demand: str = "demand"
    sites: str = "sites"


@dataclass
class CommonColumnNames:

    status: str = "status"
    latitude: str = "latitude"
    longitude: str = "longitude"
    site: str = "site"
    volume: str = "quantity"
    product: str = "product"
    period: str = "period"
    mode: str = "transportationMode"
    origin: str = "origin"
    destination: str = "destination"


@dataclass
class InputSheet(Iterable):

    sheet_name: str
    status: str = CommonColumnNames.status

    def __iter__(self) -> Iterator[str]:
        for field, value in self.__dict__.items():
            if field != "sheet_name":
                aux_typing: str = value
                yield aux_typing

    def __next__(self):
        pass

    @property
    def columns(self):
        return self


@dataclass
class RunConfigSheet(InputSheet):

    sheet_name: str = GlobalSheetNames.run_config

    scenario_name: str = "scenarioName"
    engine: str = "engine"


@dataclass
class ScenariosSheet(InputSheet):

    sheet_name: str = GlobalSheetNames.scenarios

    scenario_name: str = "scenarioName"
    scenario_item: str = "scenarioItem"


@dataclass
class ScenarioItemsSheet(InputSheet):

    sheet_name: str = GlobalSheetNames.scenario_items

    scenario_item_name: str = "scenarioItemName"
    table: str = "table"
    column: str = "column"
    type: str = "type"
    option: str = "option"
    value: str = "value"


@dataclass
class DemandSheet(InputSheet):

    sheet_name: str = GlobalSheetNames.demand

    site: str = CommonColumnNames.site
    volume: str = CommonColumnNames.volume
    product: str = CommonColumnNames.product
    period: str = CommonColumnNames.period


@dataclass
class SitesSheet(InputSheet):

    sheet_name: str = GlobalSheetNames.sites

    site_id: str = "siteID"
    latitude: str = CommonColumnNames.latitude
    longitude: str = CommonColumnNames.longitude
    city: str = "city"
    state: str = "state"
    country: str = "country"
    type: str = "type"
    postal_code: str = "postalCode"

    fixed_step_operating_cost = "fixedOperatingStepCost"
    variable_operating_cost = "variableOperatingCost"
    variable_cost_basis = "variableCostBasis"
    site_category = "siteCategory"
