#!/usr/bin/env python3

import json
import os

import pika


QUEUE_NAME = os.getenv(
    "HOMEPULSE_QUEUE",
    "homepulse.events"
)


def publish_event(
    event_type,
    payload,
    url=None,
    connection_factory=pika.BlockingConnection
):
    """
    Publish a HomePulse event to RabbitMQ.

    If RabbitMQ is not configured, the application
    continues operating without messaging.
    """

    rabbitmq_url = (
        url
        or os.getenv("RABBITMQ_URL")
    )

    if not rabbitmq_url:
        return False

    try:

        parameters = pika.URLParameters(
            rabbitmq_url
        )

        connection = connection_factory(
            parameters
        )

        channel = connection.channel()

        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True
        )

        message = {
            "type": event_type,
            "payload": payload,
        }

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json"
            )
        )

        connection.close()

        return True

    except pika.AMQPError as error:

        print(
            f"RabbitMQ publish failed: {error}"
        )

        return False


def consume_events(
    handler,
    url=None
):
    """
    Consume HomePulse events from RabbitMQ.
    """

    rabbitmq_url = (
        url
        or os.getenv("RABBITMQ_URL")
    )

    if not rabbitmq_url:

        raise RuntimeError(
            "RABBITMQ_URL is not configured."
        )

    parameters = pika.URLParameters(
        rabbitmq_url
    )

    connection = pika.BlockingConnection(
        parameters
    )

    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True
    )

    channel.basic_qos(
        prefetch_count=1
    )

    def callback(
        ch,
        method,
        properties,
        body
    ):

        try:

            event = json.loads(
                body.decode("utf-8")
            )

            handler(event)

            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

        except Exception as error:

            print(
                f"Event processing failed: {error}"
            )

            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False
            )

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback
    )

    print(
        "HomePulse analyzer is waiting "
        "for events..."
    )

    channel.start_consuming()
