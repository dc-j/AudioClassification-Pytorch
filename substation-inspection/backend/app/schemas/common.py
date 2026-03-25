from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, List

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[List[T]] = None
    total: int = 0
    page: int = 1
    page_size: int = 20
