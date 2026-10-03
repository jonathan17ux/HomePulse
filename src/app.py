#!/usr/bin/env python3

import os

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from src.extensions import db, migrate
from src.metrics import (
    metrics_response,
    record_http_request,
)
from src.models import (
    AnalysisResult,
    NetworkObservation,
)


def create_app(test_config=None):

    app = Flask(
        __name__,
        instance_relative_config=True
    )

    database_url = os.getenv(
        "DATABASE_URL"
    )

    if (
        database_url
        and database_url.startswith(
            "postgres://"
        )
    ):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    # Heroku Postgres requires SSL.
    if (
        database_url
        and database_url.startswith(
            "postgresql://"
        )
        and "sslmode=" not in database_url
    ):

        separator = (
            "&"
            if "?" in database_url
            else "?"
        )

        database_url = (
            f"{database_url}"
            f"{separator}sslmode=require"
        )

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=(
            database_url
            or "sqlite:///homepulse.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(
        app.instance_path,
        exist_ok=True
    )

    db.init_app(app)
    migrate.init_app(app, db)

    register_routes(app)

    return app


def get_recent_observations(
    limit=10
):

    statement = (
        db.select(NetworkObservation)
        .order_by(
            NetworkObservation.collected_at.desc()
        )
        .limit(limit)
    )

    return (
        db.session.execute(statement)
        .scalars()
        .all()
    )


def get_latest_analysis():

    statement = (
        db.select(AnalysisResult)
        .order_by(
            AnalysisResult.analyzed_at.desc()
        )
        .limit(1)
    )

    return (
        db.session.execute(statement)
        .scalars()
        .first()
    )


def register_routes(app):

    @app.after_request
    def capture_metrics(response):

        record_http_request(
            request.method,
            request.endpoint or "unknown",
            response.status_code
        )

        return response

    @app.route("/")
    def main():

        return render_template(
            "index.html",
            observations=(
                get_recent_observations()
            ),
            latest_analysis=(
                get_latest_analysis()
            ),
            echoed_input=None
        )

    @app.route(
        "/echo_user_input",
        methods=["POST"]
    )
    def echo_input():

        input_text = request.form.get(
            "user_input",
            ""
        ).strip()

        if not input_text:
            input_text = (
                "No device name entered"
            )

        return render_template(
            "index.html",
            observations=(
                get_recent_observations()
            ),
            latest_analysis=(
                get_latest_analysis()
            ),
            echoed_input=input_text
        )

    @app.route("/health")
    def health():

        try:

            db.session.execute(
                db.select(1)
            )

            return jsonify({
                "status": "healthy",
                "service": "HomePulse",
                "database": "connected",
            }), 200

        except Exception:

            return jsonify({
                "status": "unhealthy",
                "service": "HomePulse",
                "database": "unavailable",
            }), 503

    @app.route(
        "/api/observations"
    )
    def observations_api():

        observations = (
            get_recent_observations(
                limit=50
            )
        )

        return jsonify([
            observation.to_dict()
            for observation
            in observations
        ])

    @app.route(
        "/api/analysis"
    )
    def analysis_api():

        analysis = (
            get_latest_analysis()
        )

        if analysis is None:

            return jsonify({
                "status": "not_available"
            })

        return jsonify(
            analysis.to_dict()
        )

    @app.route("/metrics")
    def metrics():

        return metrics_response()


app = create_app()


if __name__ == "__main__":

    app.run(
        debug=True
    )
