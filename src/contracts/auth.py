from pydantic import BaseModel, EmailStr


class LoginPasswordSchema(BaseModel):
    email: EmailStr
    password: str
