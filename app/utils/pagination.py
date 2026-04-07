from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.orm import Query as SQLAlchemyQuery
from sqlalchemy import asc, desc

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Query(0, ge=0, description="Number of items to skip")
    limit: int = Query(20, ge=1, le=100, description="Number of items to return")
    
class SortParams(BaseModel):
    """Sorting parameters"""
    sort_by: Optional[str] = Query(None, description="Field to sort by")
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order (asc/desc)")

class FilterParams(BaseModel):
    """Filtering parameters"""
    status: Optional[str] = Query(None, description="Filter by status")
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price")
    search: Optional[str] = Query(None, description="Search term")
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_previous: bool

def apply_pagination(query: SQLAlchemyQuery, skip: int, limit: int) -> SQLAlchemyQuery:
    """Apply pagination to query"""
    return query.offset(skip).limit(limit)

def apply_sorting(query: SQLAlchemyQuery, model, sort_by: Optional[str], sort_order: str):
    """Apply sorting to query"""
    if sort_by and hasattr(model, sort_by):
        sort_column = getattr(model, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
    return query

def get_paginated_response(items: List[T], total: int, skip: int, limit: int) -> PaginatedResponse:
    """Create paginated response"""
    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_next=(skip + limit) < total,
        has_previous=skip > 0
    )