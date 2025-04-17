from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from .models import (
    User, Product, Order, Cart, CartProduct, 
    Payment, EWalletPayment, CreditCardPayment, 
    ShippingMethod, PaymentFactory, WarrantyDecorator, GiftWrapDecorator, CustomerProfile, Notification  # Added Notification import
)
from django.contrib import messages

@csrf_protect
def register(request):
    error_message = None
    if request.method == 'POST':
        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            
            # Validate input
            if not username or not email or not password:
                error_message = "All fields are required."
                return render(request, 'register.html', {'error_message': error_message})
            
            # Check if username exists
            if User.objects.filter(username=username).exists():
                error_message = "Username already exists. Please choose a different username."
                return render(request, 'register.html', {'error_message': error_message})
            
            # Check if email exists
            if User.objects.filter(email=email).exists():
                error_message = "Email already registered. Please use a different email."
                return render(request, 'register.html', {'error_message': error_message})
            
            # Create regular user (not admin)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_admin=False,  # Ensure this is a regular user
                is_staff=False,  # Not a staff user
                is_superuser=False  # Not a superuser
            )
            
            # Create cart for the user
            Cart.objects.create(user=user)
            
            # Log the user in and redirect
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return redirect('login')
                
        except IntegrityError as e:
            # If user was created but something failed, delete the user
            if 'user' in locals():
                user.delete()
            error_message = "Registration failed. Please try again with different information."
        except Exception as e:
            # If user was created but something failed, delete the user
            if 'user' in locals():
                user.delete()
            error_message = f"Registration failed: {str(e)}"
    
    return render(request, 'register.html', {'error_message': error_message})

@csrf_protect
def login_view(request):
    error_message = None
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            
            if not username or not password:
                error_message = "Both username and password are required."
                return render(request, 'login.html', {'error_message': error_message})
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user type
                if user.is_admin:
                    return redirect('admin:index')  # Redirect admin to Django admin interface
                else:
                    return redirect('home')  # Redirect regular users to home page
            else:
                error_message = "Invalid username or password."
        except Exception as e:
            error_message = f"Login failed: {str(e)}"
    
    return render(request, 'login.html', {'error_message': error_message})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    # For admin users, show admin dashboard
    if request.user.is_admin:
        # Get summary data for admin dashboard
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(order_status='PENDING').count()
        total_products = Product.objects.count()
        total_users = User.objects.filter(is_admin=False).count()
        
        context = {
            'is_admin': True,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_products': total_products,
            'total_users': total_users,
            'user': request.user
        }
        return render(request, 'admin_dashboard.html', context)
    
    # For regular users, show products
    products = Product.objects.all()
    return render(request, 'home.html', {
        'products': products,
        'is_admin': False,
        'user': request.user
    })

@login_required
@csrf_protect
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(user=request.user)
    
    # Create cart product
    cart_product = CartProduct.objects.create(
        cart=cart,
        product=product,
        quantity=1
    )
    
    # Add warranty if checkbox is checked
    if request.POST.get('warranty') == 'on':  # Check if warranty checkbox is checked
        warranty_duration = request.POST.get('warranty_duration')
        if warranty_duration:
            cart_product.warranty_duration = int(warranty_duration)
    
    # Add gift wrap if checkbox is checked
    if request.POST.get('gift_wrap') == 'on':  # Check if gift wrap checkbox is checked
        gift_wrap_type = request.POST.get('gift_wrap_type')
        if gift_wrap_type:
            cart_product.gift_wrap_type = gift_wrap_type.lower()
    
    cart_product.update_total_price()
    cart_product.save()
    
    return redirect('cart')

@login_required
@csrf_protect
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        
        # Check if cart is empty
        if not cart.cartproduct_set.exists():
            messages.error(request, "Your cart is empty")
            return redirect('cart')
        
        # Check if shipping method is selected
        if not cart.shipping_method:
            messages.error(request, "Please select a shipping method in your cart before proceeding to checkout")
            return redirect('cart')
        
        if request.method == 'POST':
            payment_type = request.POST.get('payment_type')
            if not payment_type:
                messages.error(request, "Please select a payment method")
                return render(request, 'checkout.html', {'cart': cart, 'error': 'Please select a payment method'})
            
            try:
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    order_status='PENDING',
                    shipping_method=cart.shipping_method
                )
                
                # Add admin users as observers
                admin_users = User.objects.filter(is_admin=True)
                order.observers.add(*admin_users)
                
                # Create payment data
                payment_data = {
                    'order': order,
                    'amount': cart.get_total(),
                }
                
                # Process payment based on type
                if payment_type == 'credit_card':
                    card_number = request.POST.get('card_number')
                    expiry_date = request.POST.get('expiry_date')
                    cvv = request.POST.get('cvv')
                    
                    if not all([card_number, expiry_date, cvv]):
                        raise ValueError("All credit card fields are required")
                    
                    payment_data.update({
                        'card_number': card_number,
                        'expiry_date': expiry_date,
                        'cvv': cvv
                    })
                    payment = PaymentFactory.create_payment('CreditCard', **payment_data)
                    
                elif payment_type == 'ewallet':
                    wallet_id = request.POST.get('wallet_id')
                    wallet_password = request.POST.get('wallet_password')
                    
                    if not all([wallet_id, wallet_password]):
                        raise ValueError("All e-wallet fields are required")
                    
                    payment_data.update({
                        'wallet_id': wallet_id,
                        'password': wallet_password
                    })
                    payment = PaymentFactory.create_payment('EWallet', **payment_data)
                
                # Process payment
                payment.process_payment()
                
                # Create notifications
                Notification.objects.create(
                    user=request.user,
                    order=order,
                    message=f"Order #{order.id} has been created and is pending"
                )
                
                for admin in admin_users:
                    Notification.objects.create(
                        user=admin,
                        order=order,
                        message=f"New order #{order.id} created by {request.user.username}"
                    )
                
                # Clear cart
                cart.cartproduct_set.all().delete()
                
                messages.success(request, "Order placed successfully!")
                return redirect('home')
                
            except Exception as e:
                if 'order' in locals():
                    order.delete()
                messages.error(request, str(e))
                return render(request, 'checkout.html', {
                    'cart': cart,
                    'error': str(e)
                })
        
        return render(request, 'checkout.html', {'cart': cart})
        
    except Cart.DoesNotExist:
        messages.error(request, "Cart not found")
        return redirect('home')

@login_required
def profile(request):
    # Check if user is admin
    if request.user.is_admin:
        return render(request, 'admin_profile.html', {'user': request.user})
    
    try:
        # Get the customer profile for regular users
        customer_profile = request.user.customer_profile
        
        if request.method == 'POST':
            # Update profile
            customer_profile.shipping_address = request.POST.get('shipping_address', '')
            customer_profile.contact_number = request.POST.get('contact_number', '')
            customer_profile.save()
            return redirect('profile')
            
        return render(request, 'profile.html', {'profile': customer_profile})
    except CustomerProfile.DoesNotExist:
        return redirect('home')

@login_required
def notifications(request):
    # Get all notifications for the user, ordered by most recent first
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'is_admin': request.user.is_admin
    }
    return render(request, 'notifications.html', context)

@login_required
@csrf_protect
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return redirect('notifications')
        except Notification.DoesNotExist:
            pass
    return redirect('notifications')

@login_required
@csrf_protect
def delete_cart_item(request, cart_product_id):
    try:
        # Get the cart product using the ID
        cart_product = CartProduct.objects.get(id=cart_product_id, cart__user=request.user)
        
        # Delete the cart product
        cart_product.delete()
        
        # Redirect to the cart page after deletion
        return redirect('cart')
    except CartProduct.DoesNotExist:
        # If the cart product doesn't exist or is not associated with the logged-in user
        return redirect('cart')

@login_required
@csrf_protect
def update_shipping(request):
    if request.method == 'POST':
        shipping_method_id = request.POST.get('shipping_method')
        if shipping_method_id:
            cart = Cart.objects.get(user=request.user)
            cart.shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
            cart.save()
    return redirect('cart')

@login_required
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        shipping_methods = ShippingMethod.objects.all()
        
        return render(request, 'cart.html', {
            'cart': cart,
            'shipping_methods': shipping_methods,
        })
    except Cart.DoesNotExist:
        return render(request, 'cart.html', {'error_message': 'Cart not found.'})

# Add this context processor to include unread_count in all views
def notification_processor(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}

@login_required
@csrf_protect
def update_order_status(request, order_id):
    if not request.user.is_admin:
        messages.error(request, "Only admin can update order status")
        return redirect('home')
        
    try:
        order = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        
        if new_status:
            # Update the status and notify observers
            order.update_status(new_status)
            messages.success(request, f"Order #{order.id} status updated to {new_status}")
        
        return redirect('admin_dashboard')  # or wherever you want to redirect
        
    except Order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('admin_dashboard')

@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        messages.error(request, "Access denied")
        return redirect('home')
        
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'admin_dashboard.html', {
        'orders': orders
    })
