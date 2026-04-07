from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Create a new product (Admin only)"""
    try:
        return ProductService.create_product(db, product_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=dict)
def get_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of products to return"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by (name, price, stock, created_at)"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    in_stock_only: bool = Query(False, description="Show only products in stock"),
    db: Session = Depends(get_db)
):
    """
    Get all products with pagination, filtering, and sorting.
    """
    try:
        products, total = ProductService.get_products(
            db, skip, limit, search, min_price, max_price, sort_by, sort_order, in_stock_only
        )
        
        # Convert products to response format
        product_list = []
        for product in products:
            product_list.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "stock": product.stock,
                "is_active": product.is_active,
                "created_at": product.created_at,
                "updated_at": product.updated_at
            })
        
        return {
            "items": product_list,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": (skip + limit) < total,
            "has_previous": skip > 0
        }
    except Exception as e:
        print(f"Error in get_products endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    try:
        return ProductService.get_product(db, product_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Update product (Admin only)"""
    try:
        return ProductService.update_product(db, product_id, product_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Delete product (soft delete) (Admin only)"""
    try:
        return ProductService.delete_product(db, product_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))