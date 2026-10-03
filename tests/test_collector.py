from unittest.mock import MagicMock

from src.collector import (
    EXTERNAL_API_URL,
    fetch_network_observation
)


def test_fetch_network_observation():

    fake_response = MagicMock()

    fake_response.status_code = 200

    fake_response.json.return_value = {
        "ip": "203.0.113.10"
    }

    fake_response.raise_for_status.return_value = None

    fake_get = MagicMock(
        return_value=fake_response
    )

    observation = fetch_network_observation(
        get=fake_get
    )

    assert observation["public_ip"] == \
        "203.0.113.10"

    assert observation["source"] == \
        "api.ipify.org"

    assert observation["http_status"] == 200

    assert observation["response_time_ms"] >= 0

    fake_get.assert_called_once_with(
        EXTERNAL_API_URL,
        timeout=5
    )
