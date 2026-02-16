from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    email: EmailStr
    username: str
    display_name: str
    password: str