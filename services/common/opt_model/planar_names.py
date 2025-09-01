from dataclasses import dataclass


@dataclass
class PlanarOptModel:

    model_data: str = "model-data"
    demand_points: str = "demand-points"
    fixed_points: str = "fixed-points"
    number_of_facilities: str = "number-of-facilities"

    latitude: str = "latitude"
    longitude: str = "longitude"
    volume: str = "volume"
