from abc import abstractmethod, ABC


class AbstractSerializer(ABC):
    @abstractmethod
    def serialize(self, obj: any) -> any:
        """Support for serializing objects stored in Redis."""

    @abstractmethod
    def deserialize(self, obj: any) -> any:
        """Support for deserializing objects stored in Redis."""
