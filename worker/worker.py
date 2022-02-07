import pika
from sqlalchemy import create_engine, Column, String, Integer, Identity
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

'''
Code Block: Wait for server to turn on
Comment: Detached this since docker has a 'depend_on' method

import time

sleepTime = 10
print(' [*] Sleeping for %i seconds.' % sleepTime)
time.sleep(sleepTime)
'''

# rabbitMQ connection
print('[*] Connecting to server ...')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit-flask'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

# PostgreSQL connection
print('[*] Connecting to database ...')
db_string = "postgresql://rabbit:rabbitmqDatabase@postgres-flask:5432/rabbitTasks"

db = create_engine(db_string)
base = declarative_base()
Session = sessionmaker(db)
session = Session()


# DB Model
class Person(base):
    __tablename__ = 'people'
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True, )
    name = Column(String)


# Create Model/Tables
base.metadata.create_all(db)

print('[*] Waiting for messages.')


def callback(ch, method, properties, body):
    print("[x] Received %s" % body)
    name = body.decode()
    new_person = Person(name=name)
    session.add(new_person)
    session.commit()
    print('[x] Done')
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)
channel.start_consuming()
