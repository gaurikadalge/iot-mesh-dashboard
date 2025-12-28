# app/models/artefact_model.py
from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class Artefact(Base):
    __tablename__ = "heritage_artefacts"

    artefact_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    site_name = Column(String(255))
    category = Column(String(100))
    material = Column(String(100))
    description = Column(Text)
    image_url = Column(Text)
    discovered_year = Column(Integer)

    def to_dict(self):
        return {
            "artefact_id": self.artefact_id,
            "name": self.name,
            "site_name": self.site_name,
            "category": self.category,
            "material": self.material,
            "description": self.description,
            "image_url": self.image_url,
            "discovered_year": self.discovered_year
        }