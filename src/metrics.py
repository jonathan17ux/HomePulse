from flask import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    generate_latest,
)
from sqlalchemy import func

from src.extensions import db
from src.models import (
    AnalysisResult,
    NetworkObservation,
)


HTTP_REQUESTS = Counter(
    "homepulse_http_requests_total",
    "Total HTTP requests processed by HomePulse.",
    [
        "method",
        "endpoint",
        "status_code",
    ]
)


OBSERVATIONS_STORED = Gauge(
    "homepulse_observations_stored",
    "Number of network observations stored."
)


LATEST_RESPONSE_TIME = Gauge(
    "homepulse_latest_response_time_ms",
    "Latest observed external API response time."
)


ANALYSES_STORED = Gauge(
    "homepulse_analysis_results_stored",
    "Number of analysis results stored."
)


LATEST_SUCCESS_RATE = Gauge(
    "homepulse_latest_success_rate_percent",
    "Latest calculated network success rate."
)


def record_http_request(
    method,
    endpoint,
    status_code
):

    HTTP_REQUESTS.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code)
    ).inc()


def update_database_metrics():

    observation_count = db.session.scalar(
        db.select(func.count())
        .select_from(NetworkObservation)
    ) or 0

    analysis_count = db.session.scalar(
        db.select(func.count())
        .select_from(AnalysisResult)
    ) or 0

    OBSERVATIONS_STORED.set(
        observation_count
    )

    ANALYSES_STORED.set(
        analysis_count
    )

    latest_observation = (
        db.session.execute(
            db.select(NetworkObservation)
            .order_by(
                NetworkObservation.collected_at.desc()
            )
            .limit(1)
        )
        .scalars()
        .first()
    )

    if latest_observation:

        LATEST_RESPONSE_TIME.set(
            latest_observation.response_time_ms
        )

    latest_analysis = (
        db.session.execute(
            db.select(AnalysisResult)
            .order_by(
                AnalysisResult.analyzed_at.desc()
            )
            .limit(1)
        )
        .scalars()
        .first()
    )

    if latest_analysis:

        LATEST_SUCCESS_RATE.set(
            latest_analysis.success_rate
        )


def metrics_response():

    update_database_metrics()

    return Response(
        generate_latest(),
        content_type=CONTENT_TYPE_LATEST
    )
