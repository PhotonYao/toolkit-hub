# result.py
from typing import Generic, TypeVar, Optional, Dict
from pydantic import BaseModel
from typing import Any

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    success: bool
    err_code: Optional[str] = None
    err_msg: Optional[str] = None
    data: Optional[T] = None

    @classmethod
    def succ(cls, data: T = None) -> "Result[T]":
        return cls(success=True, err_code=None, err_msg=None, data=data)

    @classmethod
    def failed(cls, code: str = "E000X", msg: Optional[str] = None) -> "Result[T]":
        return cls(success=False, err_code=code, err_msg=msg, data=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
