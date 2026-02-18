from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password
from app.core.database import AsyncSessionLocal
from app.core.security import verify_password
from app.core.auth_utils import create_access_token
from fastapi import Depends
from app.core.auth_dependencies import get_current_user
from app.schemas.user import UserSignup
from sqlalchemy.exc import IntegrityError



router = APIRouter(prefix = "/auth", tags = ["auth"])

@router.get("/me")
async def me(current_user = Depends(get_current_user)):
    return{
        "id" : current_user.id,
        "email" : current_user.email,
        "username" : current_user.username,
    }

@router.post("/signup")
async def signup(user_data: UserSignup):
    async with AsyncSessionLocal() as session:

        
        result = await session.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code = 400,
                detail = "Email already registered"
            )

        
        result = await session.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code =4 00,
                detail = "Username already taken"
            )

        hashed_password = hash_password(user_data.password)

        user = User(
            email = user_data.email,
            username = user_data.username,
            display_name = user_data.display_name,
            password_hash = hashed_password
        )

        session.add(user)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code = 400,
                detail = "Email or username already exists"
            )

        return {"message": "User created successfully"}
    

@router.post("/login")
async def login(email: str, password: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code = 401,
                detail = "Invalid credentials"
            )
        
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code = 401,
                detail = "Invaild credentials"
            )
        
        token = create_access_token(
            {"sub" : str(user.id)}
        ) 

        return {
            "access_token" : token,
            "token_type": "bearer" 
        }