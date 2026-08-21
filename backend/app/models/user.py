from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True) # Nullable for phone-only registrations
    phone_number = Column(String(20), unique=True, index=True, nullable=True) # E.164 normalized +91XXXXXXXXXX
    phone_verified = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PLAYER, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    player_profile = relationship("Player", back_populates="user", uselist=False, cascade="all, delete-orphan")
    organizer_profile = relationship("Organizer", foreign_keys="Organizer.user_id", back_populates="user", uselist=False, cascade="all, delete-orphan")
    shortlists = relationship("Shortlist", back_populates="user", cascade="all, delete-orphan")
    created_recommendations = relationship("TrainingRecommendation", back_populates="coach", cascade="all, delete-orphan")
    saved_events = relationship("SavedEvent", back_populates="user", cascade="all, delete-orphan")


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_type = Column(String(20), nullable=False) # "EMAIL" or "PHONE"
    destination = Column(String(255), nullable=False)
    code_hash = Column(String(255), nullable=False)
    reset_token = Column(String(255), unique=True, index=True, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    attempt_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user = relationship("User", backref="otp_verifications")
