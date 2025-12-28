from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.postgres import get_postgres_session
from app.models.user_model import User
from pydantic import BaseModel
import hashlib

router = APIRouter()

class LoginInput(BaseModel):
    username: str
    password: str

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register")
async def register_user(data: LoginInput, session: AsyncSession = Depends(get_postgres_session)):
    # Check if user already exists
    result = await session.execute(select(User).where(User.username == data.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = hash_password(data.password)
    user = User(username=data.username, password=hashed_pw)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"message": "User registered", "user": user.to_dict()}

@router.post("/login")
async def login(data: LoginInput, session: AsyncSession = Depends(get_postgres_session)):
    hashed_pw = hash_password(data.password)
    result = await session.execute(select(User).where(User.username == data.username))
    user = result.scalars().first()
    if not user or user.password != hashed_pw:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"username": user.username, "is_admin": user.is_admin}