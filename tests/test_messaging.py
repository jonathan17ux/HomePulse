from unittest.mock import MagicMock

from src.messaging import (
    publish_event,
)


def test_publish_event():

    fake_connection = MagicMock()

    fake_channel = MagicMock()

    fake_connection.channel.return_value = (
        fake_channel
    )

    connection_factory = MagicMock(
        return_value=fake_connection
    )

    result = publish_event(
        "observation.collected",
        {
            "observation_id": 1
        },
        url=(
            "amqp://guest:guest@"
            "localhost:5672/%2F"
        ),
        connection_factory=(
            connection_factory
        )
    )

    assert result is True

    fake_channel.queue_declare\
        .assert_called_once()

    fake_channel.basic_publish\
        .assert_called_once()

    fake_connection.close\
        .assert_called_once()
