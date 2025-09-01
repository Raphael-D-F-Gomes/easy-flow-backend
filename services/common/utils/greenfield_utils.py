import math
from typing import Dict, Tuple, Set, Union

import pandas as pd

from services.common.tables.greenfield_name_registry import GreenfieldSettingsSheet
from services.common.tables.global_options import StatusOptions, SiteCategoryOptions
from services.common.tables.global_name_registry import SitesSheet

from services.run_model.build_opt_model.types.network_optimization_types import (
    Facility, Status, GeoInfo, Distance, Customer
)


def get_greenfield_candidates_table(sites: pd.DataFrame, greenfield_settings: pd.DataFrame) -> pd.DataFrame:

    valid_sites = sites[sites[SitesSheet.status] != StatusOptions.exclude].copy()
    valid_sites.loc[
        valid_sites[SitesSheet.site_category].isin([SiteCategoryOptions.supplier, SiteCategoryOptions.customer]),
        SitesSheet.status
    ] = StatusOptions.consider

    if bool(greenfield_settings[GreenfieldSettingsSheet.only_facilities_as_candidates][0]):
        candidates_table: pd.DataFrame = valid_sites[
            valid_sites[SitesSheet.site_category] == SiteCategoryOptions.facility
        ]
        return candidates_table
    else:
        valid_categories = [SiteCategoryOptions.customer]
        if not bool(greenfield_settings[GreenfieldSettingsSheet.exclude_suppliers][0]):
            valid_categories.append(SiteCategoryOptions.supplier)
        if not bool(greenfield_settings[GreenfieldSettingsSheet.exclude_facilities][0]):
            valid_categories.append(SiteCategoryOptions.facility)

        candidates_table: pd.DataFrame = valid_sites[valid_sites[SitesSheet.site_category].isin(valid_categories)]
        return candidates_table


def get_all_greenfield_facilities_with_status(
        sites: pd.DataFrame,
        greenfield_settings: pd.DataFrame,
) -> Dict[Facility, Status]:
    candidates_table = get_greenfield_candidates_table(sites, greenfield_settings)
    candidates_with_status: Dict[Facility, Status] = candidates_table.set_index(
        SitesSheet.site_id
    )[SitesSheet.status].to_dict()
    return candidates_with_status


def get_greenfield_considered_candidates(
        sites: pd.DataFrame,
        greenfield_settings: pd.DataFrame,
) -> Dict[Facility, Status]:
    candidates_table = get_greenfield_candidates_table(sites, greenfield_settings)
    candidates_with_status: Dict[Facility, Status] = candidates_table[
        candidates_table[SitesSheet.status] == StatusOptions.consider
    ].set_index(SitesSheet.site_id)[SitesSheet.status].to_dict()
    return candidates_with_status


def get_greenfield_included_candidates(
        sites: pd.DataFrame,
        greenfield_settings: pd.DataFrame,
) -> Dict[Facility, GeoInfo]:
    candidates_table = get_greenfield_candidates_table(sites, greenfield_settings)
    included_facilities: Dict[Facility, GeoInfo] = candidates_table[
        candidates_table[SitesSheet.status] == StatusOptions.include
        ].set_index(SitesSheet.site_id)[[SitesSheet.latitude, SitesSheet.longitude]].to_dict(orient="Index")
    return included_facilities


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> Distance:

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    variation_lon = lon2 - lon1
    variation_lat = lat2 - lat1
    var_a = math.sin(variation_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(variation_lon / 2) ** 2)
    var_a = max(min(var_a, 1), 0)
    var_c = 2 * math.atan2(math.sqrt(var_a), math.sqrt(1 - var_a))

    earth_radius_in_km = 6371
    return Distance(var_c * earth_radius_in_km)


def calculate_haversine(
        facilities: Set[Facility],
        customers: Set[Customer],
        sites_geolocation: Dict[Union[Customer, Facility], GeoInfo],
) -> Dict[Tuple[Facility, Customer], Distance]:
    distances: Dict[Tuple[Facility, Customer], Distance] = {}
    for facility in facilities:
        for customer in customers:
            if facility == customer:
                distances[facility, customer] = 0
            else:
                origin_latitude = sites_geolocation[facility][SitesSheet.latitude]
                origin_longitude = sites_geolocation[facility][SitesSheet.longitude]
                destination_latitude = sites_geolocation[customer][SitesSheet.latitude]
                destination_longitude = sites_geolocation[customer][SitesSheet.longitude]
                calculation = haversine(
                    origin_latitude, origin_longitude, destination_latitude, destination_longitude
                )
                distances[facility, customer] = Distance(round(calculation, 5))
    return distances


def calculate_euclidean(
        facilities: Set[Facility],
        customers: Set[Customer],
        coordinates_by_site_id: Dict[Union[Customer, Facility], GeoInfo],
) -> Dict[Tuple[Facility, Customer], Distance]:
    distances: Dict[Tuple[Facility, Customer], Distance] = {}
    for candidate in facilities:
        for customer in customers:
            if candidate == customer:
                distances[candidate, customer] = 0
            else:
                latitude_difference = (
                        coordinates_by_site_id[candidate][SitesSheet.latitude] -
                        coordinates_by_site_id[customer][SitesSheet.latitude]
                )
                longitude_difference = (
                        coordinates_by_site_id[candidate][SitesSheet.longitude] -
                        coordinates_by_site_id[customer][SitesSheet.longitude]
                )
                distances[candidate, customer] = Distance(
                    round((latitude_difference**2 + longitude_difference**2) ** (1 / 2), 5)
                )
    return distances
