from dyte_project.celery import app
from logs_handler.models import Log
from elasticsearch import helpers
from dyte_project.settings import (
    elasticsearch_instance,
    pika_parameters,
    LOG_MESSAGES_QUEUE_NAME,
    ELASTICSEARCH_INDEX_NAME
)
import pika
import json

@app.task(name="write_records_to_db", bind=True)
def consume_first_100_messages(self):

    batch_size = 0
    messages_fetched = 0
    messages = []
    objects_to_be_created = []

    def callback(ch, method, properties, body):

        nonlocal messages_fetched
        nonlocal batch_size
        nonlocal messages
        nonlocal objects_to_be_created

        messages_fetched = messages_fetched+1
        ch.basic_ack(delivery_tag=method.delivery_tag)
        log_payload = (json.loads(body))
        objects_to_be_created.append(
            Log(
                level = log_payload['level'],
                message = log_payload['message'],
                resourceId = log_payload['resourceId'],
                timestamp = log_payload['timestamp'],
                traceId = log_payload['traceId'],
                spanId = log_payload['spanId'],
                commit = log_payload['commit'],
                metadata = log_payload['metadata']
            )
        )
        messages.append(log_payload)
        if messages_fetched == batch_size:
            ch.stop_consuming()
    connection = pika.BlockingConnection(pika_parameters)
    channel = connection.channel()
    queue = channel.queue_declare(LOG_MESSAGES_QUEUE_NAME)
    total_messages_in_queue = queue.method.message_count
    batch_size = 100 if total_messages_in_queue > 100 else total_messages_in_queue
    if batch_size > 0:
        channel.basic_qos(prefetch_count=batch_size)
        channel.basic_consume(queue=LOG_MESSAGES_QUEUE_NAME, on_message_callback=callback)
        channel.start_consuming()
        messages_fetched = 0
        batch_size = 0
        Log.objects.bulk_create(objects_to_be_created)
        if not elasticsearch_instance.indices.exists(index=ELASTICSEARCH_INDEX_NAME):
            elasticsearch_instance.indices.create(index=ELASTICSEARCH_INDEX_NAME)
        helpers.bulk(
            elasticsearch_instance,
            messages,
            index=ELASTICSEARCH_INDEX_NAME
        )
        print("logs Created to db and elasticsearch")
        messages = []
        objects_to_be_created = []
