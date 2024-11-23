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
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD операции
async def create_user(db: Session, user: UserCreate):
    # Сначала нужно сделать is_actual = False для всех пользователей
    db.query(UserModel).update({"is_actual": False})
    db.commit()
    # Создаем новую запись
    db_user = UserModel(user_id=user.user_id, name=user.name, surname=user.surname, age=user.age, is_actual=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UserModel).offset(skip).limit(limit).all()


async def delete_user(db: Session, user_id: int):
    user = db.query(UserModel).filter(UserModel.user_id == user_id, UserModel.is_actual == True).first()
    if user:
        user.is_actual = False
        db.commit()
        return {"message": "User successfully deleted"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


# Маршруты
@app.post("/users/", response_model=User)
async def create_user_view(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


@app.get("/users/", response_model=list[User])
async def get_users_view(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_users(db=db, skip=skip, limit=limit)


@app.delete("/users/{user_id}")
async def delete_user_view(user_id: int, db: Session = Depends(get_db)):
    return delete_user(db=db, user_id=user_id)
