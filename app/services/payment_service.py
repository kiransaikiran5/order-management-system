from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.order import Order, OrderStatus
from app.schemas.payment import PaymentCreate
from app.services.email_service import EmailService
from fastapi import HTTPException, status, BackgroundTasks
import uuid
import random
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    @staticmethod
    def process_payment(
        db: Session, 
        user_id: int, 
        payment_data: PaymentCreate,
        background_tasks: BackgroundTasks
    ):
        """Process payment with simulation and email notifications"""
        # Get order
        order = db.query(Order).filter(
            Order.id == payment_data.order_id,
            Order.user_id == user_id
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Order not found"
            )
        
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot pay for cancelled order"
            )
        
        # Check if payment already exists
        existing_payment = db.query(Payment).filter(Payment.order_id == order.id).first()
        if existing_payment and existing_payment.status == PaymentStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already processed for this order"
            )
        
        # Simulate payment processing (80% success rate)
        transaction_id = str(uuid.uuid4())
        success = random.random() < 0.8
        
        if success:
            payment_status = PaymentStatus.SUCCESS
            order.status = OrderStatus.CONFIRMED
            payment_message = "Payment processed successfully"
        else:
            payment_status = PaymentStatus.FAILED
            payment_message = "Payment processing failed"
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            status=payment_status,
            payment_method=payment_data.payment_method,
            transaction_id=transaction_id
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Send email notification in background
        if success:
            background_tasks.add_task(
                EmailService.send_payment_success,
                db, payment.id
            )
        else:
            background_tasks.add_task(
                EmailService.send_payment_failed,
                db, payment.id
            )
        
        return {
            "payment": payment,
            "message": payment_message,
            "success": success
        }
    
    @staticmethod
    def get_payment_by_order(db: Session, order_id: int, user_id: int):
        """Get payment details for an order"""
        payment = db.query(Payment).join(Order).filter(
            Payment.order_id == order_id,
            Order.user_id == user_id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        return payment