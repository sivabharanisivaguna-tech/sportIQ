from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class VideoAssessment(Base):
    __tablename__ = "video_assessments"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    sport = Column(String(100), nullable=False, index=True)
    assessment_type = Column(String(100), nullable=False, index=True)
    video_url = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    processing_status = Column(String(50), default="UPLOADED", nullable=False, index=True) # UPLOADED, PROCESSING, ANALYZED, COMPLETED, FAILED

    # Verification Lifecycle State (UPLOADED -> PROCESSING -> ANALYZED -> PENDING_VERIFICATION -> VERIFIED / REJECTED)
    status = Column(String(50), default="UPLOADED", nullable=False, index=True)
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejected_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Strict Video Validation Gates
    validation_status = Column(String(50), default="PENDING", nullable=False, index=True) # PENDING, VALIDATED, REJECTED, INSUFFICIENT_EVIDENCE
    validation_reason = Column(Text, nullable=True)
    detected_sport = Column(String(100), nullable=True)
    detected_activity = Column(String(100), nullable=True)
    activity_confidence = Column(Float, default=0.0)
    video_quality_score = Column(Float, default=0.0)
    athlete_visibility_score = Column(Float, default=0.0)
    athletes_detected_count = Column(Integer, default=1)
    camera_stability_score = Column(Float, default=0.0)
    lighting_quality_score = Column(Float, default=0.0)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    player = relationship("Player", backref="video_assessments")
    analysis_result = relationship("VideoAnalysisResult", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    verifier = relationship("User", foreign_keys=[verified_by])
    rejecter = relationship("User", foreign_keys=[rejected_by])


class VideoAnalysisResult(Base):
    __tablename__ = "video_analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("video_assessments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    overall_score = Column(Float, nullable=False)           # Overall Performance Score 0 - 100
    analysis_confidence = Column(Float, nullable=False)     # AI Video Analysis Confidence 0 - 100%
    video_quality_status = Column(String(50), default="OPTIMAL", nullable=False) # OPTIMAL, SUFFICIENT, MARGINAL, INSUFFICIENT
    video_quality_notes = Column(Text, nullable=True)

    movement_score = Column(Float, nullable=False)          # Movement Sub-Score 0 - 100
    technique_score = Column(Float, nullable=False)         # Technique Sub-Score 0 - 100
    consistency_score = Column(Float, nullable=False)       # Consistency Sub-Score 0 - 100

    detected_indicators = Column(Text, nullable=True)       # JSON or string of detected key movement events
    strengths = Column(Text, nullable=True)
    areas_for_improvement = Column(Text, nullable=True)
    ai_recommendations = Column(Text, nullable=True)

    # Structured Pros/Cons Analysis & Observable Metrics (JSON strings)
    structured_strengths = Column(Text, nullable=True)      # JSON list of { name, observation, why_it_matters, confidence }
    structured_weaknesses = Column(Text, nullable=True)     # JSON list of { area, observation, why_it_matters, recommendation, confidence }
    observable_metrics = Column(Text, nullable=True)        # JSON dict of observable metrics with available/not_available status

    processed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    assessment = relationship("VideoAssessment", back_populates="analysis_result")


class VideoAssessmentAudit(Base):
    __tablename__ = "video_assessment_audits"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, nullable=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False, index=True) # VIDEO_UPLOADED, VIDEO_DELETED, AI_ANALYSIS_COMPLETED, SUBMITTED_FOR_VERIFICATION, VIDEO_VERIFIED, VIDEO_REJECTED
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text, nullable=True)

    # Relationship
    actor = relationship("User")
