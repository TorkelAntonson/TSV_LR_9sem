from pydantic import BaseModel

# Схема для создания и обновления пользователя
class UserCreate(BaseModel):
    user_id: int
    name: str
    surname: str
    age: int

# Схема для отображения пользователя
class User(BaseModel):
    user_id: int
    name: str
    surname: str
    age: int
    is_actual: bool

    class Config:
        orm_mode = True  # Чтобы Pydantic мог работать с SQLAlchemy моделями
