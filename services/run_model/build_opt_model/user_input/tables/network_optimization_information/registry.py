from typing import List, Tuple, Dict, Set

import pandas as pd

from optimization_construction_api.etl.types import Origin, StepID, Status, Product, Period, Ratio, Unit, Site
from optimization_construction_api.etl.user_input.tables import NetworkOptimizationTable
from shared.tables.global_name_registry import SitesSheet
from shared.tables.network_optimization_name_registry import (
    TransportationModeSheet,
    ProductsSheet,
    PeriodsSheet,
)
from shared.tables.network_optimization_options import OptionsName


class NetworkOptimizationSitesTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(NetworkOptimizationSitesTable, self).__init__(
            SitesSheet.sheet_name, SitesSheet(), data
        )
        self.columns: SitesSheet = SitesSheet()

    def get_sites_step_ids(self, sites: List[Origin]) -> List[Tuple[Origin, StepID]]:
        location = self.columns.site_id
        step_id = self.columns.fixed_step_operating_cost
        sites_step_ids: List[Tuple[Origin, StepID]] = list(
            self.data[self.data[location].isin(sites)][[location, step_id]].itertuples(index=False, name=None)
        )
        sites_step_ids = [
            (origin, OptionsName.none) if pd.isna(step_id) else (origin, step_id) for origin, step_id in sites_step_ids
        ]
        return sites_step_ids

    def get_step_by_site(self) -> Dict[Site, StepID]:
        step_by_site: Dict[Site, StepID] = self.data.dropna(
            subset=[self.columns.fixed_step_operating_cost]
        ).set_index(self.columns.site_id)[self.columns.fixed_step_operating_cost].to_dict()
        return step_by_site

    def get_variable_costs(self) -> Dict[Origin, float]:
        variable_costs: Dict[Origin, float] = (
            self.data.set_index([SitesSheet.site_id])[
                SitesSheet.variable_operating_cost
            ]
            .dropna()
            .to_dict()
        )
        return variable_costs

    def get_variable_costs_unit_of_measure(self) -> Dict[Origin, Unit]:
        columns = SitesSheet
        unit_by_origin: Dict[Origin, Unit] = (
            self.data[
                ~self.data[columns.variable_operating_cost].isna() & ~self.data[columns.variable_cost_basis].isna()
            ]
            .set_index(columns.site_id)[columns.variable_cost_basis]
            .to_dict()
        )
        return unit_by_origin

    def get_sites(self) -> Set[Site]:
        return set(self.data[self.columns.site_id].tolist())

    def get_sites_with_status(self) -> Dict[Site, Status]:
        sites_with_status: Dict[Site, Status] = self.data.set_index([self.columns.site_id])[
            self.columns.status
        ].to_dict()
        return sites_with_status


class TransportationModeTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(TransportationModeTable, self).__init__(
            TransportationModeSheet.sheet_name, TransportationModeSheet(), data
        )
        self.columns: TransportationModeSheet = TransportationModeSheet()


class ProductsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(ProductsTable, self).__init__(ProductsSheet.sheet_name, ProductsSheet(), data)
        self.columns: ProductsSheet = ProductsSheet()

    def get_unit_by_products(self) -> Dict[Unit, Dict[Product, Ratio]]:
        ratio_by_product_by_uom: Dict[Unit, Dict[Product, Ratio]] = self.data.set_index(ProductsSheet.product_id)[
            [ProductsSheet.alternative_unit1]
        ].dropna().to_dict()
        ratio_by_product_by_uom.update(self.data.set_index(ProductsSheet.product_id)[
            [ProductsSheet.alternative_unit2]
        ].dropna().to_dict())
        return ratio_by_product_by_uom


class PeriodsTable(NetworkOptimizationTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        self.periods: List[Period] = []
        super(PeriodsTable, self).__init__(PeriodsSheet.sheet_name, PeriodsSheet(), data)
        self.columns: PeriodsSheet = PeriodsSheet()

    def get_periods(self) -> List[Period]:
        if self.periods:
            return self.periods
        self.periods = self.data[self.columns.period].tolist()
        return self.periods
