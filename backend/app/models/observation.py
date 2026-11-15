from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.dataset import Base

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False, index=True)
    date = Column(String(16), nullable=False, index=True)  # Format: "YYYY-MM" or "YYYY"
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True, index=True)
    value = Column(Float, nullable=False)
    raw_value = Column(String(64), nullable=True)
    uncertainty = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    quality_flag = Column(String(32), nullable=True, default="VALID")
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="observations")

    __table_args__ = (
        Index("idx_dataset_year", "dataset_id", "year"),
        Index("idx_dataset_date", "dataset_id", "date"),
    )

    def __repr__(self):
        return f"<Observation(dataset='{self.dataset_id}', date='{self.date}', value={self.value})>"
