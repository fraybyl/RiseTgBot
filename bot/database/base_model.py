from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
model_registry = {}


class BaseModel(AsyncAttrs, Base):
    __abstract__ = True

    @property
    def as_dict(self):
        result = {}
        for key, value in self.__mapper__.c.items():
            column_value = getattr(self, key)
            if isinstance(column_value, Decimal):
                result[key] = float(column_value)
            elif isinstance(column_value, datetime):
                result[key] = column_value.isoformat()
            else:
                result[key] = column_value
        return result

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        model_registry[cls.__name__] = cls  # Register the model class
