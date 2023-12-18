from pydantic import BaseModel, Field
from pydantic.networks import EmailStr
from bson import ObjectId


class User(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(unique=True, index=True)
    password: str = Field(...)

    class Config:
        allow_populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Dolly",
                "email": "dollyna@gmail.com",
                "password": "cachorrinha.fofa.123"
            }
        }


class UserResponse(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)

    class Config:
        allow_populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "jdoe@example.com"
            }
        }


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class ForgetPasswordSchema(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    password: str = Field(...)
