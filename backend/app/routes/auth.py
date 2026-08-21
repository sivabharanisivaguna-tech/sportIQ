from typing import Optional, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    VerifyResetCodeRequest,
    VerifyResetCodeResponse,
    ResetPasswordRequest,
)
from app.schemas.user import UserResponse
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================
# Standard Local Authentication (Email & Indian Phone Number)
# =============================================================
@router.post(
    "/register",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (Email or Phone Number)"
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user with Name, designated Role, and either Email OR Indian Mobile Phone Number.
    Returns the created user details along with a signed JWT access token.
    """
    user, access_token = AuthService.register_user(db, request)
    token_response = AuthService.build_token_response(user, access_token)
    return APIResponse(
        success=True,
        message="Account created successfully",
        data=token_response
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="Authenticate user and obtain JWT token"
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate an existing user using Email OR Indian Mobile Phone Number and password.
    Returns a valid JWT access token for subsequent authorized API calls.
    """
    user, access_token = AuthService.authenticate_user(db, request)
    token_response = AuthService.build_token_response(user, access_token)
    return APIResponse(
        success=True,
        message="Login successful",
        data=token_response
    )


@router.post(
    "/forgot-password",
    response_model=APIResponse[ForgotPasswordResponse],
    summary="Request password reset verification code (Email or Phone)"
)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Sends a single-use, 6-digit OTP verification code to registered email or mobile phone.
    Returns generic anti-enumeration response if account is not found.
    """
    result = OTPService.request_forgot_password_otp(
        db=db,
        identifier=request.identifier,
        preferred_destination=request.preferred_destination
    )
    return APIResponse(
        success=True,
        message=result["message"],
        data=ForgotPasswordResponse(
            message=result["message"],
            destination_type=result["destination_type"],
            masked_destination=result["masked_destination"],
            available_destinations=result["available_destinations"],
            delivery_status=result.get("delivery_status", "SENT"),
            is_dev_mode=result.get("is_dev_mode", False),
            dev_note=result.get("dev_note"),
            dev_otp=result.get("dev_otp")
        )
    )


@router.post(
    "/verify-reset-code",
    response_model=APIResponse[VerifyResetCodeResponse],
    summary="Verify 6-digit OTP and obtain temporary reset token"
)
def verify_reset_code(request: VerifyResetCodeRequest, db: Session = Depends(get_db)):
    """
    Validates the 6-digit OTP code.
    If valid, returns a temporary, single-use `reset_token` required for password update.
    """
    is_valid, reset_token, msg = OTPService.verify_reset_code(
        db=db,
        identifier=request.identifier,
        code=request.code
    )
    return APIResponse(
        success=True,
        message=msg,
        data=VerifyResetCodeResponse(
            message=msg,
            reset_token=reset_token
        )
    )


@router.post(
    "/reset-password",
    response_model=APIResponse[dict],
    summary="Set new password using verified reset token"
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Updates the user's password using the single-use reset token and revokes the token.
    """
    user = OTPService.reset_password_with_token(
        db=db,
        reset_token=request.reset_token,
        new_password=request.new_password
    )
    return APIResponse(
        success=True,
        message="Password updated successfully. You can now sign in with your new password.",
        data={"user_id": user.id, "email": user.email, "phone_number": user.phone_number}
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Retrieve current authenticated user details"
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Fetch profile information and role permissions for the currently authenticated user.
    Requires Bearer JWT token in Authorization header.
    """
    return APIResponse(
        success=True,
        message="User profile retrieved successfully",
        data=UserResponse.model_validate(current_user)
    )
