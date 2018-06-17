#!/usr/bin/env python
import pika
from config import Config


rabbitmq_connection = pika.BlockingConnection(
    pika.URLParameters(Config.amqp_uri))
rabbitmq_channel = rabbitmq_connection.channel()
rabbitmq_channel.queue_declare(queue='test')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


if __name__ == '__main__':
    rabbitmq_channel.basic_consume(callback,
                                   queue='test',
                                   no_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    rabbitmq_channel.start_consuming()
