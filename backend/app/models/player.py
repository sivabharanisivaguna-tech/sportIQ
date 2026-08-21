from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    sport = Column(String(100), nullable=False, index=True)
    position = Column(String(100), nullable=True)
    experience = Column(Integer, nullable=True)  # in years
    height = Column(Float, nullable=True)        # in cm
    weight = Column(Float, nullable=True)        # in kg
    achievements = Column(Text, nullable=True)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="player_profile")
    performance_records = relationship("PerformanceRecord", back_populates="player", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="player", cascade="all, delete-orphan")
    shortlisted_by = relationship("Shortlist", back_populates="player", cascade="all, delete-orphan")
    training_recommendations = relationship("TrainingRecommendation", back_populates="player", cascade="all, delete-orphan")
