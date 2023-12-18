from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from bson import ObjectId
...
M = TypeVar('M')


class PaginatedResponse(GenericModel, Generic[M]):
    message: str = Field(...)
    count: int = Field(description='Number of items returned in the response')
    items: List[M] = Field(description='List of items returned in the response following given criteria')


class IResponse(GenericModel, Generic[M]):
    message: str = Field(...)
    data: dict = Field(description='')

    class Config:
        allow_populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ErrorResponse(GenericModel, Generic[M]):
    error: str = Field(...)
    message: str = Field(...)
