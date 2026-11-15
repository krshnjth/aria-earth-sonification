from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.dataset import Dataset
from app.models.observation import Observation

class DatasetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, dataset_id: str) -> Optional[Dataset]:
        return self.db.query(Dataset).filter(Dataset.id == dataset_id).first()

    def list_all(self) -> List[Dataset]:
        return self.db.query(Dataset).filter(Dataset.is_active == True).all()

    def upsert(self, dataset_data: dict) -> Dataset:
        dataset = self.get(dataset_data["id"])
        if dataset:
            for k, v in dataset_data.items():
                setattr(dataset, k, v)
            dataset.last_retrieved = datetime.utcnow()
        else:
            dataset = Dataset(**dataset_data, last_retrieved=datetime.utcnow())
            self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

class ObservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_time_series(
        self,
        dataset_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        limit: int = 5000
    ) -> List[Observation]:
        query = self.db.query(Observation).filter(Observation.dataset_id == dataset_id)
        if start_year is not None:
            query = query.filter(Observation.year >= start_year)
        if end_year is not None:
            query = query.filter(Observation.year <= end_year)
        return query.order_by(Observation.date.asc()).limit(limit).all()

    def count(self, dataset_id: str) -> int:
        return self.db.query(func.count(Observation.id)).filter(Observation.dataset_id == dataset_id).scalar() or 0

    def get_latest_date(self, dataset_id: str) -> Optional[str]:
        obs = (
            self.db.query(Observation.date)
            .filter(Observation.dataset_id == dataset_id)
            .order_by(Observation.date.desc())
            .first()
        )
        return obs[0] if obs else None

    def bulk_replace(self, dataset_id: str, observations: List[dict]):
        # Remove old observations for this dataset
        self.db.query(Observation).filter(Observation.dataset_id == dataset_id).delete()
        # Bulk insert new observations in batches
        batch_size = 1000
        for i in range(0, len(observations), batch_size):
            batch = observations[i:i + batch_size]
            obs_objs = [Observation(dataset_id=dataset_id, **o) for o in batch]
            self.db.bulk_save_objects(obs_objs)
        self.db.commit()
