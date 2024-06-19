import json
import os

class ConfigManager:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self._config = self._load_config()

    def _load_config(self) -> dict[str, any]:
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file {self.config_file} not found.")
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_config(self) -> None:
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=4)

    def get_config_value(self, key: str) -> any:
        if key not in self._config:
            raise KeyError(f"Config key {key} does not exist")
        return self._config[key]

    def set_config_value(self, key: str, value: any) -> None:
        self._config[key] = value
        self._save_config()

class FileIds:
    def __init__(self, json_path):
        self.json_path = json_path
        self.file_ids = self.load_file_ids()

    def load_file_ids(self):
        try:
            with open(self.json_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_file_id(self, file_id, key):
        self.file_ids[key]['file_id'] = file_id
        with open(self.json_path, 'w') as file:
            json.dump(self.file_ids, file, indent=4)

    def get_file_path(self, key):
        return self.file_ids.get(key, {}).get('path')

    def get_file_id(self, key):
        return self.file_ids.get(key, {}).get('file_id')

    def has_file_id(self, key):
        return 'file_id' in self.file_ids.get(key, {})