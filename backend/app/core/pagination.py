import math
from typing import Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

T = TypeVar("T")


class PageParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        limit: int = Query(default=20, ge=1, le=100),
    ) -> None:
        self.page = page
        self.limit = limit


class Page(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    items: List[T]
    total: int
    page: int
    limit: int
    pages: int


def paginate(db: Session, stmt: Select, params: PageParams) -> Page:
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = (
        db.execute(stmt.offset((params.page - 1) * params.limit).limit(params.limit))
        .scalars()
        .all()
    )
    pages = math.ceil(total / params.limit) if params.limit else 0
    return Page(items=list(items), total=total, page=params.page, limit=params.limit, pages=pages)