from typing import Dict, Tuple, List

import pandas as pd

from optimization_construction_api.etl.user_input.tables.greenfield_table_abstraction import GreenfieldTable

from shared.tables.global_name_registry import DemandSheet
from shared.tables.global_name_registry import SitesSheet
from shared.tables.global_options import SiteCategoryOptions
from shared.tables.greenfield_name_registry import DistanceSheet

from shared.utils.greenfield_utils import get_all_greenfield_candidates, get_greenfield_included_candidates, \
    get_greenfield_considered_candidates, haversine


class SitesTable(GreenfieldTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(SitesTable, self).__init__(SitesSheet.sheet_name, SitesSheet(), data)
        self.columns: SitesSheet = SitesSheet()

    def get_candidate_sites(self, greenfield_settings: pd.DataFrame) -> List[str]:
        candidates = get_all_greenfield_candidates(self.data, greenfield_settings)
        return list(candidates)

    def get_included_sites(self, greenfield_settings: pd.DataFrame) -> List[str]:
        included_sites = get_greenfield_included_candidates(self.data, greenfield_settings)
        return list(included_sites)

    def get_customers(self) -> List[str]:
        customers: List[str] = self.data[
            self.data[SitesSheet.site_category] == SiteCategoryOptions.customer
        ][SitesSheet.site_id].tolist()
        return customers

    def get_considering_candidates_sites(self, greenfield_settings: pd.DataFrame) -> List[str]:
        considered_candidates = get_greenfield_considered_candidates(self.data, greenfield_settings)
        return list(considered_candidates)

    def get_latitude_and_longitude_by_site_id(self) -> Dict[str, Dict[str, float]]:
        coordinates_by_site_id: Dict[str, Dict[str, float]] = self.data.set_index(self.columns.site_id)[
            [self.columns.latitude, self.columns.longitude]
        ].to_dict(orient="index")
        return coordinates_by_site_id

    def get_location_cities(self) -> Dict[str, Tuple[str, str, str]]:
        locations: Dict[str, Tuple[str, str, str]] = (
            self.data.set_index(self.columns.site_id)[[SitesSheet.city, SitesSheet.state, SitesSheet.country]]
            .apply(tuple, axis=1)
            .to_dict()
        )
        return locations


class DemandTable(GreenfieldTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(DemandTable, self).__init__(DemandSheet.sheet_name, DemandSheet(), data)
        self.columns: DemandSheet = DemandSheet()

    def get_name_map_to_demand(self) -> Dict[str, float]:
        if self.data.empty:
            return {}
        return dict(self.data.set_index(self.columns.site)[self.columns.volume].to_dict())


class DistanceTable(GreenfieldTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(DistanceTable, self).__init__(DistanceSheet.sheet_name, DistanceSheet(), data)
        self.columns: DistanceSheet = DistanceSheet()

    def get_locations(
            self,
            candidates: List[str],
            customers: List[str],
            sites_geolocation: Dict[str, Dict[str, float]],
    ) -> Dict[Tuple[str, str], float]:

        registered_distances: Dict[Tuple[str, str], float] = self.data.set_index(
            [self.columns.origin, self.columns.destination]
        )[self.columns.distance].to_dict()
        model_distances: Dict[Tuple[str, str], float] = {}
        for candidate in candidates:
            for customer in customers:
                if candidate == customer:
                    model_distances[candidate, customer] = 0.0
                elif (candidate, customer) in registered_distances or (customer, candidate) in registered_distances:
                    model_distances[candidate, customer] = registered_distances.get(
                        (candidate, customer), registered_distances.get((customer, candidate), None)
                    )
                else:
                    model_distances[candidate, customer] = haversine(
                        sites_geolocation[candidate][SitesSheet.latitude],
                        sites_geolocation[candidate][SitesSheet.longitude],
                        sites_geolocation[customer][SitesSheet.latitude],
                        sites_geolocation[customer][SitesSheet.longitude],
                    )

        return model_distances
