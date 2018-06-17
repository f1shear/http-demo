
import psycopg2

from config import Config
import datetime
from pymongo import MongoClient
from pymemcache.client import base

import pika
import redis
import json
import logging


pg_conn = psycopg2.connect(
    database=Config.db,
    user=Config.user,
    password=Config.password,
    host=Config.host)

mongo_client = MongoClient(Config.mongo_uri)


rabbitmq_connection = pika.BlockingConnection(
    pika.URLParameters(Config.amqp_uri))
rabbitmq_channel = rabbitmq_connection.channel()
rabbitmq_channel.queue_declare(queue='test')

redis_cache = redis.Redis.from_url(Config.redis_uri)


mem_cache = base.Client(
    (Config.memcache_host, Config.memcache_port))


class DataStore(object):

    @classmethod
    def store_message(cls, datastore, message):
        logging.info(
            '****Saving message "%s" to %s' % (message, datastore))
        if datastore == 'postgresql':
            cls.store_pg(message)
        elif datastore == 'mongo':
            cls.store_mongo(message)
        elif datastore == 'rabbitmq':
            cls.store_rabbitmq(message)
        elif datastore == 'redis':
            cls.store_redis(message)
        elif datastore == 'memcache':
            cls.store_memcache(message)
        else:
            raise Exception("Unknown DataStore")

    @staticmethod
    def store_pg(message):
        # need to manage connections better
        cur = pg_conn.cursor()
        cur.execute(
            """
                INSERT INTO
                test
                (message)
                VALUES
            ('%s')
            """ % message)
        pg_conn.commit()

    @staticmethod
    def store_mongo(message):

        db = mongo_client['test']
        collection = db['test']
        collection.insert_one({
            'message': message,
            'created_at': datetime.datetime.utcnow()
        })

    @staticmethod
    def store_rabbitmq(message):
        rabbitmq_channel.basic_publish(exchange='',
                                       routing_key='test',
                                       body=message)

    @staticmethod
    def store_redis(message):
        messages = redis_cache.get('messages')
        if messages:
            messages = json.loads(messages)
        else:
            messages = []
        messages.append(message)
        redis_cache.set('messages', json.dumps(messages))

    @staticmethod
    def store_memcache(message):
        mem_cache = base.Client(
            (Config.memcache_host, Config.memcache_port))
        messages = mem_cache.get('messages')
        if messages:
            messages = json.loads(messages)
        else:
            messages = []
        messages.append(message)
        mem_cache.set('messages', json.dumps(messages))
