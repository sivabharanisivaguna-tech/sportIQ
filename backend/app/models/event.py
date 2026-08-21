from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class Organizer(Base):
    __tablename__ = "organizers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    organization_name = Column(String(255), nullable=False, index=True)
    contact_person = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    organization_type = Column(String(100), nullable=True) # e.g. Club, District Association, Academy, School, Private Organizer
    website = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    verification_status = Column(String(50), default="PENDING", nullable=False, index=True) # PENDING, VERIFIED, REJECTED
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="organizer_profile")
    verifier = relationship("User", foreign_keys=[verified_by])
    events = relationship("SportsEvent", back_populates="organizer_profile", cascade="all, delete-orphan")


class SportsEvent(Base):
    __tablename__ = "sports_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    sport = Column(String(100), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, default="Tournament", index=True) # Tournament, Championship, Selection Trials, etc.
    description = Column(Text, nullable=False)

    # Dates & Timings
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    registration_deadline = Column(Date, nullable=False, index=True)
    start_time = Column(String(50), nullable=True) # e.g. "08:30 AM"
    end_time = Column(String(50), nullable=True)   # e.g. "06:00 PM"

    # Location
    venue = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    country = Column(String(100), default="India", nullable=False)

    # Eligibility & Category
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)
    gender = Column(String(50), default="All", nullable=False) # All, Male, Female, Co-ed
    competition_level = Column(String(100), default="Open", nullable=False, index=True) # District, State, National, Open, etc.

    # Financial & Awards
    entry_fee = Column(String(150), nullable=True) # e.g. "₹500 / Entry", "Free"
    prize_details = Column(Text, nullable=True)   # e.g. "₹50,000 Cash Prize + Trophies + Certificates"
    eligibility = Column(Text, nullable=True)     # e.g. "Registered district players with valid ID"

    # Organizer Information
    organizer_id = Column(Integer, ForeignKey("organizers.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    organizer_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)

    # External Registration & Verification Proof
    registration_url = Column(String(500), nullable=True) # Official external registration link
    source_url = Column(String(500), nullable=True)       # Official source link / circular
    poster_url = Column(String(500), nullable=True)       # Banner / Flyer image URL

    # Lifecycle & Verification Status
    status = Column(String(50), default="PENDING_REVIEW", nullable=False, index=True) # DRAFT, PENDING_REVIEW, CHANGES_REQUESTED, PUBLISHED, REJECTED, CANCELLED, EXPIRED
    verification_status = Column(String(50), default="PENDING", nullable=False, index=True) # UNVERIFIED, PENDING, VERIFIED, REJECTED
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    admin_notes = Column(Text, nullable=True) # Change requests / rejection notes

    views_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organizer_profile = relationship("Organizer", back_populates="events")
    creator = relationship("User", foreign_keys=[created_by_user_id])
    verifier = relationship("User", foreign_keys=[verified_by])
    saved_by = relationship("SavedEvent", back_populates="event", cascade="all, delete-orphan")
    recommendations = relationship("EventRecommendation", back_populates="event", cascade="all, delete-orphan")


class SavedEvent(Base):
    __tablename__ = "saved_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("sports_events.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_saved_event"),
    )

    # Relationships
    user = relationship("User", back_populates="saved_events")
    event = relationship("SportsEvent", back_populates="saved_by")


class EventRecommendation(Base):
    __tablename__ = "event_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("sports_events.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=True)
    status = Column(String(50), default="SENT", nullable=False) # SENT, VIEWED, DISMISSED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    coach = relationship("User", foreign_keys=[coach_id])
    player = relationship("Player", foreign_keys=[player_id])
    event = relationship("SportsEvent", back_populates="recommendations")
