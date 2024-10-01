from orjson import orjson

from bot.database.base_model import model_registry
from bot.serializers.abstract_serializer import AbstractSerializer


class SQLSerializer(AbstractSerializer):
    """
    Сериализация и десериализация объектов с использованием библиотеки orjson.

    Методы:
    - serialize(obj: any) -> bytes:
      Сериализует объект в формат байтов. Добавляет информацию о классе модели (_model), если объект имеет метод as_dict.

      Аргументы:
      - obj (any): Объект для сериализации.

      Возвращает:
      - bytes: Сериализованный объект в формате байтов.

    - deserialize(data: bytes) -> any:
      Десериализует байтовые данные в объект(ы). Если данные представляют собой список, каждый элемент десериализуется отдельно.
      Ожидается, что каждый объект содержит информацию о классе модели (_model).

      Аргументы:
      - data (bytes): Байтовые данные для десериализации.

      Возвращает:
      - any: Десериализованный объект или список объектов.
    """

    def serialize(self, obj: any) -> bytes:
        """
        Сериализует объект в формат байтов с использованием orjson.

        Аргументы:
        - obj (any): Объект для сериализации.

        Возвращает:
        - bytes: Сериализованный объект в формате байтов.
        """

        def default(obj):
            if hasattr(obj, 'as_dict'):
                data = obj.as_dict
                data['_model'] = obj.__class__.__name__
                return data
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

        return orjson.dumps(obj, default=default, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS)

    def deserialize(self, data: bytes) -> any:
        """
        Десериализует байтовые данные в объект(ы) с использованием orjson.

        Аргументы:
        - data (bytes): Байтовые данные для десериализации.

        Возвращает:
        - any: Десериализованный объект или список объектов.
        """
        obj_dict_or_list = orjson.loads(data)

        if isinstance(obj_dict_or_list, list):
            return [self._deserialize_single(obj_dict) for obj_dict in obj_dict_or_list]
        else:
            return self._deserialize_single(obj_dict_or_list)

    @staticmethod
    def _deserialize_single(obj_dict: dict) -> any:
        """
        Восстанавливает отдельный объект из словаря с информацией о классе модели.

        Аргументы:
        - obj_dict (dict): Словарь с данными объекта и информацией о классе модели.

        Возвращает:
        - any: Десериализованный объект.

        Исключения:
        - ValueError: Если данные не содержат информации о модели или модель неизвестна.
        """
        model_name = obj_dict.pop('_model', None)

        if model_name is None:
            raise ValueError("Deserialized data does not contain model information")

        model_class = model_registry.get(model_name)

        if model_class is None:
            raise ValueError(f"Unknown model: {model_name}")

        return model_class(**obj_dict)
