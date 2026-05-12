import glob
import yaml

from pydantic import BaseModel
from pathlib import Path


class ConfigProvider:

    @staticmethod
    def load(config_path: str, model_class: type[BaseModel]) -> BaseModel:
        BASE_DIR = Path(__file__).resolve().parent.parent
        merged_data = {}

        files = glob.glob(f"{BASE_DIR}/{config_path}/*.yaml")
        for file_path in files:

            with open(file_path, "r") as file:
                data = yaml.safe_load(file) or {}

            for key, value in data.items():

                if isinstance(value, list):

                    if key not in merged_data:
                        merged_data[key] = []

                    merged_data[key].extend(value)

                elif isinstance(value, dict):

                    if key not in merged_data:
                        merged_data[key] = {}

                    merged_data[key].update(value)

                else:
                    merged_data[key] = value
        return model_class(**merged_data)
