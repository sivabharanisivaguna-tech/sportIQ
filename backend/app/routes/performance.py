from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.performance import (
    PerformanceCreate,
    PerformanceUpdate,
    PerformanceVerificationRequest,
    PerformanceResponse,
    PerformanceStatsSummary,
    PerformanceHistoryResponse,
    EvidenceUploadResponse
)
from app.schemas.common import APIResponse
from app.services.performance_service import PerformanceService

router = APIRouter(prefix="/performance", tags=["Performance"])


@router.post(
    "",
    response_model=APIResponse[PerformanceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a new performance assessment record"
)
def add_performance(
    data: PerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.PLAYER, UserRole.COACH, UserRole.ADMIN]))
):
    """
    Log performance assessment metrics (speed, stamina, strength, agility, accuracy, matches played).
    - Athletes log for their own profile.
    - Coaches and Admins can log for any athlete by specifying `player_id`.
    - Automatically evaluates data source authenticity and assigns transparent Data Confidence Score.
    """
    record = PerformanceService.add_performance_record(db, current_user, data)
    return APIResponse(
        success=True,
        message="Performance record added successfully",
        data=PerformanceResponse.model_validate(record)
    )


@router.post(
    "/evidence",
    response_model=APIResponse[EvidenceUploadResponse],
    summary="Upload smartphone video or photo proof for field tests"
)
def upload_evidence(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles([UserRole.PLAYER, UserRole.COACH, UserRole.ADMIN]))
):
    """
    Upload smartphone video (MP4, WebM, MOV) or photo/document evidence supporting a physical trial.
    Elevates the Data Confidence Score of the associated performance record.
    """
    upload_res = PerformanceService.upload_evidence_file(file)
    return APIResponse(
        success=True,
        message="Evidence file uploaded successfully",
        data=upload_res
    )


@router.put(
    "/{record_id}/verify",
    response_model=APIResponse[PerformanceResponse],
    summary="Coach verification and certification of athlete performance record"
)
def verify_performance_record(
    record_id: int,
    data: PerformanceVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.COACH, UserRole.ADMIN]))
):
    """
    Allows a coach or platform admin to review video evidence or field test metrics
    and certify the measurement as COACH_VERIFIED.
    """
    verified_record = PerformanceService.verify_performance_record(db, current_user, record_id, data)
    return APIResponse(
        success=True,
        message="Performance record certified and verified successfully",
        data=PerformanceResponse.model_validate(verified_record)
    )


@router.get(
    "/player/{player_id}",
    response_model=APIResponse[PerformanceHistoryResponse],
    summary="Get performance history and time-series for a player"
)
def get_performance_history(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all historical performance assessments for a specific player,
    including overall statistical summary.
    """
    records = PerformanceService.get_player_performance_history(db, player_id)
    summary = PerformanceService.get_player_performance_stats(db, player_id)

    return APIResponse(
        success=True,
        message="Performance history retrieved successfully",
        data=PerformanceHistoryResponse(
            player_id=player_id,
            records=[PerformanceResponse.model_validate(r) for r in records],
            summary=summary
        )
    )


@router.get(
    "/player/{player_id}/stats",
    response_model=APIResponse[PerformanceStatsSummary],
    summary="Get aggregated performance statistics (averages & bests)"
)
def get_performance_stats(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compute average and maximum values for speed, stamina, strength, agility, and accuracy.
    """
    stats = PerformanceService.get_player_performance_stats(db, player_id)
    return APIResponse(
        success=True,
        message="Performance statistics calculated successfully",
        data=stats
    )


@router.put(
    "/{record_id}",
    response_model=APIResponse[PerformanceResponse],
    summary="Update a performance record"
)
def update_performance(
    record_id: int,
    data: PerformanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.PLAYER, UserRole.COACH, UserRole.ADMIN]))
):
    """
    Update metric values for an existing performance record.
    Enforces ownership verification.
    """
    updated_record = PerformanceService.update_performance_record(db, current_user, record_id, data)
    return APIResponse(
        success=True,
        message="Performance record updated successfully",
        data=PerformanceResponse.model_validate(updated_record)
    )


@router.delete(
    "/{record_id}",
    response_model=APIResponse[dict],
    summary="Delete a performance record"
)
def delete_performance(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.PLAYER, UserRole.COACH, UserRole.ADMIN]))
):
    """
    Delete a performance record. Enforces ownership verification.
    """
    PerformanceService.delete_performance_record(db, current_user, record_id)
    return APIResponse(
        success=True,
        message="Performance record deleted successfully",
        data={"deleted": True}
    )
