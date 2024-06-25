import orjson
from datetime import timedelta
from functools import wraps

from bot.core.loader import redis_cache
from bot.serializers.abstract_serializer import AbstractSerializer
from bot.serializers.orjson_serializer import JSONSerializer

DEFAULT_TTL = 60


async def set_redis_value(
        key: bytes | str, value: bytes | str, ttl: int | timedelta | None = DEFAULT_TTL, is_transaction: bool = False
) -> None:
    """Set a value in Redis with an optional time-to-live (TTL)."""
    async with redis_cache.pipeline(transaction=is_transaction) as pipeline:
        await pipeline.set(key, value)
        if ttl:
            await pipeline.expire(key, ttl)
        await pipeline.execute()


def build_key(*args: tuple[str, any], **kwargs: dict[str, any]) -> str:
    """Build a string key based on provided arguments and keyword arguments."""
    args_str = ":".join(map(str, args))
    kwargs_str = ":".join(f"{key}={value}" for key, value in sorted(kwargs.items()))
    return f"{args_str}:{kwargs_str}"


def cached(
        ttl: int | timedelta | None = DEFAULT_TTL,
        namespace: str = "main",
        key_builder: callable = build_key,
        serializer: AbstractSerializer | None = None
) -> callable:
    """Caches the function's return value into a key generated with module_name, function_name, and args."""
    if serializer is None:
        serializer = JSONSerializer()
    def decorator(func: callable) -> callable:
        @wraps(func)
        async def wrapper(*args: any, **kwargs: any) -> any:
            key = key_builder(*args, **kwargs)
            key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"

            # Check if the key is in the cache
            cached_value = await redis_cache.get(key)
            if cached_value is not None:
                return serializer.deserialize(cached_value)

            # If not in cache, call the original function
            result = await func(*args, **kwargs)

            # Store the result in Redis
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
    """Clear the cache for a specific function and arguments.

    Parameters
    ----------
    - func (callable): The target function for which the cache needs to be cleared.
    - args (any): Positional arguments passed to the function.
    - kwargs (any): Keyword arguments passed to the function.

    Keyword Arguments:
    - namespace (str, optional): A string indicating the namespace for the cache. Defaults to "main".
    """
    namespace: str = kwargs.get("namespace", "main")

    key = build_key(*args, **kwargs)
    key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"
    await redis_cache.delete(key)
