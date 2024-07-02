import asyncio
import json
import os

import aiofiles


class ConfigFileManager:
    """
    Управляет файлами конфигурации и JSON-файлами для хранения и доступа к данным.

    Attributes:
        config_file (str): Путь к файлу конфигурации.
        json_path (str): Путь к JSON-файлу.

    Methods:
        get_config_value(key: str) -> any:
            Возвращает значение из конфигурации по заданному ключу.

        set_config_value(key: str, value: any) -> None:
            Устанавливает значение в конфигурации и сохраняет изменения.

        save_file_id(file_id: str, key: str) -> None:
            Сохраняет идентификатор файла по заданному ключу.

        get_file_path(key: str) -> str:
            Возвращает путь к файлу, связанному с заданным ключом.

        get_file_id(key: str) -> str:
            Возвращает идентификатор файла, связанный с заданным ключом.

        has_file_id(key: str) -> bool:
            Проверяет, существует ли идентификатор файла для заданного ключа.
    """

    def __init__(self, config_file: str, json_path: str):
        self.config_file = config_file
        self.json_path = json_path
        self._config = asyncio.run(self._load_file(config_file))
        self.file_ids = asyncio.run(self._load_file(json_path, default={}))

    @staticmethod
    async def _load_file(path: str, default=None) -> dict:
        """Загружает JSON-файл и возвращает его содержимое. Возвращает `default`, если файл не найден."""
        if not os.path.exists(path):
            if default is not None:
                return default
            raise FileNotFoundError(f"Файл {path} не найден.")
        async with aiofiles.open(path, 'r', encoding='utf-8') as file:
            content = await file.read()
            return json.loads(content)

    @staticmethod
    async def _save_file(path: str, data: dict) -> None:
        """Сохраняет словарь в JSON-файл."""
        async with aiofiles.open(path, 'w', encoding='utf-8') as file:
            await file.write(json.dumps(data, indent=4))

    async def get_config_value(self, key: str) -> any:
        """Возвращает значение из конфигурации."""
        if key not in self._config:
            raise KeyError(f"Ключ конфигурации {key} не существует.")
        return self._config[key]

    async def set_config_value(self, key: str, value: any) -> None:
        """Устанавливает значение в конфигурации и сохраняет его."""
        self._config[key] = value
        await self._save_file(self.config_file, self._config)

    async def save_file_id(self, file_id: str, key: str) -> None:
        """Сохраняет идентификатор файла по заданному ключу."""
        self.file_ids.setdefault(key, {})['file_id'] = file_id
        await self._save_file(self.json_path, self.file_ids)

    async def get_file_path(self, key: str) -> str:
        """Возвращает путь к файлу, связанному с заданным ключом."""
        return self.file_ids.get(key, {}).get('path')

    async def get_file_id(self, key: str) -> str:
        """Возвращает идентификатор файла, связанный с заданным ключом."""
        return self.file_ids.get(key, {}).get('file_id')

    async def has_file_id(self, key: str) -> bool:
        """Проверяет, существует ли идентификатор файла для заданного ключа."""
        return 'file_id' in self.file_ids.get(key, {})
