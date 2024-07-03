from orjson import orjson

from bot.serializers.abstract_serializer import AbstractSerializer


class JSONSerializer(AbstractSerializer):
    """Сериализация значений с помощью JSON."""

    def serialize(self, obj: any) -> bytes:
        """Сериализуйте значения с помощью JSON."""
        return orjson.dumps(obj)

    def deserialize(self, obj: str) -> any:
        """Десериализуйте значения с помощью JSON."""
        return orjson.loads(obj)
