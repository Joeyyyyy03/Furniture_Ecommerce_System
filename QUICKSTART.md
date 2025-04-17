# FurniDelight Quick Start Guide

## Quick Setup (Windows)

1. **Setup Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install django==5.1.5
   ```

2. **Reset Database**
   ```powershell
   Remove-Item -Path "db.sqlite3" -Force -ErrorAction SilentlyContinue
   Get-ChildItem -Path "ecommerce\migrations" -Exclude "__init__.py" | Remove-Item -Force
   python manage.py makemigrations ecommerce
   python manage.py migrate
   ```

3. **Create Admin User**
   ```powershell
   python manage.py createsuperuser
   # Username: admin
   # Email: admin@example.com
   # Password: admin123
   ```

4. **Run Server**
   ```powershell
      python manage.py runserver
   ```

## Test Scenarios

### 1. Admin Setup
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Add some products:
   - Add at least 3 furniture items
   - Set different prices
   - Add descriptions

### 2. Regular User Shopping
1. Go to http://127.0.0.1:8000/register/
2. Register new account
3. Browse products
4. Add items to cart with:
   - Warranty option
   - Gift wrapping

### 3. Checkout Process
1. Go to cart
2. Proceed to checkout
3. Select shipping method
4. Choose payment method:
   - Try credit card
   - Try e-wallet

### 4. Order Management (Admin)
1. Login as admin
2. Go to Orders
3. Change order status
4. Check notifications

### 5. User Notifications
1. Login as regular user
2. Check notifications
3. Mark as read

## Test Data

### Sample Products
1. Modern Sofa
   - Price: $999.99
   - Description: "Comfortable 3-seater sofa"

2. Dining Table
   - Price: $599.99
   - Description: "6-person wooden dining table"

3. Bed Frame
   - Price: $799.99
   - Description: "Queen size bed frame with storage"

### Test Credit Card
- Number: 4111111111111111
- Expiry: 12/25
- CVV: 123

### Test E-Wallet
- ID: TEST_WALLET
- Password: test123

## Common Issues

1. **Server Already Running**
   ```powershell
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Database Errors**
   - Follow Reset Database steps above

3. **Login Issues**
   - Clear browser cookies
   - Try incognito mode 