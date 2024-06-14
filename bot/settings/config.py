import json

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file

    async def load_config(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)

    async def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    async def get_config_value(self, key):
        config = await self.load_config()
        if key not in config:
            raise ValueError(f"Config key {key} does not exist")
        return config[key]

    async def set_config_value(self, key, value):
        config = await self.load_config()
        config[key] = value
        await self.save_config(config)

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