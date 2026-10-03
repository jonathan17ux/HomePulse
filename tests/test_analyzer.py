from types import SimpleNamespace

from src.analyzer import (
    analyze_once,
    calculate_analysis,
)
from src.extensions import db
from src.models import (
    AnalysisResult,
    NetworkObservation,
)


def test_calculate_analysis():

    observations = [
        SimpleNamespace(
            response_time_ms=100,
            http_status=200
        ),
        SimpleNamespace(
            response_time_ms=200,
            http_status=200
        ),
        SimpleNamespace(
            response_time_ms=300,
            http_status=200
        ),
    ]

    result = calculate_analysis(
        observations
    )

    assert result["sample_size"] == 3

    assert (
        result["average_response_ms"]
        == 200
    )

    assert (
        result["minimum_response_ms"]
        == 100
    )

    assert (
        result["maximum_response_ms"]
        == 300
    )

    assert (
        result["success_rate"]
        == 100
    )

    assert (
        result["status"]
        == "HEALTHY"
    )


def test_analyzer_stores_result(
    app
):

    with app.app_context():

        db.session.add_all([
            NetworkObservation(
                public_ip="203.0.113.1",
                source="test",
                http_status=200,
                response_time_ms=100
            ),
            NetworkObservation(
                public_ip="203.0.113.1",
                source="test",
                http_status=200,
                response_time_ms=200
            ),
        ])

        db.session.commit()

    result = analyze_once(
        app=app
    )

    assert result is not None

    with app.app_context():

        saved = db.session.get(
            AnalysisResult,
            result["id"]
        )

        assert saved is not None

        assert saved.sample_size == 2

        assert saved.status == "HEALTHY"
