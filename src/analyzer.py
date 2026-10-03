#!/usr/bin/env python3

import sys

from src.app import create_app
from src.extensions import db
from src.messaging import consume_events
from src.models import (
    AnalysisResult,
    NetworkObservation,
)


def calculate_analysis(observations):
    """
    Analyze a collection of network observations.
    """

    if not observations:
        return None

    response_times = [
        observation.response_time_ms
        for observation in observations
    ]

    successful_requests = [
        observation
        for observation in observations
        if 200 <= observation.http_status < 400
    ]

    sample_size = len(observations)

    average_response_ms = (
        sum(response_times) / sample_size
    )

    minimum_response_ms = min(response_times)
    maximum_response_ms = max(response_times)

    success_rate = (
        len(successful_requests)
        / sample_size
    ) * 100

    # Simple rule-based analysis suitable for the MVP.
    if (
        success_rate >= 95
        and average_response_ms <= 500
    ):
        status = "HEALTHY"

    elif (
        success_rate >= 80
        and average_response_ms <= 1000
    ):
        status = "WARNING"

    else:
        status = "CRITICAL"

    return {
        "sample_size": sample_size,
        "average_response_ms": average_response_ms,
        "minimum_response_ms": minimum_response_ms,
        "maximum_response_ms": maximum_response_ms,
        "success_rate": success_rate,
        "status": status,
    }


def save_analysis_result(data):
    """
    Save analyzed data to persistent storage.
    """

    result = AnalysisResult(
        sample_size=data["sample_size"],
        average_response_ms=data[
            "average_response_ms"
        ],
        minimum_response_ms=data[
            "minimum_response_ms"
        ],
        maximum_response_ms=data[
            "maximum_response_ms"
        ],
        success_rate=data["success_rate"],
        status=data["status"],
    )

    db.session.add(result)
    db.session.commit()
    db.session.refresh(result)

    return result


def analyze_once(app=None, limit=20):
    """
    Run one complete analysis cycle.
    """

    app = app or create_app()

    with app.app_context():

        statement = (
            db.select(NetworkObservation)
            .order_by(
                NetworkObservation.collected_at.desc()
            )
            .limit(limit)
        )

        observations = (
            db.session.execute(statement)
            .scalars()
            .all()
        )

        analysis = calculate_analysis(
            observations
        )

        if analysis is None:
            return None

        result = save_analysis_result(
            analysis
        )

        return result.to_dict()


def handle_event(event, app):
    """
    React to RabbitMQ events.
    """

    if event.get("type") != "observation.collected":
        return None

    return analyze_once(app=app)


def run_consumer():
    """
    Run analyzer as an asynchronous event consumer.
    """

    app = create_app()

    def callback(event):

        result = handle_event(
            event,
            app
        )

        if result:

            print(
                "HomePulse analysis completed:"
            )

            print(result)

    consume_events(callback)


if __name__ == "__main__":

    if "--consume" in sys.argv:

        run_consumer()

    else:

        result = analyze_once()

        if result:

            print(
                "HomePulse analysis successful:"
            )

            print(result)

        else:

            print(
                "No observations are available "
                "for analysis."
            )
