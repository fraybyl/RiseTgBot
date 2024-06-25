from orjson import orjson

from bot.serializers.abstract_serializer import AbstractSerializer


class JSONSerializer(AbstractSerializer):
    """Serialize values using JSON."""

    def serialize(self, obj: any) -> bytes:
        return orjson.dumps(obj)

    def deserialize(self, obj: str) -> any:
        """Deserialize values using JSON."""
        return orjson.loads(obj)