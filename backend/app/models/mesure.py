from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.models.base import Base, BaseModelMixin

class Mesure(Base, BaseModelMixin):
    __tablename__ = 'mesures'

    id = Column(Integer, primary_key=True, autoincrement=True)
    methode = Column(String(20), nullable=False, index=True)   
    anime_id = Column(Integer, nullable=False)                 
    temps_ms = Column(Float, nullable=False)                   
    nb_resultats = Column(Integer, nullable=False)
    date_mesure = Column(DateTime, default=datetime.now)