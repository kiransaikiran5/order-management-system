from jinja2 import Template
from typing import Dict, Any

class EmailTemplates:
    """HTML email templates"""
    
    # Base template wrapper
    BASE_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }
            .content {
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }
            .order-details {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }
            .order-item {
                border-bottom: 1px solid #eee;
                padding: 10px 0;
            }
            .total {
                font-size: 18px;
                font-weight: bold;
                text-align: right;
                margin-top: 15px;
                padding-top: 15px;
                border-top: 2px solid #4CAF50;
            }
            .status {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            .status-pending { background-color: #ffc107; color: #333; }
            .status-confirmed { background-color: #17a2b8; color: white; }
            .status-shipped { background-color: #007bff; color: white; }
            .status-delivered { background-color: #28a745; color: white; }
            .status-cancelled { background-color: #dc3545; color: white; }
            .button {
                display: inline-block;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{{ title }}</h1>
            </div>
            <div class="content">
                {{ content | safe }}
            </div>
            <div class="footer">
                <p>Thank you for shopping with us!</p>
                <p>&copy; 2024 Order Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    @staticmethod
    def render_template(template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        templates = {
            "order_confirmation": """
            <h2>Hello {{ user_name }},</h2>
            <p>Thank you for your order! Your order has been confirmed and is being processed.</p>
            
            <div class="order-details">
                <h3>Order #{{ order_id }}</h3>
                <p><strong>Order Date:</strong> {{ order_date }}</p>
                <p><strong>Status:</strong> 
                    <span class="status status-{{ status }}">{{ status|upper }}</span>
                </p>
                
                <h4>Order Items:</h4>
                {% for item in items %}
                <div class="order-item">
                    <strong>{{ item.product_name }}</strong><br>
                    Quantity: {{ item.quantity }} × ${{ "%.2f"|format(item.price) }} = ${{ "%.2f"|format(item.quantity * item.price) }}
                </div>
                {% endfor %}
                
                <div class="total">
                    Total Amount: ${{ "%.2f"|format(total_amount) }}
                </div>
            </div>
            
            <p>We'll notify you once your order is shipped.</p>
            <a href="{{ track_url }}" class="button">Track Your Order</a>
            """,
            
            "payment_success": """
            <h2>Hello {{ user_name }},</h2>
            <p>Great news! Your payment has been processed successfully.</p>
            
            <div class="order-details">
                <h3>Payment Details</h3>
                <p><strong>Order #:</strong> {{ order_id }}</p>
                <p><strong>Amount:</strong> ${{ "%.2f"|format(amount) }}</p>
                <p><strong>Payment Method:</strong> {{ payment_method|replace("_", " ")|title }}</p>
                <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
                <p><strong>Date:</strong> {{ payment_date }}</p>
            </div>
            
            <p>Your order is now confirmed and will be prepared for shipping.</p>
            """,
            
            "payment_failed": """
            <h2>Hello {{ user_name }},</h2>
            <p>We're sorry, but your payment could not be processed.</p>
            
            <div class="order-details">
                <h3>Payment Details</h3>
                <p><strong>Order #:</strong> {{ order_id }}</p>
                <p><strong>Amount:</strong> ${{ "%.2f"|format(amount) }}</p>
                <p><strong>Payment Method:</strong> {{ payment_method|replace("_", " ")|title }}</p>
                <p><strong>Status:</strong> Failed</p>
            </div>
            
            <h3>Possible Reasons:</h3>
            <ul>
                <li>Insufficient funds</li>
                <li>Incorrect payment details</li>
                <li>Bank declined the transaction</li>
            </ul>
            
            <p>Please try again with a different payment method or contact your bank.</p>
            <a href="{{ retry_url }}" class="button">Try Again</a>
            """,
            
            "order_status_update": """
            <h2>Hello {{ user_name }},</h2>
            <p>Your order status has been updated!</p>
            
            <div class="order-details">
                <h3>Order #{{ order_id }}</h3>
                <p><strong>New Status:</strong> 
                    <span class="status status-{{ new_status }}">{{ new_status|upper }}</span>
                </p>
                <p><strong>Previous Status:</strong> {{ old_status|upper }}</p>
                <p><strong>Update Time:</strong> {{ update_time }}</p>
            </div>
            
            {% if new_status == 'shipped' %}
            <div class="order-details">
                <h3>Shipping Information</h3>
                <p><strong>Tracking Number:</strong> {{ tracking_number }}</p>
                <p><strong>Carrier:</strong> {{ carrier }}</p>
                <p><strong>Estimated Delivery:</strong> {{ estimated_delivery }}</p>
            </div>
            <a href="{{ tracking_url }}" class="button">Track Shipment</a>
            {% elif new_status == 'delivered' %}
            <p>We hope you enjoy your purchase! If you have any issues, please contact our support team.</p>
            {% endif %}
            """,
            
            "order_cancelled": """
            <h2>Hello {{ user_name }},</h2>
            <p>Your order has been cancelled as requested.</p>
            
            <div class="order-details">
                <h3>Order #{{ order_id }}</h3>
                <p><strong>Cancelled Date:</strong> {{ cancel_date }}</p>
                <p><strong>Total Amount:</strong> ${{ "%.2f"|format(total_amount) }}</p>
            </div>
            
            {% if was_paid %}
            <div class="order-details">
                <h3>Refund Information</h3>
                <p>A refund of <strong>${{ "%.2f"|format(total_amount) }}</strong> will be processed to your original payment method within 5-7 business days.</p>
            </div>
            {% endif %}
            
            <p>We're sorry to see you go. If you changed your mind, you can place a new order anytime.</p>
            """,
            
            "welcome_email": """
            <h2>Welcome to Order Management System, {{ user_name }}!</h2>
            <p>We're excited to have you on board!</p>
            
            <h3>Getting Started:</h3>
            <ul>
                <li>Browse our wide selection of products</li>
                <li>Create your first order</li>
                <li>Track your orders in real-time</li>
                <li>Get exclusive offers and discounts</li>
            </ul>
            
            <p>If you have any questions, our support team is here to help 24/7.</p>
            <a href="{{ shop_url }}" class="button">Start Shopping</a>
            """
        }
        
        template_content = templates.get(template_name, "")
        if not template_content:
            raise ValueError(f"Template {template_name} not found")
        
        # Render template with context
        template = Template(template_content)
        rendered_content = template.render(**context)
        
        # Wrap in base template
        base_template = Template(EmailTemplates.BASE_TEMPLATE)
        return base_template.render(
            title=context.get("title", "Order Management System"),
            content=rendered_content
        )