from typing import Dict, List
from services.run_model.build_opt_model.opt_models.greenfield.socp_models.json_output import JsonOutput
from services.run_model.build_opt_model.opt_models.model_builder import ModelBuilder
from services.common.user_input import GreenfieldUserInput

from services.common.opt_model.planar_names import PlanarOptModel


class SingleFacilityPlanarPMedianModel(ModelBuilder):
    def __init__(self) -> None:
        super(SingleFacilityPlanarPMedianModel, self).__init__()
        self.writer = JsonOutput()

    def __repr__(self) -> str:
        return "p-median planar single facility"

    def build_model(self, user_input: GreenfieldUserInput) -> str:
        coordinates_demand = user_input.get_coordinates_demand()
        data_points: List[Dict] = []
        m1_needed_data = {"model-data": data_points}
        point_structure = {"latitude": None, "longitude": None, "volume": None}
        for point in coordinates_demand:
            point_structure["latitude"], point_structure["longitude"] = point["coordinates"]
            point_structure["volume"] = point["volume"]
            data_points.append(point_structure.copy())
        path = self.writer.write_model(m1_needed_data)
        return path


class PMedianContinuousBuilder(ModelBuilder):
    """
    This model considers new geolocation coordinates
    """

    def __repr__(self) -> str:
        return "p-median planar multi facilities"

    @staticmethod
    def get_demand_points(user_input: GreenfieldUserInput) -> List[Dict]:
        data_points: List[Dict] = []
        coordinates_demand = user_input.get_coordinates_demand()
        latitude = PlanarOptModel.latitude
        longitude = PlanarOptModel.longitude
        volume = PlanarOptModel.volume
        point_structure = {latitude: None, longitude: None, volume: None}
        for point in coordinates_demand:
            point_structure[latitude], point_structure[longitude] = point["coordinates"]
            point_structure[volume] = point[volume]
            data_points.append(point_structure.copy())
        return data_points

    @staticmethod
    def get_fixed_points(user_input: GreenfieldUserInput) -> List[Dict]:
        points = []
        latitude = PlanarOptModel.latitude
        longitude = PlanarOptModel.longitude
        point_structure = {latitude: None, longitude: None}
        for point in user_input.get_coordinates_fixed():
            point_structure[latitude], point_structure[longitude] = point["coordinates"]
            points.append(point_structure.copy())
        return points

    def build_model(self, user_input: GreenfieldUserInput) -> str:
        needed_data = {
            PlanarOptModel.model_data: {
                PlanarOptModel.demand_points: self.get_demand_points(user_input),
                PlanarOptModel.fixed_points: self.get_fixed_points(user_input),
                PlanarOptModel.number_of_facilities: user_input.get_number_of_facilities(),
            }
        }

        path = JsonOutput.write_model(needed_data)
        return path
