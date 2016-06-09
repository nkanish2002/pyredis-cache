from redis import StrictRedis, ConnectionPool, RedisError
import logging
from .utils import key_generator, default_passage


class HashCacheClient:
    """
    HashCacheClient can be used to cache contextually similar data under a common hash name.
        *   Automatically Sync data between the sync_func and cache
        *   Use of Async/Await for Asynchronous execution of sync_func
    """
    def __init__(self, redis_pool: ConnectionPool, hash_key, key, sync_func, log=logging, set_func=default_passage,
                 get_func=default_passage, asynchronous=False):
        """
        Initializer for HashCacheClient
        :param redis_pool: Redis Pool object
        :param hash_key: Unique Hash key for the data
        :param key: Operation Key specific to this cache
        :param sync_func: Data function
        :param log: log object (default logging)
        :param set_func: Function for Manipulation of data being set in the cache. (Default: None)
        :param get_func: Function for Manipulation of data being set in the cache. (Default: None)
        :param asynchronous: To enable Asynchronous execution of sync function. (Default: True (bool))
        """
        self.redis_pool = redis_pool
        self.hash_key = hash_key
        self.key = key
        self.sync_func = sync_func
        self.set_func = set_func
        self.get_func = get_func
        if asynchronous:
            self.set = self.async_set
            self.get = self.async_get
        else:
            self.set = self.sync_set
            self.get = self.sync_get
        self.log = log

    def sync_set(self, hash_id, identity, *args, data=None, **kwargs):
        """
        For setting data
        :param hash_id: Unique Hash key for the data
        :param identity: Unique Integer for the data
        :param args: Args for the sync function. (Default: None)
        :param data: Data to be set. By default it will pick data from the sync_function. (Default: None)
        :param kwargs: Args for the sync function.
        """
        if data is None:
            data = self.sync_func(identity, *args, **kwargs)
        redis = StrictRedis(connection_pool=self.redis_pool)
        hash_key = key_generator(self.hash_key, hash_id)
        key = key_generator(self.key, identity)
        try:
            redis.hset(hash_key, key, self.set_func(data))
            return 1
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            return 0
        finally:
            del redis

    def sync_get(self, hash_id, identity, *args, **kwargs):
        """
        For getting data from cache
        :param hash_id: Unique Hash key for the data
        :param identity: Unique Integer for the data
        :param args: Args for the sync function. (Default: None)
        """
        redis = StrictRedis(connection_pool=self.redis_pool)
        hash_key = key_generator(self.hash_key, hash_id)
        key = key_generator(self.key, identity)
        try:
            if redis.hexists(hash_key, key):
                data = self.get_func(redis.hget(hash_key, key))
            else:
                data = self.sync_func(identity, *args, **kwargs)
                redis.hset(hash_key, key, self.set_func(data))
            if data is not None or data != "":
                return data
            return None
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            data = self.sync_func(identity, args)
            return data
        finally:
            del redis

    async def async_set(self, hash_id, identity, *args, data=None, **kwargs):
        """
        For setting data
        :param hash_id: Unique Hash key for the data
        :param identity: Unique Integer for the data
        :param args: Args for the sync function. (Default: None)
        :param data: Data to be set. By default it will pick data from the sync_function. (Default: None)
        :param kwargs: Args for the sync function.
        """
        if data is None:
            data = await self.sync_func(identity, *args, **kwargs)
        redis = StrictRedis(connection_pool=self.redis_pool)
        hash_key = key_generator(self.hash_key, hash_id)
        key = key_generator(self.key, identity)
        try:
            redis.hset(hash_key, key, self.set_func(data))
            return 1
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            return 0
        finally:
            del redis

    async def async_get(self, hash_id, identity, *args, **kwargs):
        """
        For getting data from cache
        :param hash_id: Unique Hash key for the data
        :param identity: Unique Integer for the data
        :param args: Args for the sync function. (Default: None)
        """
        redis = StrictRedis(connection_pool=self.redis_pool)
        hash_key = key_generator(self.hash_key, hash_id)
        key = key_generator(self.key, identity)
        try:
            if redis.hexists(hash_key, key):
                data = self.get_func(redis.hget(hash_key, key))
            else:
                data = await self.sync_func(identity, *args, **kwargs)
                redis.hset(hash_key, key, self.set_func(data))
            if data is not None or data != "":
                return data
            return None
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            data = await self.sync_func(identity, args)
            return data
        finally:
            del redis

    def delete(self, hash_id, identity):
        """
        For Deleting a key inside the hash
        :param hash_id:
        :param identity:
        :return:
        """
        redis = StrictRedis(connection_pool=self.redis_pool)
        hash_key = key_generator(self.hash_key, hash_id)
        key = key_generator(self.key, identity)
        try:
            i = redis.hdel(hash_key, key)
            return i
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            return 0
        finally:
            del redis

    def delete_hash(self, hash_id):
        """
        For deleting the hash
        :param hash_id:
        :return:
        """
        redis = StrictRedis(connection_pool=self.redis_pool)
        hash_key = key_generator(self.hash_key, hash_id)
        try:
            i = redis.delete(hash_key)
            return i
        except RedisError as re:
            self.log.error("[REDIS] %s", str(re))
            return 0
        finally:
            del redis
