
 Order Management System
 
A production-ready backend built with FastAPI, MySQL, and JWT Authentication.

## ✨ Overview

A **production-ready backend system** for managing an e-commerce platform with:

* 🔐 Secure Authentication (JWT)
* 🛍️ Product Management
* 📦 Order Processing
* 💳 Payment Simulation
* 📧 Email Notifications
* 📊 Advanced Query Features

---

## 🔥 Key Features

### 🔐 Authentication & Security

* JWT Access + Refresh Tokens
* Password hashing (bcrypt)
* Role-Based Access Control (Admin / Customer)
* Secure API endpoints

### 🛍️ Product Management

* Full CRUD operations
* Stock management
* Price filtering
* Search & sorting

### 📦 Order System

* Multi-item orders
* Order lifecycle tracking
* Stock validation
* Cancel & restore stock

### 💳 Payment System

* Simulated payment gateway
* Success/failure handling
* Transaction tracking

### 📧 Email Notifications

* Order confirmation
* Payment updates
* Shipping notifications
* Background task processing

---

## 🏗️ Architecture

```
app/
├── core/        # Security, config, email
├── models/      # SQLAlchemy models
├── schemas/     # Pydantic schemas
├── routers/     # API routes
├── services/    # Business logic
├── deps/        # Dependencies
```

---

## 🚀 Quick Start

### 1️⃣ Clone Repo

```bash
git clone https://github.com/your-username/order-management.git
cd order-management
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\\Scripts\\activate    # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables

Create `.env` file:

```env
SECRET_KEY=supersecret
ALGORITHM=HS256
DATABASE_URL=mysql+pymysql://root:password@localhost/order_db
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 5️⃣ Run Server

```bash
uvicorn app.main:app --reload
```

---

## 📡 API Docs

| Tool       | URL                         |
| ---------- | --------------------------- |
| Swagger UI | http://localhost:8000/docs  |
| ReDoc      | http://localhost:8000/redoc |

---

## 🔐 Default Users

| Role     | Email                                               | Password     |
| -------- | --------------------------------------------------- | ------------ |
| Admin    | [admin@example.com](mailto:admin@example.com)       | Admin@123    |
| Customer | [customer@example.com](mailto:customer@example.com) | Customer@123 |

---

## 📊 Database Schema

### Core Tables

* Users
* Products
* Orders
* OrderItems
* Payments

### Relationships

```
User → Orders → OrderItems → Products
Order → Payment
```

---

## 🔄 Sample Flow

```text
Register → Login → Create Product (Admin)
        → Place Order (Customer)
        → Payment → Order Confirmed
        → Shipped → Delivered
```

---

## 📧 Email System

* Uses FastAPI BackgroundTasks
* Triggered on:

  * Order creation
  * Payment status
  * Shipping updates

---

## 🧪 Testing

### Swagger

* Interactive API testing

### Postman

* Import collection
* Test full flow

---

## 🐳 Docker (Optional)

```bash
docker build -t order-system .
docker run -p 8000:8000 order-system
```

---

## 📈 Performance Features

* Pagination (limit/offset)
* Indexed queries
* Optimized joins
* Lazy loading relationships

---

## 🔒 Security

* Hashed passwords
* Token expiration
* Role-based access
* Input validation

---

## 📁 Project Structure

```
order_management/
├── app/
├── .env
├── requirements.txt
├── README.md
```

---

## 🤝 Contributing

```bash
fork → create branch → commit → push → PR
```

---

## 📄 License

MIT License © 2026

---

## ⭐ Support

If you like this project:

👉 Star ⭐ the repo
👉 Share with others
👉 Contribute improvements

---
🔥 Built with FastAPI for scalable backend systems

