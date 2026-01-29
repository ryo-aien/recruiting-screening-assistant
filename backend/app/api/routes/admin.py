from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.score_config_repository import ScoreConfigRepository
from app.schemas.score_config import ScoreConfigCreate, ScoreConfigResponse

router = APIRouter()


@router.get("/score-config", response_model=ScoreConfigResponse)
async def get_score_config(
    db: AsyncSession = Depends(get_db),
) -> ScoreConfigResponse:
    """Get the current score configuration."""
    repo = ScoreConfigRepository(db)
    config = await repo.get_latest()
    if not config:
        # Return default config if none exists
        return ScoreConfigResponse(
            version=0,
            weights_json={"must": 0.45, "nice": 0.20, "year": 0.20, "role": 0.15},
            must_cap_enabled=True,
            must_cap_value=20.0,
            nice_top_n=3,
            role_distance_json={
                "IC": {"IC": 1.0, "Lead": 0.7, "Manager": 0.3},
                "Lead": {"IC": 0.7, "Lead": 1.0, "Manager": 0.7},
                "Manager": {"IC": 0.3, "Lead": 0.7, "Manager": 1.0},
            },
            created_at=None,
        )
    return ScoreConfigResponse.model_validate(config)


@router.post(
    "/score-config",
    response_model=ScoreConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
async def update_score_config(
    data: ScoreConfigCreate,
    db: AsyncSession = Depends(get_db),
) -> ScoreConfigResponse:
    """Create a new version of the score configuration."""
    repo = ScoreConfigRepository(db)

    # Get current config for role_distance default
    current = await repo.get_latest()
    role_distance = data.role_distance or (
        current.role_distance_json
        if current
        else {
            "IC": {"IC": 1.0, "Lead": 0.7, "Manager": 0.3},
            "Lead": {"IC": 0.7, "Lead": 1.0, "Manager": 0.7},
            "Manager": {"IC": 0.3, "Lead": 0.7, "Manager": 1.0},
        }
    )

    config = await repo.create_new_version(
        weights_json=data.weights.model_dump(),
        must_cap_enabled=data.must_cap_enabled,
        must_cap_value=data.must_cap_value,
        nice_top_n=data.nice_top_n,
        role_distance_json=role_distance,
    )
    return ScoreConfigResponse.model_validate(config)
