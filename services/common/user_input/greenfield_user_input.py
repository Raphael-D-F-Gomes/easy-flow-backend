from typing import Dict, List, Tuple, Set

import pandas as pd

from services.common.user_input.tables import Facilities
from services.common.user_input.tables import DemandTable
from services.common.user_input.tables import DistanceTable
from services.common.user_input.tables import GreenfieldSettingsTable
from services.common.user_input.tables import DistanceConstraintsTable

from services.common.tables.greenfield_options import DistanceOptions
from services.common.tables.global_name_registry import SitesSheet, DemandSheet
from services.common.tables.greenfield_name_registry import (DistanceSheet, GreenfieldSettingsSheet,
                                                             GreenfieldDistanceConstraints)
from services.common.utils.greenfield_utils import calculate_haversine, calculate_euclidean
from services.run_model.build_opt_model.types.network_optimization_types import (
    Customer, Facility, Distance_Level, Demand_Percentage, Demand, N_Facilities, Distance
)


class GreenfieldUserInput:
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
        include_candidates = self.get_included_facilities()
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

    def get_number_of_facilities(self) -> int:
        return self.greenfield_settings.get_number_of_facilities()

    def get_included_sites_number(self) -> int:
        return len(self.sites.get_included_sites(self.greenfield_settings.data))

    def get_customers(self) -> Set[Customer]:
        return set(self.customers.get_name_map_to_demand().keys())

    def get_candidate_sites(self) -> Set[Facility]:
        return self.sites.get_all_greenfield_facilities(self.greenfield_settings.data)

    def get_considering_candidates(self) -> Set[Facility]:
        return self.sites.get_considering_candidates_sites(self.greenfield_settings.data)

    def get_included_facilities(self) -> Set[Facility]:
        return self.sites.get_included_sites(self.greenfield_settings.data)

    def get_demand(self) -> dict:
        return self.customers.get_name_map_to_demand()

    def get_distance_options(self) -> str:
        return self.greenfield_settings.get_distance_option()

    def get_flow_distances(self) -> Dict[Tuple[Facility, Customer], Distance]:
        distance_option = self.get_distance_options()
        facilities = self.sites.get_all_greenfield_facilities(self.greenfield_settings.data)
        customers = self.sites.get_customers()
        sites_geolocation = self.sites.get_latitude_and_longitude_by_site_id()
        if distance_option == DistanceOptions.geodesic:
            distances = calculate_haversine(facilities, customers, sites_geolocation)
        elif distance_option == DistanceOptions.euclidean:
            distances = calculate_euclidean(facilities, customers, sites_geolocation)
        else:
            distances = self.distances.get_locations(facilities, customers, sites_geolocation)

        return distances

    def get_demand_percentage_per_distance_level(self) -> Dict[Distance_Level, Demand_Percentage]:
        service_distance_name = self.greenfield_settings.get_service_distance_constraint()
        distance_percentage = self.distance_constraints.get_demand_percentage_by_service_distance(
            service_distance_name
        )
        if self.greenfield_settings.is_service_type_absolute():
            return distance_percentage
        else:
            distance_by_percentage: Dict[Distance_Level, Demand_Percentage] = {}
            total = 0.0
            for distance, percentage in distance_percentage.items():
                total += percentage
                distance_by_percentage[distance] = total
            return distance_by_percentage

    def get_flows_set_per_distance_level(self) -> Dict[Distance_Level, Set[Tuple[Facility, Customer]]]:
        facilities = self.sites.get_all_greenfield_facilities(self.greenfield_settings.data)
        customers = self.get_customers()
        distances = self.get_flow_distances()
        flow_per_service_distance: Dict[Distance_Level, Set[Tuple[Facility, Customer]]] = {}
        distance_levels = self.get_demand_percentage_per_distance_level().keys()
        for distance_level in distance_levels:
            flow_per_service_distance[distance_level] = set()
            for facility in facilities:
                for customer in customers:
                    if (facility, customer) in distances:
                        distance = distances[facility, customer]
                    else:
                        distance = distances[customer, facility]
                    if distance <= distance_level:
                        flow_per_service_distance[distance_level].add((facility, customer))
        return flow_per_service_distance
