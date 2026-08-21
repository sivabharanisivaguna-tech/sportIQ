from sqlalchemy import Column, Integer, Float, Date, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    speed = Column(Float, nullable=False)           # 0 - 100
    stamina = Column(Float, nullable=False)         # 0 - 100
    strength = Column(Float, nullable=False)        # 0 - 100
    agility = Column(Float, nullable=False)         # 0 - 100
    accuracy = Column(Float, nullable=False)        # 0 - 100
    matches_played = Column(Integer, default=0, nullable=False)
    assessment_date = Column(Date, nullable=False, index=True)

    # Inclusive Data Source & Verification Metadata
    source_type = Column(String(50), default="STANDARDIZED_FIELD_TEST", nullable=False, index=True) # SMARTPHONE_DERIVED, STANDARDIZED_FIELD_TEST, COACH_VERIFIED, WEARABLE_DEVICE, SELF_REPORTED_MANUAL
    verification_status = Column(String(50), default="UNVERIFIED", nullable=False, index=True)     # UNVERIFIED, COACH_VERIFIED, AI_VIDEO_VERIFIED, SYSTEM_VALIDATED
    evidence_url = Column(String(500), nullable=True)                                               # URL or path to video / photo proof
    field_test_protocol = Column(String(100), nullable=True)                                        # e.g., "30m Sprint", "Beep Test", "Standing Long Jump", "Illinois Agility"
    data_confidence_score = Column(Float, default=65.0, nullable=False)                            # 0.0 - 100.0%
    verified_by_coach_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verification_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player = relationship("Player", back_populates="performance_records")
    ai_analysis = relationship("AIAnalysis", back_populates="performance_record", uselist=False, cascade="all, delete-orphan")
    verified_by_coach = relationship("User", foreign_keys=[verified_by_coach_id])
