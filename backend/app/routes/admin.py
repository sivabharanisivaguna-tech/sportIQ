from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import require_roles, get_current_user
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.admin import (
    UserAdminUpdate,
    UserStatusToggle,
    UserListResponse,
    PlatformStatsResponse,
    PlatformReportsResponse,
    PlatformSettings,
    AdminDashboardResponse,
    AthleteAdminItem,
    CoachAdminItem,
    ScoutAdminItem,
    AdminNotificationItem
)
from app.schemas.user import UserResponse
from app.schemas.sport import SportCreate, SportResponse
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventAdminReview,
    EventOut,
    EventListResponse,
    OrganizerProfileOut,
    OrganizerAdminVerify,
    AdminEventStatsResponse
)
from app.schemas.common import APIResponse
from app.services.admin_service import AdminService
from app.services.event_service import EventService

router = APIRouter(prefix="/admin", tags=["Admin Governance"])


# -------------------------------------------------------------
# Admin Dashboard & Unified Metrics
# -------------------------------------------------------------
@router.get(
    "/dashboard",
    response_model=APIResponse[AdminDashboardResponse],
    summary="Get comprehensive Admin Dashboard metrics and activity streams"
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    """
    Retrieve live platform KPIs, user distributions, and recent submission/approval activity.
    """
    AdminService.seed_dev_admin_user(db)
    dashboard_data = AdminService.get_admin_dashboard(db)

    return APIResponse(
        success=True,
        message="Admin dashboard metrics retrieved successfully",
        data=AdminDashboardResponse(
            total_users=dashboard_data["total_users"],
            total_athletes=dashboard_data["total_athletes"],
            total_coaches=dashboard_data["total_coaches"],
            total_scouts=dashboard_data["total_scouts"],
            total_organizers=dashboard_data["total_organizers"],
            total_events=dashboard_data["total_events"],
            published_events=dashboard_data["published_events"],
            pending_events=dashboard_data["pending_events"],
            rejected_events=dashboard_data["rejected_events"],
            upcoming_events=dashboard_data["upcoming_events"],
            recent_users=[UserResponse.model_validate(u) for u in dashboard_data["recent_users"]],
            recent_event_submissions=[EventOut(**e) for e in dashboard_data["recent_event_submissions"]],
            recent_event_approvals=[EventOut(**e) for e in dashboard_data["recent_event_approvals"]]
        )
    )


# -------------------------------------------------------------
# Entity Management: Users, Athletes, Coaches, Scouts, Organizers
# -------------------------------------------------------------
@router.get(
    "/users",
    response_model=APIResponse[UserListResponse],
    summary="List all registered platform users"
)
def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    AdminService.seed_dev_admin_user(db)
    users, total = AdminService.list_users(
        db=db,
        role=role,
        search=search,
        page=page,
        limit=limit
    )
    return APIResponse(
        success=True,
        message="Users list retrieved successfully",
        data=UserListResponse(
            total=total,
            page=page,
            limit=limit,
            users=[UserResponse.model_validate(u) for u in users]
        )
    )


@router.get(
    "/athletes",
    response_model=APIResponse[List[AthleteAdminItem]],
    summary="List all athlete profiles"
)
def list_athletes(
    search: Optional[str] = Query(None, description="Search athlete by name, email, or sport"),
    is_active: Optional[bool] = Query(None, description="Filter by account status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    athletes, _ = AdminService.list_athletes(db, search=search, is_active=is_active, page=page, limit=limit)
    return APIResponse(
        success=True,
        message="Athletes list retrieved successfully",
        data=athletes
    )


@router.get(
    "/coaches",
    response_model=APIResponse[List[CoachAdminItem]],
    summary="List all coach profiles"
)
def list_coaches(
    search: Optional[str] = Query(None, description="Search coach by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by account status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    coaches, _ = AdminService.list_coaches(db, search=search, is_active=is_active, page=page, limit=limit)
    return APIResponse(
        success=True,
        message="Coaches list retrieved successfully",
        data=coaches
    )


@router.get(
    "/scouts",
    response_model=APIResponse[List[ScoutAdminItem]],
    summary="List all scout profiles"
)
def list_scouts(
    search: Optional[str] = Query(None, description="Search scout by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by account status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    scouts, _ = AdminService.list_scouts(db, search=search, is_active=is_active, page=page, limit=limit)
    return APIResponse(
        success=True,
        message="Scouts list retrieved successfully",
        data=scouts
    )


@router.put(
    "/users/{user_id}/status",
    response_model=APIResponse[UserResponse],
    summary="Activate or deactivate a user account"
)
def toggle_user_status(
    user_id: int,
    data: UserStatusToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    updated = AdminService.toggle_user_status(db, user_id, data.is_active)
    return APIResponse(
        success=True,
        message=f"User status updated to {'Active' if updated.is_active else 'Deactivated'}",
        data=UserResponse.model_validate(updated)
    )


@router.put(
    "/users/{user_id}",
    response_model=APIResponse[UserResponse],
    summary="Update a user's role or details"
)
def update_user(
    user_id: int,
    data: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    updated_user = AdminService.update_user(db, user_id, data)
    return APIResponse(
        success=True,
        message="User updated successfully",
        data=UserResponse.model_validate(updated_user)
    )


@router.delete(
    "/users/{user_id}",
    response_model=APIResponse[dict],
    summary="Delete a user from the platform"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    AdminService.delete_user(db, user_id)
    return APIResponse(
        success=True,
        message="User account deleted successfully",
        data={"deleted": True}
    )


# -------------------------------------------------------------
# Sports Events Admin & Verification Pipeline
# -------------------------------------------------------------
@router.post(
    "/events",
    response_model=APIResponse[EventOut],
    status_code=status.HTTP_201_CREATED,
    summary="Admin directly create and publish an event"
)
def admin_create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    new_event = EventService.admin_create_event(db, current_user, data)
    event_dict = EventService.get_event_by_id(db, new_event.id, current_user)
    return APIResponse(
        success=True,
        message="Event created and published as verified",
        data=EventOut(**event_dict)
    )


@router.get(
    "/events",
    response_model=APIResponse[EventListResponse],
    summary="Admin list all events across all statuses"
)
def admin_list_events(
    status_filter: Optional[str] = Query(None, description="Filter by event status"),
    search: Optional[str] = Query(None, description="Search keyword"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    EventService.seed_default_events(db)
    events, total = EventService.admin_list_all_events(
        db=db,
        status_filter=status_filter,
        search=search,
        page=page,
        limit=limit
    )
    return APIResponse(
        success=True,
        message="Events retrieved successfully",
        data=EventListResponse(
            total=total,
            page=page,
            limit=limit,
            events=[EventOut(**EventService.get_event_by_id(db, e.id, current_user)) for e in events]
        )
    )


@router.get(
    "/events/pending",
    response_model=APIResponse[List[EventOut]],
    summary="List pending review event verification queue"
)
def admin_list_pending_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    pending = EventService.admin_list_pending_events(db)
    return APIResponse(
        success=True,
        message="Pending review events retrieved",
        data=[EventOut(**EventService.get_event_by_id(db, e.id, current_user)) for e in pending]
    )


@router.get(
    "/events/stats",
    response_model=APIResponse[AdminEventStatsResponse],
    summary="Get aggregated event and organizer metrics"
)
def get_event_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    stats_data = EventService.admin_get_stats(db)
    return APIResponse(
        success=True,
        message="Event statistics retrieved",
        data=AdminEventStatsResponse(**stats_data)
    )


@router.get(
    "/events/{event_id}",
    response_model=APIResponse[EventOut],
    summary="Get full event data for Admin review"
)
def admin_get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    event_dict = EventService.get_event_by_id(db, event_id, current_user)
    return APIResponse(
        success=True,
        message="Event details retrieved for review",
        data=EventOut(**event_dict)
    )


@router.put(
    "/events/{event_id}/approve",
    response_model=APIResponse[EventOut],
    summary="Approve and publish a pending event"
)
def admin_approve_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    review = EventAdminReview(action="APPROVE", admin_notes="Verified and certified by SportIQ Admin.")
    event = EventService.admin_review_event(db, current_user, event_id, review)
    return APIResponse(
        success=True,
        message="Event approved and published to public Event Hub",
        data=EventOut(**EventService.get_event_by_id(db, event.id, current_user))
    )


@router.put(
    "/events/{event_id}/reject",
    response_model=APIResponse[EventOut],
    summary="Reject an event submission"
)
def admin_reject_event(
    event_id: int,
    review: EventAdminReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    review.action = "REJECT"
    event = EventService.admin_review_event(db, current_user, event_id, review)
    return APIResponse(
        success=True,
        message="Event submission rejected",
        data=EventOut(**EventService.get_event_by_id(db, event.id, current_user))
    )


@router.put(
    "/events/{event_id}/request-changes",
    response_model=APIResponse[EventOut],
    summary="Request changes on an event submission"
)
def admin_request_changes(
    event_id: int,
    review: EventAdminReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    review.action = "REQUEST_CHANGES"
    event = EventService.admin_review_event(db, current_user, event_id, review)
    return APIResponse(
        success=True,
        message="Changes requested from organizer",
        data=EventOut(**EventService.get_event_by_id(db, event.id, current_user))
    )


@router.put(
    "/events/{event_id}",
    response_model=APIResponse[EventOut],
    summary="Admin edit any event directly"
)
def admin_update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    event = EventService.organizer_update_event(db, current_user, event_id, data)
    return APIResponse(
        success=True,
        message="Event updated by administrator",
        data=EventOut(**EventService.get_event_by_id(db, event.id, current_user))
    )


@router.delete(
    "/events/{event_id}",
    response_model=APIResponse[dict],
    summary="Admin cancel or delete an event"
)
def admin_delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    EventService.organizer_cancel_event(db, current_user, event_id)
    return APIResponse(
        success=True,
        message="Event status updated to CANCELLED",
        data={"cancelled": True, "event_id": event_id}
    )


# -------------------------------------------------------------
# Organizer Verification Management
# -------------------------------------------------------------
@router.get(
    "/organizers",
    response_model=APIResponse[List[OrganizerProfileOut]],
    summary="List all registered sports organizers"
)
def list_organizers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    organizers = EventService.admin_list_organizers(db)
    return APIResponse(
        success=True,
        message="Organizers retrieved successfully",
        data=[OrganizerProfileOut.model_validate(o) for o in organizers]
    )


@router.put(
    "/organizers/{organizer_id}/verify",
    response_model=APIResponse[OrganizerProfileOut],
    summary="Verify or reject an organizer account"
)
def verify_organizer(
    organizer_id: int,
    data: OrganizerAdminVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    org = EventService.admin_verify_organizer(db, current_user, organizer_id, data)
    return APIResponse(
        success=True,
        message=f"Organizer status updated to {org.verification_status}",
        data=OrganizerProfileOut.model_validate(org)
    )


# -------------------------------------------------------------
# Reports, Notifications & System Settings
# -------------------------------------------------------------
@router.get(
    "/reports",
    response_model=APIResponse[PlatformReportsResponse],
    summary="Get aggregated platform governance and event reports"
)
def get_platform_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    reports_data = AdminService.get_platform_reports(db)
    return APIResponse(
        success=True,
        message="Platform reports generated successfully",
        data=reports_data
    )


@router.get(
    "/notifications",
    response_model=APIResponse[List[AdminNotificationItem]],
    summary="Get live administrative notifications and alerts"
)
def get_admin_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    notifs = AdminService.get_admin_notifications(db)
    return APIResponse(
        success=True,
        message="Admin notifications retrieved",
        data=notifs
    )


@router.get(
    "/settings",
    response_model=APIResponse[PlatformSettings],
    summary="Get platform configuration settings"
)
def get_platform_settings(
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    settings_obj = AdminService.get_platform_settings()
    return APIResponse(
        success=True,
        message="Platform settings retrieved",
        data=settings_obj
    )


@router.put(
    "/settings",
    response_model=APIResponse[PlatformSettings],
    summary="Update platform configuration settings"
)
def update_platform_settings(
    new_settings: PlatformSettings,
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    updated = AdminService.update_platform_settings(new_settings)
    return APIResponse(
        success=True,
        message="Platform settings updated successfully",
        data=updated
    )


# -------------------------------------------------------------
# Sports Taxonomy & Legacy Metrics
# -------------------------------------------------------------
@router.post(
    "/sports",
    response_model=APIResponse[SportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a new sport to the catalog"
)
def create_sport(
    data: SportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    sport = AdminService.create_sport(db, data)
    return APIResponse(
        success=True,
        message="Sport created successfully",
        data=SportResponse.model_validate(sport)
    )


@router.get(
    "/sports",
    response_model=APIResponse[List[SportResponse]],
    summary="List all sports in the catalog"
)
def list_sports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sports = AdminService.list_sports(db)
    return APIResponse(
        success=True,
        message="Sports catalog retrieved successfully",
        data=[SportResponse.model_validate(s) for s in sports]
    )


@router.delete(
    "/sports/{sport_id}",
    response_model=APIResponse[dict],
    summary="Delete a sport from the catalog"
)
def delete_sport(
    sport_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    AdminService.delete_sport(db, sport_id)
    return APIResponse(
        success=True,
        message="Sport removed from catalog successfully",
        data={"deleted": True}
    )


@router.delete(
    "/performance/{record_id}",
    response_model=APIResponse[dict],
    summary="Admin delete a performance record"
)
def admin_delete_performance(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    AdminService.delete_performance_record(db, record_id)
    return APIResponse(
        success=True,
        message="Performance record deleted by administrator",
        data={"deleted": True}
    )


@router.get(
    "/stats",
    response_model=APIResponse[PlatformStatsResponse],
    summary="Get platform-wide statistics and KPIs"
)
def get_platform_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    stats = AdminService.get_platform_stats(db)
    return APIResponse(
        success=True,
        message="Platform statistics calculated successfully",
        data=stats
    )



