#!/usr/bin/env python3

import os
import time

import requests

from src.app import create_app
from src.extensions import db
from src.messaging import publish_event
from src.models import NetworkObservation


EXTERNAL_API_URL = os.getenv(
    "HOMEPULSE_EXTERNAL_API",
    "https://api.ipify.org?format=json"
)


def fetch_network_observation(
    get=requests.get
):
    """
    Fetch network data from an external REST API.
    """

    start_time = time.perf_counter()

    response = get(
        EXTERNAL_API_URL,
        timeout=5
    )

    response_time_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    response.raise_for_status()

    data = response.json()

    public_ip = data.get("ip")

    if not public_ip:

        raise ValueError(
            "External API response did not "
            "contain an IP address."
        )

    return {
        "public_ip": public_ip,
        "source": "api.ipify.org",
        "http_status": response.status_code,
        "response_time_ms": response_time_ms,
    }


def save_network_observation(data):
    """
    Persist collected network data.
    """

    observation = NetworkObservation(
        public_ip=data["public_ip"],
        source=data["source"],
        http_status=data["http_status"],
        response_time_ms=data[
            "response_time_ms"
        ],
    )

    db.session.add(observation)
    db.session.commit()
    db.session.refresh(observation)

    return observation


def collect_once(
    app=None,
    get=requests.get,
    publisher=publish_event
):
    """
    Perform one complete data collection cycle.
    """

    app = app or create_app()

    with app.app_context():

        data = fetch_network_observation(
            get=get
        )

        observation = (
            save_network_observation(data)
        )

        event_published = False

        if publisher:

            event_published = publisher(
                "observation.collected",
                {
                    "observation_id":
                        observation.id
                }
            )

        result = observation.to_dict()

        result["event_published"] = bool(
            event_published
        )

        return result


if __name__ == "__main__":

    try:

        observation = collect_once()

        print(
            "HomePulse collection successful:"
        )

        print(observation)

    except Exception as error:

        print(
            f"HomePulse collection failed: "
            f"{error}"
        )
