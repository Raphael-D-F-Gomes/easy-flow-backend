from typing import Dict, List, Tuple

import pandas as pd

from services.common.user_input.tables import (Facilities, DemandTable, DistanceTable, GreenfieldSettingsTable,
                                               DistanceConstraintsTable)

from services.common.tables.greenfield_options import DistanceOptions
from services.common.tables.global_name_registry import SitesSheet, DemandSheet
from services.common.tables.greenfield_name_registry import (DistanceSheet, GreenfieldSettingsSheet,
                                                             GreenfieldDistanceConstraints)
from services.common.utils.greenfield_utils import calculate_haversine, calculate_euclidean

from services.run_model.build_opt_model.types.network_optimization_types import (
    Customer, Facility, GeoInfo, City, State, Country, Demand, Distance, N_Facilities
)


class GreenfieldUserInput:
    """
    The tables won't pass through validation here
    therefore the dataframe should already be formatted
    and verified
    """

    def __init__(self, tables: Dict[str, pd.DataFrame]):
        self.sites = Facilities(tables.get(SitesSheet.sheet_name, pd.DataFrame()))
        self.customers = DemandTable(tables.get(DemandSheet.sheet_name, pd.DataFrame()))
        self.distances = DistanceTable(tables.get(DistanceSheet.sheet_name, pd.DataFrame()))

        self.greenfield_settings = GreenfieldSettingsTable(
            tables.get(GreenfieldSettingsSheet.sheet_name, pd.DataFrame())
        )
        self.distance_constraints = DistanceConstraintsTable(
            tables.get(GreenfieldDistanceConstraints.sheet_name, pd.DataFrame())
        )

    @property
    def greenfield_objective(self) -> str:
        return self.greenfield_settings.data[GreenfieldSettingsSheet.objective_type][0]

    def is_type_two(self) -> bool:
        return self.greenfield_settings.is_type_two()

    def candidates_generation_from_existing_nodes(self) -> bool:
        return self.greenfield_settings.are_candidates_registered()

    def get_coordinates_demand(self) -> List[Dict]:

        sites_coordinates = self.sites.get_latitude_and_longitude_by_site_id()
        customers_demand = self.customers.get_name_map_to_demand()
        coordinates_demand = [
            {
                "label": name,
                "coordinates": (
                    sites_coordinates[name][SitesSheet.latitude], sites_coordinates[name][SitesSheet.longitude]
                ),
                "volume": volume,
            }
            for name, volume in customers_demand.items()
        ]
        return coordinates_demand

    def get_coordinates_fixed(self) -> List[Dict]:

        sites_coordinates = self.sites.get_latitude_and_longitude_by_site_id()
        include_candidates = self.get_included_candidates()
        coordinates_demand = [
            {
                "label": name,
                "coordinates": (
                    sites_coordinates[name][SitesSheet.latitude], sites_coordinates[name][SitesSheet.longitude]
                ),
            }
            for name in include_candidates
        ]
        return coordinates_demand

    def get_number_of_facilities(self) -> N_Facilities:
        return self.greenfield_settings.get_number_of_facilities()

    def get_included_sites_number(self) -> int:
        return len(self.sites.get_included_sites(self.greenfield_settings.data))

    def get_included_facilities_with_geolocation(self) -> Dict[Facility, GeoInfo]:
        return self.sites.get_included_sites(self.greenfield_settings.data)

    def get_customers_with_geolocation(self) -> Dict[Customer, GeoInfo]:
        return self.sites.get_customers()

    def get_demand_sites(self) -> list:
        return list(self.customers.get_name_map_to_demand().keys())

    def get_candidate_sites(self) -> list:
        return self.sites.get_all_greenfield_facilities(self.greenfield_settings.data)

    def get_considering_candidates(self) -> list:
        return self.sites.get_considering_candidates_sites(self.greenfield_settings.data)

    def get_included_candidates(self) -> list:
        return self.sites.get_included_sites(self.greenfield_settings.data)

    def get_demand(self) -> Dict[Customer, Demand]:
        return self.customers.get_name_map_to_demand()

    def get_distance_options(self) -> str:
        return self.greenfield_settings.get_distance_option()

    def get_distances(self) -> Dict[Tuple[str, str], float]:
        distance_option = self.get_distance_options()
        candidates = self.sites.get_all_greenfield_facilities(self.greenfield_settings.data)
        customers = self.sites.get_customers()
        sites_geolocation = self.sites.get_latitude_and_longitude_by_site_id()
        if distance_option == DistanceOptions.geodesic:
            distances = calculate_haversine(candidates, customers, sites_geolocation)
        elif distance_option == DistanceOptions.euclidean:
            distances = calculate_euclidean(candidates, customers, sites_geolocation)
        else:
            distances = self.distances.get_locations(candidates, customers, sites_geolocation)

        return distances

    def get_distance_demand_percentage(self) -> Dict[float, float]:
        service_distance_name = self.greenfield_settings.get_service_distance_constraint()
        distance_percentage = self.distance_constraints.get_demand_percentage_by_service_distance(
            service_distance_name
        )
        if self.greenfield_settings.is_service_type_absolute():
            return distance_percentage
        else:
            distance_by_percentage: Dict[float, float] = {}
            total = 0.0
            for distance, percentage in distance_percentage.items():
                total += percentage
                distance_by_percentage[distance] = total
            return distance_by_percentage

    def get_service_distance(self) -> Dict[float, Dict[Tuple[str, str], float]]:
        suppliers = self.sites.get_all_greenfield_facilities(self.greenfield_settings.data)
        demands = self.get_demand_sites()
        distances = self.get_distances()
        service_distance: Dict[float, Dict[Tuple[str, str], float]] = {}
        restriction_distances = self.get_distance_demand_percentage().keys()
        for distance_key in restriction_distances:
            in_distance_serv_distance_activation = {}
            for supply in suppliers:
                for demand in demands:
                    try:
                        distance = distances[supply, demand]
                    except KeyError:
                        distance = distances[demand, supply]
                    if distance <= distance_key:
                        in_distance_serv_distance_activation[supply, demand] = 1.0
            service_distance[distance_key] = in_distance_serv_distance_activation
        return service_distance
