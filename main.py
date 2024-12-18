from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User as UserModel
from views import UserCreate, User
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Инициализация FastAPI приложения
app = FastAPI()

# Создание всех таблиц
from models import Base

Base.metadata.create_all(bind=engine)


# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD операции
def create_user(db: Session, user: UserCreate):
    # Создаем новую запись
    db_user = UserModel(user_id=user.user_id, name=user.name, surname=user.surname, age=user.age, is_actual=True, created_at=user.created_at)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Сортируем по дате создания в обратном порядке
    newest_user = (db.query(UserModel).order_by(UserModel.created_at.desc()).first())
    if newest_user:
        db.query(UserModel).update({"is_actual": False})  # Сбрасываем is_actual для всех
        newest_user.is_actual = True #Устанавливаем is_actual только самому свежему
        db.commit()
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UserModel).offset(skip).limit(limit).all()

def get_user_by_id(user_id: int, db: Session) -> User:
    # Ищем пользователя в базе данных по user_id
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        # Если пользователь не найден, выбрасываем исключение
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        # Сортируем по дате создания в обратном порядке
        newest_user = (db.query(UserModel).order_by(UserModel.created_at.desc()).first())
        if newest_user:
            db.query(UserModel).update({"is_actual": False})  # Сбрасываем is_actual для всех
            newest_user.is_actual = True #Устанавливаем is_actual только самому свежему
            db.commit()
        
        return {"detail": "Пользователь успешно удален"}
    else:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


def update_user_attribute(db: Session, user_id: int, attribute: str, value):
    # Проверяем, существует ли пользователь
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем, является ли переданный атрибут валидным
    if not hasattr(UserModel, attribute):
        raise HTTPException(status_code=400, detail=f"Атрибут '{attribute}' не существует")

    # Обновляем атрибут
    setattr(user, attribute, value)
    db.commit()
    db.refresh(user)

    # Если обновляется `created_at`, необходимо пересчитать `is_actual`
    if attribute == "created_at":
        newest_user = db.query(UserModel).order_by(UserModel.created_at.desc()).first()
        if newest_user:
            db.query(UserModel).update({"is_actual": False})
            newest_user.is_actual = True
            db.commit()

    return user

# Маршруты
@app.post("/users/", response_model=User)
async def create_user_view(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)

@app.get("/users/", response_model=list[User])
async def get_users_view(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_users(db=db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return get_user_by_id(user_id, db)

@app.delete("/users/{user_id}")
async def delete_user_view(user_id: int, db: Session = Depends(get_db)):
    return delete_user(db=db, user_id=user_id)

@app.patch("/users/{user_id}")
async def update_user_attribute_view(user_id: int, attribute: str, value: str, db: Session = Depends(get_db)):
    # Если обновляемый атрибут — это `age` или другой числовой тип, преобразуем значение
    if attribute in ["age"]:
        value = int(value)
    elif attribute in ["created_at"]:
        value = datetime.fromisoformat(value)  # Преобразование строки в дату
    return update_user_attribute(db=db, user_id=user_id, attribute=attribute, value=value)
