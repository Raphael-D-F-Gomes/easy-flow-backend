import os
import tempfile
import json
from typing import Dict


class JsonOutput:
    @staticmethod
    def write_model(model_data: Dict) -> str:
        file_path = os.path.join(tempfile.mkdtemp(), "model.json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(model_data, file)
        return file_path
