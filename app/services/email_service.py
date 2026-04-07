from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.core.email import send_email
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.product import Product
from app.models.payment import Payment
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Reusable email service with background task support"""
    
    @staticmethod
    async def send_order_confirmation_email(recipient_email: str, user_name: str, order_id: int, 
                                           total_amount: float, status: str, items: list):
        """Send order confirmation email"""
        subject = f"Order Confirmation #{order_id}"
        
        # Build items list HTML
        items_html = ""
        for item in items:
            items_html += f"""
            <tr>
                <td>{item['product_name']}</td>
                <td>{item['quantity']}</td>
                <td>${item['price']:.2f}</td>
                <td>${item['quantity'] * item['price']:.2f}</td>
            </tr>
            """
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .order-details {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                .total {{ font-size: 18px; font-weight: bold; text-align: right; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Order Confirmation</h2>
                </div>
                <div class="content">
                    <h3>Dear {user_name},</h3>
                    <p>Thank you for your order! Your order has been confirmed and is being processed.</p>
                    
                    <div class="order-details">
                        <h3>Order #{order_id}</h3>
                        <p><strong>Status:</strong> {status.upper()}</p>
                        <p><strong>Order Date:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                        
                        <h4>Order Items:</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Product</th>
                                    <th>Quantity</th>
                                    <th>Unit Price</th>
                                    <th>Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items_html}
                            </tbody>
                        </table>
                        
                        <div class="total">
                            Grand Total: ${total_amount:.2f}
                        </div>
                    </div>
                    
                    <p>We'll notify you once your order is shipped.</p>
                </div>
                <div class="footer">
                    <p>Thank you for shopping with us!</p>
                    <p>&copy; 2024 Order Management System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        await send_email([recipient_email], subject, body)
        logger.info(f"Order confirmation email sent to {recipient_email}")
    
    @staticmethod
    async def send_payment_success_email(recipient_email: str, user_name: str, order_id: int,
                                        amount: float, payment_method: str, transaction_id: str):
        """Send payment success email"""
        subject = f"Payment Successful - Order #{order_id}"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .payment-details {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; }}
                .success {{ color: #28a745; font-size: 24px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Payment Successful!</h2>
                </div>
                <div class="content">
                    <div class="success">✓ Payment Completed</div>
                    <h3>Dear {user_name},</h3>
                    <p>Your payment has been processed successfully.</p>
                    
                    <div class="payment-details">
                        <h3>Payment Details</h3>
                        <p><strong>Order #:</strong> {order_id}</p>
                        <p><strong>Amount:</strong> ${amount:.2f}</p>
                        <p><strong>Payment Method:</strong> {payment_method.replace('_', ' ').title()}</p>
                        <p><strong>Transaction ID:</strong> {transaction_id}</p>
                        <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                    </div>
                    
                    <p>Your order is now confirmed and will be prepared for shipping.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        await send_email([recipient_email], subject, body)
        logger.info(f"Payment success email sent to {recipient_email}")
    
    @staticmethod
    async def send_payment_failed_email(recipient_email: str, user_name: str, order_id: int, amount: float):
        """Send payment failed email"""
        subject = f"Payment Failed - Order #{order_id}"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .failed {{ color: #dc3545; font-size: 24px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Payment Failed</h2>
                </div>
                <div class="content">
                    <div class="failed">✗ Payment Failed</div>
                    <h3>Dear {user_name},</h3>
                    <p>We're sorry, but your payment could not be processed.</p>
                    
                    <div class="payment-details">
                        <h3>Payment Details</h3>
                        <p><strong>Order #:</strong> {order_id}</p>
                        <p><strong>Amount:</strong> ${amount:.2f}</p>
                        <p><strong>Status:</strong> Failed</p>
                    </div>
                    
                    <h4>Possible Reasons:</h4>
                    <ul>
                        <li>Insufficient funds</li>
                        <li>Incorrect payment details</li>
                        <li>Bank declined the transaction</li>
                    </ul>
                    
                    <p>Please try again with a different payment method or contact your bank.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        await send_email([recipient_email], subject, body)
        logger.info(f"Payment failed email sent to {recipient_email}")
    
    @staticmethod
    async def send_order_status_update_email(recipient_email: str, user_name: str, order_id: int, 
                                            status: str, tracking_number: str = None):
        """Send order status update email"""
        subject = f"Order #{order_id} Status Update - {status.upper()}"
        
        status_color = {
            "shipped": "#007bff",
            "delivered": "#28a745",
            "confirmed": "#17a2b8",
            "cancelled": "#dc3545"
        }.get(status, "#6c757d")
        
        additional_info = ""
        if status == "shipped" and tracking_number:
            additional_info = f"""
            <div class="shipping-info">
                <h3>Shipping Information</h3>
                <p><strong>Tracking Number:</strong> {tracking_number}</p>
                <p><strong>Carrier:</strong> FastExpress</p>
                <p><strong>Estimated Delivery:</strong> Within 3-5 business days</p>
            </div>
            """
        elif status == "delivered":
            additional_info = """
            <div class="delivery-info">
                <h3>Delivered!</h3>
                <p>We hope you enjoy your purchase! </p>
                <p>If you have any issues with your order, please contact our support team within 7 days.</p>
            </div>
            """
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {status_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .status {{ font-size: 20px; font-weight: bold; text-align: center; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Order Status Update</h2>
                </div>
                <div class="content">
                    <h3>Dear {user_name},</h3>
                    <p>Your order status has been updated!</p>
                    
                    <div class="status">
                        New Status: {status.upper()}
                    </div>
                    
                    {additional_info}
                    
                    <p>You can track your order progress in your account dashboard.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        await send_email([recipient_email], subject, body)
        logger.info(f"Order status update email sent to {recipient_email}")
    
    @staticmethod
    async def send_order_cancellation_email(recipient_email: str, user_name: str, order_id: int, 
                                           total_amount: float, was_paid: bool):
        """Send order cancellation email"""
        subject = f"Order #{order_id} Cancelled"
        
        refund_info = ""
        if was_paid:
            refund_info = f"""
            <div class="refund-info">
                <h3>Refund Information</h3>
                <p>A refund of <strong>${total_amount:.2f}</strong> will be processed to your original payment method.</p>
                <p>Please allow 5-7 business days for the refund to appear in your account.</p>
            </div>
            """
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Order Cancelled</h2>
                </div>
                <div class="content">
                    <h3>Dear {user_name},</h3>
                    <p>Your order #{order_id} has been cancelled as requested.</p>
                    
                    <div class="order-details">
                        <p><strong>Cancelled Date:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                        <p><strong>Total Amount:</strong> ${total_amount:.2f}</p>
                    </div>
                    
                    {refund_info}
                    
                    <p>If you changed your mind, you can place a new order anytime.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        await send_email([recipient_email], subject, body)
        logger.info(f"Order cancellation email sent to {recipient_email}")
    
    # Background task wrappers
    @staticmethod
    async def send_order_confirmation(db: Session, order_id: int):
        """Background task wrapper for order confirmation"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.error(f"Order {order_id} not found")
                return
            
            user = db.query(User).filter(User.id == order.user_id).first()
            if not user:
                logger.error(f"User for order {order_id} not found")
                return
            
            # Get order items with product names
            items = []
            for item in order.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                items.append({
                    "product_name": product.name if product else f"Product {item.product_id}",
                    "quantity": item.quantity,
                    "price": item.price
                })
            
            await EmailService.send_order_confirmation_email(
                user.email, user.full_name, order.id, 
                order.total_amount, order.status.value, items
            )
        except Exception as e:
            logger.error(f"Error in send_order_confirmation: {str(e)}")
    
    @staticmethod
    async def send_payment_success(db: Session, payment_id: int):
        """Background task wrapper for payment success"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                logger.error(f"Payment {payment_id} not found")
                return
            
            order = db.query(Order).filter(Order.id == payment.order_id).first()
            user = db.query(User).filter(User.id == order.user_id).first()
            
            await EmailService.send_payment_success_email(
                user.email, user.full_name, order.id, 
                payment.amount, payment.payment_method.value, payment.transaction_id
            )
        except Exception as e:
            logger.error(f"Error in send_payment_success: {str(e)}")
    
    @staticmethod
    async def send_payment_failed(db: Session, payment_id: int):
        """Background task wrapper for payment failed"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                logger.error(f"Payment {payment_id} not found")
                return
            
            order = db.query(Order).filter(Order.id == payment.order_id).first()
            user = db.query(User).filter(User.id == order.user_id).first()
            
            await EmailService.send_payment_failed_email(
                user.email, user.full_name, order.id, payment.amount
            )
        except Exception as e:
            logger.error(f"Error in send_payment_failed: {str(e)}")
    
    @staticmethod
    async def send_order_status_update(db: Session, order_id: int):
        """Background task wrapper for order status update"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.error(f"Order {order_id} not found")
                return
            
            user = db.query(User).filter(User.id == order.user_id).first()
            
            tracking_number = f"TRK{order_id}{datetime.now().year}" if order.status == OrderStatus.SHIPPED else None
            
            await EmailService.send_order_status_update_email(
                user.email, user.full_name, order.id, order.status.value, tracking_number
            )
        except Exception as e:
            logger.error(f"Error in send_order_status_update: {str(e)}")
    
    @staticmethod
    async def send_order_cancellation(db: Session, order_id: int):
        """Background task wrapper for order cancellation"""
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.error(f"Order {order_id} not found")
                return
            
            user = db.query(User).filter(User.id == order.user_id).first()
            
            # Check if payment was made
            payment = db.query(Payment).filter(Payment.order_id == order_id).first()
            was_paid = payment and payment.status.value == "success"
            
            await EmailService.send_order_cancellation_email(
                user.email, user.full_name, order.id, order.total_amount, was_paid
            )
        except Exception as e:
            logger.error(f"Error in send_order_cancellation: {str(e)}")