from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password
from app.core.database import AsyncSessionLocal
from app.core.security import verify_password
from app.core.auth_utils import create_access_token
from fastapi import Depends
from app.core.auth_dependencies import get_current_user


router = APIRouter(prefix = "/auth", tags = ["auth"])

@router.get("/me")
async def me(current_user = Depends(get_current_user)):
    return{
        "id" : current_user.id,
        "email" : current_user.email,
        "username" : current_user.username,
    }

@router.post("/signup")
async def signup(email: str, username: str, display_name: str,password: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code = 400,
                detail = "Email already registered"
            )
        
        print("PASSWORD VALUE:", password)
        print("PASSWORD LENGTH:", len(password.encode("utf-8")))

        hashed_password = hash_password(password)

        user = User(
            email = email,
            username = username,
            display_name = display_name,
            password_hash = hashed_password
        )

        session.add(user)
        await session.commit()

        return {"message" : "User created successfully"}
    

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