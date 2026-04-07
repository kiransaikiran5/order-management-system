from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from fastapi import HTTPException, status
from typing import Optional, Tuple, List

class ProductService:
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate):
        db_product = Product(**product_data.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def get_products(
        db: Session, 
        skip: int = 0, 
        limit: int = 20,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        in_stock_only: bool = False
    ) -> Tuple[List[Product], int]:
        """Get products with advanced filtering and sorting"""
        try:
            query = db.query(Product).filter(Product.is_active == True)
            
            # Apply search filter
            if search and search.strip():
                query = query.filter(
                    or_(
                        Product.name.ilike(f"%{search}%"),
                        Product.description.ilike(f"%{search}%")
                    )
                )
            
            # Apply price range filter
            if min_price is not None and min_price > 0:
                query = query.filter(Product.price >= min_price)
            if max_price is not None and max_price > 0:
                query = query.filter(Product.price <= max_price)
            
            # Apply stock filter
            if in_stock_only:
                query = query.filter(Product.stock > 0)
            
            # Get total count before pagination
            total = query.count()
            
            # Apply sorting
            if sort_by and hasattr(Product, sort_by):
                sort_column = getattr(Product, sort_by)
                if sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                # Default sort by created_at desc
                query = query.order_by(Product.created_at.desc())
            
            # Apply pagination
            products = query.offset(skip).limit(limit).all()
            
            return products, total
            
        except Exception as e:
            print(f"Error in get_products: {str(e)}")
            raise e
    
    @staticmethod
    def get_product(db: Session, product_id: int):
        product = db.query(Product).filter(
            Product.id == product_id, 
            Product.is_active == True
        ).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Product not found"
            )
        return product
    
    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate):
        product = ProductService.get_product(db, product_id)
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int):
        product = ProductService.get_product(db, product_id)
        product.is_active = False
        db.commit()
        return {"message": "Product deleted successfully"}
    
    @staticmethod
    def check_stock(db: Session, items: list):
        """Check stock availability for order items"""
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product ID {item.product_id} not found"
                )
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}. Available: {product.stock}"
                )
        return True
    
    @staticmethod
    def bulk_update_stock(db: Session, updates: dict):
        """Bulk update product stock"""
        for product_id, quantity in updates.items():
            product = ProductService.get_product(db, product_id)
            product.stock -= quantity
        db.commit()