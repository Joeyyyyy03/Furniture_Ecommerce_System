# FurniDelight E-commerce System

A Django-based e-commerce system for furniture with advanced design patterns and principles.

## Features

- User Authentication (Admin and Regular Users)
- Product Management with Decorators (Warranty and Gift Wrapping)
- Shopping Cart System
- Multiple Payment Methods (Credit Card and E-Wallet)
- Order Management with Status Notifications
- Multiple Shipping Methods
- Real-time Order Status Updates
- User Profile Management

## Design Patterns Implemented

1. **Observer Pattern**: Order status notifications
2. **Decorator Pattern**: Product customization (warranty, gift wrapping)
3. **Factory Method Pattern**: Payment method creation
4. **Strategy Pattern**: Shipping method calculation
5. **Template Method Pattern**: Payment processing

## Prerequisites

- Python 3.13.0 or higher
- Django 5.1.5
- SQLite3

## Installation Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd FurniDelight
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django==5.1.5
   ```

4. **Initialize Database**
   ```bash
   pip install django==5.1.5
   ```

5. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   # Follow the prompts to create admin account
   ```

6. **Run Development Server**
   ```bash
   python manage.py createsuperuser
   ```

## System Usage

### Admin User

1. **Access Admin Interface**
   - Go to: http://127.0.0.1:8000/admin/
   - Login with superuser credentials

2. **Admin Dashboard Features**
   - Manage Products
   - View Orders
   - Monitor Users
   - Track Sales
   - Handle Shipping Methods

### Regular User

1. **Register New Account**
   - Go to: http://127.0.0.1:8000/register/
   - Fill in required information

2. **Shopping Process**
   - Browse products on home page
   - Add items to cart
   - Select product decorators (warranty/gift wrap)
   - Proceed to checkout
   - Choose shipping method
   - Select payment method
   - Complete order

3. **User Features**
   - View order history
   - Track order status
   - Receive notifications
   - Update profile information

## Testing the Features

1. **Product Decoration**
   - Add product to cart
   - Select warranty option
   - Add gift wrapping
   - Verify price changes

2. **Payment Methods**
   - Test Credit Card payment
   - Test E-Wallet payment

3. **Shipping Methods**
   - Try different shipping options
   - Verify cost calculations

4. **Order Status Updates**
   - Place an order
   - Login as admin
   - Change order status
   - Verify notifications

## Database Tables

- user
- customer_profile
- product
- warranty_decorator
- gift_wrap_decorator
- payment
- ewallet_payment
- credit_card_payment
- shipping_method
- air_shipping
- ground_shipping
- cart
- cart_product
- order
- notification

## Troubleshooting

1. **Database Issues**
   ```bash
   # Reset database
   rm db.sqlite3
   rm -r ecommerce/migrations
   python manage.py makemigrations ecommerce
   python manage.py migrate
   python manage.py createsuperuser
   ```

2. **Server Issues**
   ```bash
   # Kill existing server
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F

   # Linux/Mac
   lsof -i :8000
   kill -9 <PID>
   ```

## Security Notes

- Default DEBUG mode is True (development only)
- Change SECRET_KEY in production
- Set DEBUG=False in production
- Update ALLOWED_HOSTS for production

## Support

For any issues or questions, please:
1. Check the troubleshooting section
2. Review Django documentation
3. Contact system administrator

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request 