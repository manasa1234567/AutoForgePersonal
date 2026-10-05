from sqlalchemy.orm import Session
from . import models, schemas


def create_application(db: Session, app_data: schemas.ApplicationCreate):
    db_app = models.Application(**app_data.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app
