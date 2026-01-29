from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScoreConfig(Base):
    """Score configuration model for weights and settings."""

    __tablename__ = "score_config"

    version: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weights_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {"must": 0.45, "nice": 0.20, "year": 0.20, "role": 0.15},
    )
    must_cap_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    must_cap_value: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)
    nice_top_n: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    role_distance_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "IC": {"IC": 1.0, "Lead": 0.7, "Manager": 0.3},
            "Lead": {"IC": 0.7, "Lead": 1.0, "Manager": 0.7},
            "Manager": {"IC": 0.3, "Lead": 0.7, "Manager": 1.0},
        },
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
