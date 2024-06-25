from orjson import orjson

from bot.database.base_model import model_registry
from bot.serializers.abstract_serializer import AbstractSerializer


class SQLSerializer(AbstractSerializer):
    """Serialize values using to_dict and orjson."""

    def serialize(self, obj: any) -> bytes:
        def default(obj):
            if hasattr(obj, 'as_dict'):
                data = obj.as_dict
                data['_model'] = obj.__class__.__name__
                return data
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

        return orjson.dumps(obj, default=default, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS)

    def deserialize(self, data: bytes) -> any:
        obj_dict_or_list = orjson.loads(data)

        if isinstance(obj_dict_or_list, list):
            return [self._deserialize_single(obj_dict) for obj_dict in obj_dict_or_list]
        else:
            return self._deserialize_single(obj_dict_or_list)

    @staticmethod
    def _deserialize_single(obj_dict: dict) -> any:
        model_name = obj_dict.pop('_model', None)

        if model_name is None:
            raise ValueError("Deserialized data does not contain model information")

        model_class = model_registry.get(model_name)

        if model_class is None:
            raise ValueError(f"Unknown model: {model_name}")

        return model_class(**obj_dict)

