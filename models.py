from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base


# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    age = Column(Integer)
    is_actual = Column(Boolean, default=True)

