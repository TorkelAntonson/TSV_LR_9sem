from pydantic import BaseModel
from datetime import datetime

# Схема для создания и обновления пользователя
class UserCreate(BaseModel):
    user_id: int
    name: str
    surname: str
    age: int
    created_at: datetime  # Временная метка создания


# Схема для отображения пользователя
class User(BaseModel):
    user_id: int
    name: str
    surname: str
    age: int
    is_actual: bool
    created_at: datetime  # Временная метка создания

    class Config:
        orm_mode = True  # Чтобы Pydantic мог работать с SQLAlchemy моделями
