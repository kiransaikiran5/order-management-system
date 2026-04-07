from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class PaymentMethodEnum(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"

class PaymentCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    payment_method: PaymentMethodEnum

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    status: str
    payment_method: str
    transaction_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentProcessResponse(BaseModel):
    payment: PaymentResponse
    message: str
    success: bool