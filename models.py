from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
from datetime import datetime


# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    age = Column(Integer)
    is_actual = Column(Boolean, default=True)
    created_at = Column(DateTime)
