import json
from typing import Any

import redis


class Repo:
    def __init__(self):
        self.db = {}

    def set(self, key: str, value):
        self.db[key] = value

    def get(self, key: str):
        return self.db.get(key)

    def delete(self, key: str):
        del self.db[key]


class RedisRepo:
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 1):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def set(self, key: str, value: dict[str, Any]):
        _value = json.dumps(value)
        self.redis.set(key, _value)

    def get(self, key: str):
        _value: bytes = self.redis.get(key)  # type: ignore
        if _value is None:
            return None
        return json.loads(_value)

    def delete(self, key: str): ...
