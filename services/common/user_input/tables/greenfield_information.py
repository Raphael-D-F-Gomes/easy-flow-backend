from typing import Dict, Tuple, List, Set, Union

import pandas as pd

from services.common.user_input.tables.greenfield_table_abstraction import GreenfieldTable

from services.common.tables.global_name_registry import DemandSheet
from services.common.tables.global_name_registry import SitesSheet
from services.common.tables.global_options import SiteCategoryOptions
from services.common.tables.greenfield_name_registry import DistanceSheet

from services.common.utils.greenfield_utils import get_all_greenfield_facilities_with_status, get_greenfield_included_candidates, \
    get_greenfield_considered_candidates, haversine

from services.run_model.build_opt_model.types.network_optimization_types import (
    Customer, Facility, GeoInfo, City, State, Country, Demand, Distance, Latitude, Longitude
)


class Facilities(GreenfieldTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(Facilities, self).__init__(SitesSheet.sheet_name, SitesSheet(), data)
        self.columns: SitesSheet = SitesSheet()

    def get_all_greenfield_facilities(self, greenfield_settings: pd.DataFrame) -> Set[Facility]:
        facilities = get_all_greenfield_facilities_with_status(self.data, greenfield_settings)
        return set(facilities)

    def get_included_sites(self, greenfield_settings: pd.DataFrame) -> Dict[Facility, GeoInfo]:
        included_sites = get_greenfield_included_candidates(self.data, greenfield_settings)
        return included_sites

    def get_customers(self) -> Dict[Customer, GeoInfo]:
        customers: Dict[Customer, GeoInfo] = self.data[
            self.data[SitesSheet.site_category] == SiteCategoryOptions.customer
        ].set_index(SitesSheet.site_id)[[SitesSheet.latitude, SitesSheet.longitude]].to_dict(orient="Index")
        return customers

    def get_considering_candidates_sites(self, greenfield_settings: pd.DataFrame) -> Set[Facility]:
        considered_candidates = get_greenfield_considered_candidates(self.data, greenfield_settings)
        return set(considered_candidates)

    def get_latitude_and_longitude_by_site_id(self) -> Dict[Union[Customer, Facility], GeoInfo]:
        coordinates_by_site_id: Dict[Union[Customer, Facility], GeoInfo] = self.data.set_index(self.columns.site_id)[
            [self.columns.latitude, self.columns.longitude]
        ].to_dict(orient="index")
        return coordinates_by_site_id

    def get_location_cities(self) -> Dict[Union[Customer, Facility], Tuple[City, State, Country]]:
        locations: Dict[Union[Customer, Facility], Tuple[City, State, Country]] = (
            self.data.set_index(self.columns.site_id)[[SitesSheet.city, SitesSheet.state, SitesSheet.country]]
            .apply(tuple, axis=1)
            .to_dict()
        )
        return locations


class DemandTable(GreenfieldTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(DemandTable, self).__init__(DemandSheet.sheet_name, DemandSheet(), data)
        self.columns: DemandSheet = DemandSheet()

    def get_name_map_to_demand(self) -> Dict[Customer, Demand]:
        if self.data.empty:
            return {}
        return dict(self.data.set_index(self.columns.site)[self.columns.volume].to_dict())


class DistanceTable(GreenfieldTable):
    def __init__(self, data: pd.DataFrame = pd.DataFrame()):
        super(DistanceTable, self).__init__(DistanceSheet.sheet_name, DistanceSheet(), data)
        self.columns: DistanceSheet = DistanceSheet()

    def get_locations(
            self,
            facilities: Set[Facility],
            customers: Set[Customer],
            sites_geolocation: Dict[Union[Customer, Facility], GeoInfo],
    ) -> Dict[Tuple[Facility, Customer], Distance]:

        registered_distances:  Dict[Tuple[Union[Customer, Facility], Union[Customer, Facility]], Distance] = (
            self.data.set_index([self.columns.origin, self.columns.destination])[self.columns.distance].to_dict())
        model_distances: Dict[Tuple[Facility, Customer], Distance]  = {}
        for facility in facilities:
            for customer in customers:
                if facility == customer:
                    model_distances[facility, customer] = Distance(0.0)
                elif (facility, customer) in registered_distances or (customer, facility) in registered_distances:
                    model_distances[facility, customer] = registered_distances.get(
                        (facility, customer), registered_distances.get((customer, facility))
                    )
                else:
                    model_distances[facility, customer] = haversine(
                        sites_geolocation[facility][SitesSheet.latitude],
                        sites_geolocation[facility][SitesSheet.longitude],
                        sites_geolocation[customer][SitesSheet.latitude],
                        sites_geolocation[customer][SitesSheet.longitude],
                    )

        return model_distances
