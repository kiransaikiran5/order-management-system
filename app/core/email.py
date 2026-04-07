from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .config import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

class EmailTemplates:
    ORDER_CONFIRMATION = """
    <h2>Order Confirmation</h2>
    <p>Dear {user_name},</p>
    <p>Your order #{order_id} has been confirmed.</p>
    <p>Total Amount: ${total_amount}</p>
    <p>Status: {status}</p>
    <p>Thank you for shopping with us!</p>
    """
    
    PAYMENT_SUCCESS = """
    <h2>Payment Successful</h2>
    <p>Dear {user_name},</p>
    <p>Your payment of ${amount} for order #{order_id} has been processed successfully.</p>
    <p>Payment Method: {payment_method}</p>
    <p>Transaction ID: {transaction_id}</p>
    """
    
    PAYMENT_FAILED = """
    <h2>Payment Failed</h2>
    <p>Dear {user_name},</p>
    <p>Your payment of ${amount} for order #{order_id} has failed.</p>
    <p>Please try again or contact support.</p>
    """
    
    ORDER_STATUS_UPDATE = """
    <h2>Order Status Update</h2>
    <p>Dear {user_name},</p>
    <p>Your order #{order_id} status has been updated to: <strong>{status}</strong></p>
    <p>Track your order for more details.</p>
    """

async def send_email(recipients: List[str], subject: str, body: str):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="html"
        )
        await fm.send_message(message)
        logger.info(f"Email sent to {recipients}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")