from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash
from fastapi import HTTPException, status
from typing import Optional, Tuple, List

class UserService:
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, 
                  search: Optional[str] = None) -> Tuple[List[User], int]:
        """Get all users with pagination and search"""
        query = db.query(User)
        
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # If password is being updated, hash it
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> dict:
        """Permanently delete user (HARD DELETE)"""
        user = UserService.get_user_by_id(db, user_id)
        
        # Prevent deleting the last admin
        if user.role == "admin":
            admin_count = db.query(User).filter(User.role == "admin", User.is_active == True).count()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last admin user"
                )
        
        # HARD DELETE - remove from database
        db.delete(user)
        db.commit()
        
        return {"message": f"User {user.username} has been permanently deleted"}
    
    @staticmethod
    def activate_user(db: Session, user_id: int) -> dict:
        """Activate a user account"""
        user = UserService.get_user_by_id(db, user_id)
        user.is_active = True
        db.commit()
        return {"message": f"User {user.username} has been activated"}
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> dict:
        """Deactivate a user account"""
        user = UserService.get_user_by_id(db, user_id)
        
        # Prevent deactivating the last admin
        if user.role == "admin":
            admin_count = db.query(User).filter(User.role == "admin", User.is_active == True).count()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate the last admin user"
                )
        
        user.is_active = False
        db.commit()
        return {"message": f"User {user.username} has been deactivated"}