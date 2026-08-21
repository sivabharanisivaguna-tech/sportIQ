from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    performance_id = Column(Integer, ForeignKey("performance_records.id", ondelete="CASCADE"), nullable=False, index=True)
    performance_score = Column(Float, nullable=False)   # Physical Ability Score 0 - 100
    talent_score = Column(Float, nullable=False, index=True) # AI Talent Rating 0 - 100 (Unbiased by device)
    potential_level = Column(String(50), nullable=False, index=True)  # HIGH, MEDIUM, DEVELOPING
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=False, default=0.85) # AI algorithm confidence (0.0 - 1.0)
    data_confidence_score = Column(Float, nullable=False, default=70.0) # Measurement / Evidence Confidence (0.0 - 100.0%)
    model_version = Column(String(50), nullable=False, default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player = relationship("Player", back_populates="ai_analyses")
    performance_record = relationship("PerformanceRecord", back_populates="ai_analysis")
