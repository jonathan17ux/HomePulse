from datetime import datetime, timezone

from src.extensions import db


class NetworkObservation(db.Model):
    """
    Raw network observations collected by HomePulse.
    """

    __tablename__ = "network_observations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    public_ip = db.Column(
        db.String(45),
        nullable=False
    )

    source = db.Column(
        db.String(120),
        nullable=False
    )

    http_status = db.Column(
        db.Integer,
        nullable=False
    )

    response_time_ms = db.Column(
        db.Float,
        nullable=False
    )

    collected_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "public_ip": self.public_ip,
            "source": self.source,
            "http_status": self.http_status,
            "response_time_ms": round(
                self.response_time_ms,
                2
            ),
            "collected_at": self.collected_at.isoformat(),
        }


class AnalysisResult(db.Model):
    """
    Stores analyzed results generated from network observations.
    """

    __tablename__ = "analysis_results"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sample_size = db.Column(
        db.Integer,
        nullable=False
    )

    average_response_ms = db.Column(
        db.Float,
        nullable=False
    )

    minimum_response_ms = db.Column(
        db.Float,
        nullable=False
    )

    maximum_response_ms = db.Column(
        db.Float,
        nullable=False
    )

    success_rate = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False
    )

    analyzed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sample_size": self.sample_size,
            "average_response_ms": round(
                self.average_response_ms,
                2
            ),
            "minimum_response_ms": round(
                self.minimum_response_ms,
                2
            ),
            "maximum_response_ms": round(
                self.maximum_response_ms,
                2
            ),
            "success_rate": round(
                self.success_rate,
                2
            ),
            "status": self.status,
            "analyzed_at": self.analyzed_at.isoformat(),
        }
