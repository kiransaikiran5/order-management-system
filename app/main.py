from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.core.middleware import PerformanceMiddleware
from app.routers import auth, users, products, orders, payments
import logging

# Create tables
Base.metadata.create_all(bind=engine)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Order Management System",
    description="Complete order management system with JWT authentication, email notifications, and advanced features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add performance monitoring
app.add_middleware(PerformanceMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(payments.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Order Management System",
        "version": "2.0.0",
        "features": {
            "authentication": "JWT with refresh tokens",
            "authorization": "Role-based access control",
            "products": "CRUD with pagination, filtering, sorting",
            "orders": "Complete order lifecycle management",
            "payments": "Simulated payment processing",
            "email": "Automated email notifications",
            "performance": "Optimized queries with indexes"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": "2.0.0"
    }