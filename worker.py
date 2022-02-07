import pika
import time

sleepTime = 10
print(' [*] Sleeping for %i seconds.' % sleepTime)
time.sleep(sleepTime)

print(' [*] Connecting to server ...')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit-flask'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

print('[*] Waiting for messages.')


def callback(ch, method, properties, body):
    print("[x] Received %s" % body)
    cmd = body.decode()
    print(cmd)

    print('[x] Done')
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)
channel.start_consuming()
