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
