from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.services.product_service import ProductService
from app.services.email_service import EmailService
from fastapi import HTTPException, status, BackgroundTasks
from typing import Optional, List, Tuple
from datetime import datetime, date

class OrderService:
    @staticmethod
    def create_order(db: Session, user_id: int, order_data: OrderCreate, background_tasks: BackgroundTasks):
        """Create a new order"""
        # Check stock availability
        ProductService.check_stock(db, order_data.items)
        
        # Calculate total amount and prepare order items
        total_amount = 0
        order_items_data = []
        
        for item in order_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            item_total = product.price * item.quantity
            total_amount += item_total
            
            # Reduce stock
            product.stock -= item.quantity
            
            order_items_data.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": product.price
            })
        
        # Create order
        db_order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        db.add(db_order)
        db.flush()
        
        # Create order items
        for item_data in order_items_data:
            db_item = OrderItem(order_id=db_order.id, **item_data)
            db.add(db_item)
        
        db.commit()
        db.refresh(db_order)
        
        # Send email notification in background
        background_tasks.add_task(
            EmailService.send_order_confirmation,
            db, db_order.id
        )
        
        return db_order
    
    @staticmethod
    def get_user_orders(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20,
        status_filter: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> Tuple[List[Order], int]:
        """Get user orders with advanced filtering and sorting"""
        query = db.query(Order).filter(Order.user_id == user_id)
        
        # Apply status filter
        if status_filter:
            try:
                status_enum = OrderStatus(status_filter.lower())
                query = query.filter(Order.status == status_enum)
            except ValueError:
                pass
        
        # Apply date range filter
        if date_from:
            query = query.filter(Order.created_at >= date_from)
        if date_to:
            query = query.filter(Order.created_at <= date_to)
        
        # Apply amount range filter
        if min_amount:
            query = query.filter(Order.total_amount >= min_amount)
        if max_amount:
            query = query.filter(Order.total_amount <= max_amount)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if hasattr(Order, sort_by):
            sort_column = getattr(Order, sort_by)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(Order.created_at.desc())
        
        # Apply pagination
        orders = query.offset(skip).limit(limit).all()
        
        return orders, total
    
    @staticmethod
    def get_all_orders_admin(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None,
        user_id: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Tuple[List[Order], int]:
        """Get all orders for admin with filters"""
        try:
            query = db.query(Order)
            
            # Apply status filter
            if status_filter and status_filter.strip():
                try:
                    status_enum = OrderStatus(status_filter.lower())
                    query = query.filter(Order.status == status_enum)
                except ValueError:
                    pass
            
            # Apply user filter
            if user_id:
                query = query.filter(Order.user_id == user_id)
            
            # Apply date range filter
            if date_from:
                query = query.filter(Order.created_at >= date_from)
            if date_to:
                query = query.filter(Order.created_at <= date_to)
            
            # Get total count
            total = query.count()
            
            # Apply sorting
            if hasattr(Order, sort_by):
                sort_column = getattr(Order, sort_by)
                if sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(Order.created_at.desc())
            
            # Apply pagination
            orders = query.offset(skip).limit(limit).all()
            
            return orders, total
            
        except Exception as e:
            print(f"Error in get_all_orders_admin: {str(e)}")
            raise e
    
    @staticmethod
    def get_order(db: Session, order_id: int, user_id: Optional[int] = None):
        """Get order by ID with optional user filter"""
        query = db.query(Order).filter(Order.id == order_id)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        order = query.first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Order not found"
            )
        
        return order
    
    @staticmethod
    def update_order_status(
        db: Session, 
        order_id: int, 
        status_update: OrderStatusUpdate,
        background_tasks: BackgroundTasks
    ):
        """Update order status"""
        order = OrderService.get_order(db, order_id)
        
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update cancelled order"
            )
        
        old_status = order.status
        order.status = status_update.status
        db.commit()
        db.refresh(order)
        
        # Send email notification for status update
        if status_update.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            background_tasks.add_task(
                EmailService.send_order_status_update,
                db, order_id
            )
        
        return order
    
    @staticmethod
    def cancel_order(db: Session, order_id: int, user_id: int, background_tasks: BackgroundTasks):
        """Cancel an order and restore stock"""
        order = OrderService.get_order(db, order_id, user_id)
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status {order.status.value}"
            )
        
        # Restore stock
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
        
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)  # Refresh to get updated data
        
        # Send cancellation email
        background_tasks.add_task(
            EmailService.send_order_cancellation,
            db, order_id
        )
        
        # Return the updated order with items
        return {
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
        }
    
    @staticmethod
    def get_order_statistics(db: Session, user_id: Optional[int] = None):
        """Get order statistics for user or admin"""
        from sqlalchemy import func
        
        query = db.query(Order)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        total_orders = query.count()
        total_spent = query.filter(Order.status != OrderStatus.CANCELLED).with_entities(
            func.sum(Order.total_amount)
        ).scalar() or 0
        
        status_counts = {}
        for status in OrderStatus:
            count = query.filter(Order.status == status).count()
            status_counts[status.value] = count
        
        return {
            "total_orders": total_orders,
            "total_spent": float(total_spent),
            "average_order_value": float(total_spent / total_orders if total_orders > 0 else 0),
            "status_breakdown": status_counts
        }