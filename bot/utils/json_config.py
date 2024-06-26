import asyncio
import json
import os

import aiofiles


class ConfigFileManager:
    def __init__(self, config_file: str, json_path: str):
        self.config_file = config_file
        self.json_path = json_path
        self._config = asyncio.run(self._load_file(config_file))
        self.file_ids = asyncio.run(self._load_file(json_path, default={}))

    @staticmethod
    async def _load_file(path: str, default=None) -> dict:
        """Loads a JSON file and returns its content. Returns `default` if file not found."""
        if not os.path.exists(path):
            if default is not None:
                return default
            raise FileNotFoundError(f"File {path} not found.")
        async with aiofiles.open(path, 'r', encoding='utf-8') as file:
            content = await file.read()
            return json.loads(content)

    @staticmethod
    async def _save_file(path: str, data: dict) -> None:
        """Saves a dictionary to a JSON file."""
        async with aiofiles.open(path, 'w', encoding='utf-8') as file:
            await file.write(json.dumps(data, indent=4))

    async def get_config_value(self, key: str) -> any:
        """Retrieves a value from the configuration."""
        if key not in self._config:
            raise KeyError(f"Config key {key} does not exist.")
        return self._config[key]

    async def set_config_value(self, key: str, value: any) -> None:
        """Sets a value in the configuration and saves it."""
        self._config[key] = value
        await self._save_file(self.config_file, self._config)

    async def save_file_id(self, file_id: str, key: str) -> None:
        """Saves a file ID under a specific key."""
        self.file_ids.setdefault(key, {})['file_id'] = file_id
        await self._save_file(self.json_path, self.file_ids)

    async def get_file_path(self, key: str) -> str:
        """Retrieves the file path associated with a specific key."""
        return self.file_ids.get(key, {}).get('path')

    async def get_file_id(self, key: str) -> str:
        """Retrieves the file ID associated with a specific key."""
        return self.file_ids.get(key, {}).get('file_id')

    async def has_file_id(self, key: str) -> bool:
        """Checks if a file ID exists for a specific key."""
        return 'file_id' in self.file_ids.get(key, {})
