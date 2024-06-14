import redis.asyncio

class RedisCache:
    def __init__(self, host='localhost', port=6379, password=None, db=0):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.client = None

    async def connect(self):
        self.client = redis.asyncio.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            decode_responses=True  # Automatically decode responses from Redis
        )

    async def close(self):
        if self.client:
            await self.client.close()

    async def set(self, key, value, expire=None):
        try:
            if expire:
                await self.client.setex(key, value, expire)
            else:
                await self.client.set(key, value)
        except redis.RedisError as e:
            print(f"Error setting value in Redis: {e}")
            raise  # Propagate the error for higher-level handling

    async def get(self, key):
        try:
            return await self.client.get(key)
        except redis.RedisError as e:
            print(f"Error getting value from Redis: {e}")
            raise  # Propagate the error for higher-level handling

    async def delete(self, key):
        try:
            await self.client.delete(key)
        except redis.RedisError as e:
            print(f"Error deleting key from Redis: {e}")
            raise  # Propagate the error for higher-level handling

    async def exists(self, key):
        try:
            return await self.client.exists(key)
        except redis.RedisError as e:
            print(f"Error checking existence in Redis: {e}")
            raise  # Propagate the error for higher-level handling