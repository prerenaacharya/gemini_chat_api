import redis
from rq import Worker, Queue, Connection

listen = ['default']
redis_conn = redis.Redis()
with Connection(redis_conn):
    worker = Worker(map(Queue, listen))
    worker.work()
