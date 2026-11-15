from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=False)
    source_url = Column(String(512), nullable=False)
    version = Column(String(32), nullable=True)
    measurement_name = Column(String(128), nullable=False)
    unit = Column(String(32), nullable=False)
    baseline = Column(String(255), nullable=True)
    temporal_resolution = Column(String(32), nullable=False, default="monthly")
    geographic_coverage = Column(String(64), nullable=False, default="global")
    last_retrieved = Column(DateTime, nullable=True, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    observations = relationship("Observation", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dataset(id='{self.id}', title='{self.title}', unit='{self.unit}')>"
