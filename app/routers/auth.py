from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, TokenRefresh
from app.services.auth_service import AuthService
from app.core.security import verify_token, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, user_data.email, user_data.password)
    return AuthService.create_tokens(user.id, user.role)

@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh):
    payload = verify_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user_id = int(payload.get("sub"))
    role = payload.get("role", "customer")
    
    access_token = create_access_token(data={"sub": str(user_id), "role": role})
    return {"access_token": access_token, "refresh_token": token_data.refresh_token}