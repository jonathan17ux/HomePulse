from unittest.mock import MagicMock

from src.collector import collect_once
from src.extensions import db
from src.models import NetworkObservation


def test_collector_stores_external_data(
    app
):

    fake_response = MagicMock()

    fake_response.status_code = 200

    fake_response.json.return_value = {
        "ip": "203.0.113.25"
    }

    fake_response.raise_for_status.return_value = None

    fake_get = MagicMock(
        return_value=fake_response
    )

    result = collect_once(
        app=app,
        get=fake_get
    )

    with app.app_context():

        saved = db.session.get(
            NetworkObservation,
            result["id"]
        )

        assert saved is not None

        assert saved.public_ip == \
            "203.0.113.25"

        assert saved.http_status == 200

        assert saved.source == \
            "api.ipify.org"
        
def test_collector_publishes_event(
    app
):

    from unittest.mock import (
        MagicMock
    )

    fake_response = MagicMock()

    fake_response.status_code = 200

    fake_response.json.return_value = {
        "ip": "203.0.113.99"
    }

    fake_response.raise_for_status\
        .return_value = None

    fake_get = MagicMock(
        return_value=fake_response
    )

    fake_publisher = MagicMock(
        return_value=True
    )

    result = collect_once(
        app=app,
        get=fake_get,
        publisher=fake_publisher
    )

    assert (
        result["event_published"]
        is True
    )

    fake_publisher\
        .assert_called_once()