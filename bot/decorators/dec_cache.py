from datetime import timedelta
from functools import wraps

from bot.core.loader import redis_db
from bot.serializers.abstract_serializer import AbstractSerializer
from bot.serializers.orjson_serializer import JSONSerializer

DEFAULT_TTL = 120


async def set_redis_value(
        key: bytes | str, value: bytes | str, ttl: int | timedelta | None = DEFAULT_TTL, is_transaction: bool = False
) -> None:
    """Устанавливает значение в Redis с дополнительным временем жизни (TTL)."""
    async with redis_db.pipeline(transaction=is_transaction) as pipeline:
        await pipeline.set(key, value)
        if ttl:
            await pipeline.expire(key, ttl)
        await pipeline.execute()


def build_key(*args: tuple[str, any], **kwargs: dict[str, any]) -> str:
    """Постройте string key на основе предоставленных аргументов и аргументов ключевых слов."""
    args_str = ":".join(map(str, args))
    kwargs_str = ":".join(f"{key}={value}" for key, value in sorted(kwargs.items()))
    return f"{args_str}:{kwargs_str}"


def cached(
        ttl: int | timedelta | None = DEFAULT_TTL,
        namespace: str = "main",
        key_builder: callable = build_key,
        serializer: AbstractSerializer | None = None
) -> callable:
    """Кэширует возвращаемое значение функции в  key из module_name, function_name, и args."""
    if serializer is None:
        serializer = JSONSerializer()

    def decorator(func: callable) -> callable:
        @wraps(func)
        async def wrapper(*args: any, **kwargs: any) -> any:
            key = key_builder(*args, **kwargs)
            key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"

            cached_value = await redis_db.get(key)
            if cached_value is not None:
                return serializer.deserialize(cached_value)

            result = await func(*args, **kwargs)

            await set_redis_value(
                key=key,
                value=serializer.serialize(result),
                ttl=ttl,
            )

            return result

        return wrapper

    return decorator


async def clear_cache(
        func: callable,
        *args: any,
        **kwargs: any,
) -> None:
    """Очистить кэш для определенной функции и аргументов.

    Параметры
    ----------
    - func (вызываемая функция): Целевая функция, для которой необходимо очистить кэш.
    - args (any): Позиционные аргументы, передаваемые функции.
    - kwargs (any): Аргументы ключевых слов, передаваемые функции.

    Аргументы ключевых слов:
    - namespace (str, optional): Строка, указывающая пространство имен для кэша. По умолчанию - "main".
    """
    namespace: str = kwargs.get("namespace", "main")

    key = build_key(*args, **kwargs)
    key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"
    await redis_db.delete(key)
