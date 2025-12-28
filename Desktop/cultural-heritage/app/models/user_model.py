from sqlalchemy import Column, Integer, String, Boolean
from app.db.postgres import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "is_admin": self.is_admin}