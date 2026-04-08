from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order_service import OrderService
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new order (Customer only)"""
    return OrderService.create_order(db, current_user.id, order_data, background_tasks)

@router.get("/", response_model=dict)
def get_user_orders(
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of orders to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's orders with pagination, filtering, and sorting"""
    orders, total = OrderService.get_user_orders(
        db, current_user.id, skip, limit, status, sort_by, sort_order,
        date_from, date_to, min_amount, max_amount
    )
    
    # Convert orders to dict
    order_list = []
    for order in orders:
        order_list.append({
            "id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "status": order.status.value,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in order.items
            ]
        })
    
    return {
        "items": order_list,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < total,
        "has_previous": skip > 0
    }

@router.get("/admin/all", response_model=dict)
def get_all_orders_admin(
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of orders to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all orders for admin with filters (Admin only)"""
    try:
        orders, total = OrderService.get_all_orders_admin(
            db, skip, limit, status, user_id, sort_by, sort_order, date_from, date_to
        )
        
        # Convert orders to dict
        order_list = []
        for order in orders:
            order_list.append({
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "status": order.status.value,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
                "items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item.price
                    }
                    for item in order.items
                ]
            })
        
        return {
            "items": order_list,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_next": (skip + limit) < total,
            "has_previous": skip > 0
        }
    except Exception as e:
        print(f"Error in get_all_orders_admin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
def get_order_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order statistics for current user"""
    return OrderService.get_order_statistics(db, current_user.id)

@router.get("/admin/statistics")
def get_admin_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get overall order statistics (Admin only)"""
    return OrderService.get_order_statistics(db)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order details by ID"""
    if current_user.role == "admin":
        return OrderService.get_order(db, order_id)
    return OrderService.get_order(db, order_id, current_user.id)

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update order status (Admin only)"""
    return OrderService.update_order_status(db, order_id, status_update, background_tasks)

@router.post("/{order_id}/cancel", response_model=dict)
def cancel_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an order (Customer only for their own orders)"""
    result = OrderService.cancel_order(db, order_id, current_user.id, background_tasks)
    return {
        "message": "Order cancelled successfully",
        "order": result
    }