

class Config(object):
    # postgres specific
    db = 'test'
    user = 'test'
    password = 'test'
    host = 'localhost'
    # mongo specific
    mongo_uri = 'mongodb://localhost:27017/'
    # rabbitmq specific
    amqp_uri = 'amqp://guest:guest@127.0.0.1:5672/'
    # redis specific
    redis_uri = 'redis://127.0.0.1:6379'
    # memcache specific
    memcache_host = 'localhost'
    memcache_port = 11211
