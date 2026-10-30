import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModelMixin:
    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"L'objet '{self.__class__.__name__}' n'a pas l'attribut '{item}'")

    def to_dict(self):
        result = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                val = val.strftime("%Y-%m-%d %H:%M:%S")
            result[col.name] = val
        return result

def get_engine(db_uri=None):
    if db_uri is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, 'anime_reco.db')
        db_uri = f"sqlite:///{db_path}"
    return create_engine(db_uri, echo=False)