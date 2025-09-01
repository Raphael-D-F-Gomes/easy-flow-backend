from abc import abstractmethod
from typing import Any

import os
import tempfile

from services.run_model.build_opt_model.opt_models.model_builder import ModelBuilder
from services.common.user_input import GreenfieldUserInput
from services.run_model.build_opt_model.opt_models.greenfield.milp_models.bases.model import MILPModel


class AsIsLabeler(object):
    def __call__(self, obj: Any) -> str:
        name: str = obj.getname(True)
        return name


class MILPBuilder(ModelBuilder):
    def __init__(self, repr_name: str, name: str) -> None:
        self.repr_name = repr_name
        self.name = name

    def __repr__(self) -> str:
        return self.repr_name

    @abstractmethod
    def create_milp_model(self, data: GreenfieldUserInput) -> MILPModel:
        pass

    def write_model_to_file(self, model: MILPModel) -> str:
        name = self.name + ".mps"
        file_path = os.path.join(tempfile.mkdtemp(), name)
        model.write_mps(file_path, io_options={"labeler": AsIsLabeler()})
        return file_path

    def build_model(self, user_input: GreenfieldUserInput) -> str:
        concrete_model = self.create_milp_model(user_input)
        path = self.write_model_to_file(concrete_model)
        return path
