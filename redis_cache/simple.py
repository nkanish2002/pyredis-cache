from redis import StrictRedis, ConnectionPool, RedisError
import logging

from .utils import key_generator, default_passage


class CacheClient:
    """
    CacheClient is a redis based simple cache client. It has the following features:
        *   Automatically Sync data between the sync_func and cache
        *   Use of Async/Await for Asynchronous execution of sync_func
    """

    def __init__(self, redis_pool: ConnectionPool, key, sync_func, log=logging, set_func=default_passage,
                 get_func=default_passage, expire_time=0, asynchronous=False):
        """
        Initializer for CacheClient
        :param redis_pool: Redis Pool object
        :param key: Operation Key specific to this cache
        :param log: log object (default logging)
        :param sync_func: Data function
        :param set_func: Function for Manipulation of data being set in the cache. (Default: None)
        :param get_func: Function for Manipulation of data being set in the cache. (Default: None)
        :param expire_time: cache expiration time in seconds.
        :param asynchronous: To enable Asynchronous execution of sync function. (Default: True (bool))
        """
        self.redis_pool = redis_pool
        self.key = key
        self.sync_func = sync_func
        self.set_func = set_func
        self.get_func = get_func
        self.expire = bool(expire_time)
        self.expire_time = expire_time
        if asynchronous:
            self.set = self.async_set
            self.get = self.async_get
        else:
            self.set = self.sync_set
            self.get = self.sync_get
        self.log = log

    def _setex(self, redis: StrictRedis, name, value):
        pipe = redis.pipeline()
        pipe.set(name, value)
        pipe.expire(name, self.expire_time)
        response = pipe.execute()
        del pipe
        return response

    def sync_set(self, identity, *args, data=None, **kwargs):
        """
        For setting data
        :param identity: Unique Integer for the data
        :param args: Args for the sync function. (Default: None)
        :param data: Data to be set. By default it will pick data from the sync_function. (Default: None)
        """
        if data is None:
            data = self.sync_func(identity, *args, **kwargs)
        redis = StrictRedis(connection_pool=self.redis_pool)
        key = key_generator(self.key, identity)
        try:
            if self.expire:
                self._setex(redis, key, self.set_func(data))
            else:
                redis.set(key, self.set_func(data))
            return 1
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            return 0
        finally:
            del redis

    def sync_get(self, identity, *args, **kwargs):
        """
        For getting data from cache
        :param identity: Unique Integer for the data
        :param args: Args for the sync function. (Default: None)
        """
        redis = StrictRedis(connection_pool=self.redis_pool)
        key = key_generator(self.key, identity)
        try:
            if redis.exists(key):
                data = self.get_func(redis.get(key))
            else:
                data = self.sync_func(identity, *args, **kwargs)
                if self.expire:
                    self._setex(redis, key, self.set_func(data))
                else:
                    redis.set(key, self.set_func(data))
            if data is not None or data != "":
                return data
            return None
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            data = self.sync_func(identity, args)
            return data
        finally:
            del redis

    async def async_set(self, identity, *args, data=None, **kwargs):
        """
        For setting data
        :param identity: Unique Integer for the data
        :param args: Args for the sync function. (Default: None)
        :param data: Data to be set. By default it will pick data from the sync_function. (Default: None)
        """
        if data is None:
            data = await self.sync_func(identity, *args, **kwargs)
        redis = StrictRedis(connection_pool=self.redis_pool)
        key = key_generator(self.key, identity)
        try:
            if self.expire:
                self._setex(redis, key, self.set_func(data))
            else:
                redis.set(key, self.set_func(data))
            return 1
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            return 0
        finally:
            del redis

    async def async_get(self, identity, *args, **kwargs):
        """
        For getting data from cache
        :param identity: Unique Integer for the data
        :param args: Args for the sync function. (Default: None)
        """
        redis = StrictRedis(connection_pool=self.redis_pool)
        key = key_generator(self.key, identity)
        try:
            if redis.exists(key):
                data = self.get_func(redis.get(key))
            else:
                data = await self.sync_func(identity, *args, **kwargs)
                if self.expire:
                    self._setex(redis, key, self.set_func(data))
                else:
                    redis.set(key, self.set_func(data))
            if data is not None or data != "":
                return data
            return None
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            data = await self.sync_func(identity, args)
            return data
        finally:
            del redis

    def delete(self, identity):
        """
        For deleting a key
        :param identity:
        :return:
        """
        redis = StrictRedis(connection_pool=self.redis_pool)
        key = key_generator(self.key, identity)
        try:
            i = redis.delete(key, key)
            return i
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            return 0
        finally:
            del redis
