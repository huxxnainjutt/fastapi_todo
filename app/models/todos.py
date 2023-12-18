from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional


class Todo(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    is_completed: bool = Field(default=False)

    class Config:
        allow_populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "title": "Dolly",
                "description": "dollyna@gmail.com",

            }
        }


class TodoUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "title": "Don Quixote",
                "description": "Miguel de Cervantes",

            }
        }


class TodoComplete(BaseModel):
    is_completed: bool = Field(default=False)

    class Config:
        schema_extra = {
            "example": {
                "title": "Don Quixote",
                "description": "Miguel de Cervantes",

            }
        }


class TodoResponse(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    is_completed: bool = Field(default=False)
    author: str = Field(...)
    created_at: str = Field(...)

    class Config:
        allow_populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "title": "Dolly",
                "description": "dollyna@gmail.com",

            }
        }