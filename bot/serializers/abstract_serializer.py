from abc import abstractmethod, ABC


class AbstractSerializer(ABC):
    @abstractmethod
    def serialize(self, obj: any) -> any:
        """Поддержка сериализации объектов, хранящихся в Redis."""

    @abstractmethod
    def deserialize(self, obj: any) -> any:
        """Поддержка десериализации объектов, хранящихся в Redis."""
