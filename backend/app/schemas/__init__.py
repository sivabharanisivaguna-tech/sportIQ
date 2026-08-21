from app.schemas.common import APIResponse, HealthResponse
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, TokenData
from app.schemas.player import (
    PlayerBase,
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
    PlayerDetailResponse,
    PlayerListResponse
)
from app.schemas.performance import (
    PerformanceBase,
    PerformanceCreate,
    PerformanceUpdate,
    PerformanceResponse,
    PerformanceStatsSummary,
    PerformanceHistoryResponse
)
from app.schemas.coach import (
    TrainingRecommendationCreate,
    TrainingRecommendationUpdate,
    TrainingRecommendationResponse,
    PlayerComparisonRequest,
    PlayerComparisonItem,
    PlayerComparisonResponse
)
from app.schemas.scout import (
    ShortlistCreate,
    ShortlistUpdate,
    ShortlistResponse,
    ScoutPlayerItem,
    ScoutSearchResponse
)
from app.schemas.sport import (
    SportBase,
    SportCreate,
    SportUpdate,
    SportResponse
)
from app.schemas.admin import (
    UserAdminUpdate,
    UserListResponse,
    SportPlayerCount,
    PlatformStatsResponse
)
from app.schemas.ai_analysis import (
    AIPredictionRequest,
    AIPredictionResponse
)

__all__ = [
    "APIResponse",
    "HealthResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "TokenData",
    "PlayerBase",
    "PlayerCreate",
    "PlayerUpdate",
    "PlayerResponse",
    "PlayerDetailResponse",
    "PlayerListResponse",
    "PerformanceBase",
    "PerformanceCreate",
    "PerformanceUpdate",
    "PerformanceResponse",
    "PerformanceStatsSummary",
    "PerformanceHistoryResponse",
    "TrainingRecommendationCreate",
    "TrainingRecommendationUpdate",
    "TrainingRecommendationResponse",
    "PlayerComparisonRequest",
    "PlayerComparisonItem",
    "PlayerComparisonResponse",
    "ShortlistCreate",
    "ShortlistUpdate",
    "ShortlistResponse",
    "ScoutPlayerItem",
    "ScoutSearchResponse",
    "SportBase",
    "SportCreate",
    "SportUpdate",
    "SportResponse",
    "UserAdminUpdate",
    "UserListResponse",
    "SportPlayerCount",
    "PlatformStatsResponse",
    "AIPredictionRequest",
    "AIPredictionResponse",
]
