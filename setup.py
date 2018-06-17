
import psycopg2

from config import Config
import datetime
from pymongo import MongoClient
from pymemcache.client import base

import pika
import redis
import json


def setup_postgres():
    conn = psycopg2.connect(
        database=Config.db,
        user=Config.user,
        password=Config.password,
        host=Config.host)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS test (
            id SERIAL PRIMARY KEY,
            message VARCHAR(255) NOT NULL,
            created_at timestamp NOT NULL default CURRENT_TIMESTAMP
        );
        """)
    conn.commit()
    conn.close()
    print('POSTGRES [ok]')


def check_mongo():
    client = MongoClient(Config.mongo_uri)
    db = client.test
    collection = db.test
    collection.insert_one({
        'message': 'Test Mongo setup',
        'created_at': datetime.datetime.utcnow()
    })
    print('MONGO [ok]')


def check_rabbitmq():
    connection = pika.BlockingConnection(pika.URLParameters(Config.amqp_uri))
    channel = connection.channel()
    channel.queue_declare(queue='test')
    channel.basic_publish(exchange='',
                          routing_key='test',
                          body='A new day, a new start!')
    connection.close()
    print('RABBITMQ [ok]')


def check_redis():
    cache = redis.Redis.from_url(Config.redis_uri)
    messages = ["hello, one", "hello, two", "hello, three"]
    cache.set('messages', json.dumps(messages))
    data = cache.get('messages')
    stored_messages = json.loads(data)
    print(stored_messages)
    print('REDIS [ok]')


def check_memcache():
    cache = base.Client(
        (Config.memcache_host, Config.memcache_port))
    messages = ["hello, one", "hello, two", "hello, three"]
    cache.set('messages', json.dumps(messages))
    data = cache.get('messages')
    stored_messages = json.loads(data)
    print(stored_messages)
    print('MEMCACHE [ok]')


if __name__ == '__main__':
    setup_postgres()
    check_mongo()
    check_rabbitmq()
    check_redis()
    check_memcache()
