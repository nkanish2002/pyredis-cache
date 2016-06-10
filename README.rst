pyredis-cache
=============

Python Cache client for redis.

Supports Python 3.5 and above.

Features
========

-  Automatically Sync data between the sync\_func and cache
-  Use of Async/Await for Asynchronous execution of sync\_func

Dependencies
============

-  `redis-py <https://github.com/andymccurdy/redis-py>`__
-  `hiredis-py <https://github.com/redis/hiredis-py>`__

Installation
============

1. Through pip: ``pip install pyredis-cache``

2. Manually: ``python setup.py install``. Install dependencies first

Getting Started
===============

-  Simple Redis Cache

.. code:: py

    # Import redis Connection pool and CacheClient.
    from redis import ConnectionPool
    from redis_cache import CacheClient

    import json

    # Initialize the Connection pool.
    redis_pool = ConnectionPool()

    # Create a data synchronisation function
    # The first argument should define the uniqueness of the data
    def sync_func(student_id, lots_of_args):
        # fetch the data however you want to
        return data # Lets assume that the data returned is of type `dict` 
     
    # Initialize the cache client
    cache = CacheClient(redis_pool, "Student", sync_func, set_func=json.dumps, get_func=json.loads, expire_time=10)
    # for persistent cache, assign 0 to expire_time (default)

    # This will set cache for ID: 12
    cache.set(12)

    # This will set cache for ID: 13, with custom data
    cache.set(13, data={"name":"John Doe", "age":16})

    # This will get cache for ID: 12 (no need to do a set, it will automatically set the data)
    cache.get(12)

    # The get function will pass extra arguments to the sync_func, same works with set.
    cache.get(14, age=15)

    # This will delete the cache for ID: 12
    cache.delete(12)

-  Caching into a single hash. I am still working on this to make a much
   more flexible caching mechanism

.. code:: py

    # Import redis Connection pool and HashCacheClient.
    from redis import ConnectionPool
    from redis_cache import CacheClient

    import json

    # Initialize the Connection pool.
    redis_pool = ConnectionPool()

    # Create a data synchronisation function
    # The first argument should define the uniqueness of the data
    def sync_func(student_id, lots_of_args):
        # fetch the data however you want to
        return data # Lets assume that the data returned is of type `dict` 
     
    # Initialize the cache client.
    hcache = HashCacheClient(redis_pool, "Class", "Student", sync_func, set_func=dumps, get_func=loads)
    # expire_time not supported.

    # This will set cache for ID: 12 for hash_id: 3
    hcache.set(3, 12)

    # This will get cache for ID: 12 for hash_id: 3 (no need to do a set, it will automatically set the data)
    hcache.get(3, 12)

    # This will delete the cache for ID: 12 for hash_id: 3
    hcache.delete(3, 12)

    # This will delete the hash with hash_id: 3
    hcache.delete_hash(3)

Terminology
===========

-  key: is the identifier for the cache object. eg. ``student`` (type
   string)
-  identity: is the index for a particular key. eg. Roll no. of a
   student ``12`` (type int)
-  sync\_func: function which will give data tto be stores in cache.
-  set\_func: data parsing function for setting data into cache. eg. if
   you want to set a dict value, you will have to set this as
   ``json.dumps``
-  get\_func: data parsing function for getting data into cache. eg. if
   you want to set a dict value, you will have to set this as
   ``json.loads``
-  hash\_key and hash\_id: Unique identifiers for the hash. eg.
   hash\_key can be ``grade12`` and hash\_id can be ``2``

Key and Identity are combined in a unique fashion to make the name
against which the cache object will be stored. Similarly for hash\_key
and hash\_id.

Async
=====

If your function is Async i.e. makes use of ``async`` and ``await``
coroutines (`PEP 492 <https://www.python.org/dev/peps/pep-0492/>`__).
You will have to use event loop to run use this functionality like
asyncio and tornado. You could do the following:-

.. code:: py

    cache = CacheClient(redis_pool, "Student", sync_func, set_func=json.dumps, get_func=json.loads, expire_time=10, asynchronous=True)

    async def some_func():
        data = await cache.get(23)

Note: the cache client is synchronous because redis servers are quite
fast. You can expect near 0 latency with the correct setup. Also the
creator of tornado-redis suggests this kind if architecture to reduce
the cost overhead caused by setting up callbacks. (see post:
http://stackoverflow.com/a/15596969/2248966)
