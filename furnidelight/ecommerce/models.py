from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Observer Pattern: User class acts as an observer that gets notified of order status changes
class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    
    # Required for custom user model in Django
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
    )

    # Observer Pattern: Method called when an order status changes
    def update(self, order):
        Notification.objects.create(
            user=self,
            order=order,
            message=f"Order #{order.id} status updated to {order.get_order_status_display()}"
        )

    # Single Responsibility Principle: User class handles user-specific logic
    def save(self, *args, **kwargs):
        if self.is_admin:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'user'

# Observer Pattern: Order class acts as the subject being observed
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(
        max_length=50, 
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('SHIPPED', 'Shipped'),
            ('DELIVERED', 'Delivered'),
            ('CANCELLED', 'Cancelled')
        ],
        default='PENDING'
    )
    shipping_method = models.ForeignKey('ShippingMethod', on_delete=models.CASCADE)
    observers = models.ManyToManyField(User, related_name='observed_orders')

    def notify_observers(self):
        """Create notifications for all observers when order status changes"""
        # Always create notification for the customer
        Notification.objects.create(
            user=self.user,
            order=self,
            message=f"Your order #{self.id} status has been updated to {self.get_order_status_display()}"
        )
        
        # Create notifications for admin users
        admin_users = User.objects.filter(is_admin=True)
        for admin in admin_users:
            if admin != self.user:
                Notification.objects.create(
                    user=admin,
                    order=self,
                    message=f"Order #{self.id} for {self.user.username} has been updated to {self.get_order_status_display()}"
                )

    def update_status(self, new_status):
        """Update order status and notify observers"""
        new_status = new_status.upper()  # Convert to uppercase to match choices
        if new_status in dict(self._meta.get_field('order_status').choices):
            old_status = self.order_status
            self.order_status = new_status
            self.save()
            
            # Only notify if status actually changed
            if old_status != new_status:
                self.notify_observers()
        else:
            raise ValueError(f"Invalid order status: {new_status}")

    def update_product_quantities(self):
        """Decrease product quantities after successful order"""
        cart = self.user.cart
        for cart_product in cart.cartproduct_set.all():
            product = cart_product.product
            if product.quantity >= cart_product.quantity:
                product.quantity -= cart_product.quantity
                product.save()
            else:
                raise ValueError(f"Insufficient stock for {product.name}")

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new orders
            try:
                # First validate all quantities
                cart = self.user.cart
                for cart_product in cart.cartproduct_set.all():
                    if cart_product.product.quantity < cart_product.quantity:
                        raise ValueError(f"Insufficient stock for {cart_product.product.name}")
                
                # Then update quantities
                self.update_product_quantities()
                
            except Exception as e:
                raise ValueError(f"Order creation failed: {str(e)}")
        
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'order'

# Single Responsibility Principle: Handles user profile data separately from User model
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    shipping_address = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)

    # Open/Closed Principle: Validation logic can be extended without modifying the class
    def save(self, *args, **kwargs):
        if not self.user.is_admin:
            super().save(*args, **kwargs)
        else:
            raise ValueError("Admin users cannot have customer profiles")

    class Meta:
        db_table = 'customer_profile'

# Decorator Pattern: Base Product class that can be decorated
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def get_price(self):
        return self.price

    def get_description(self):
        return self.description

    class Meta:
        db_table = 'product'

# Decorator Pattern: Base decorator class
class ProductDecorator(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def get_price(self):
        return self.product.get_price()

    def get_description(self):
        return self.product.get_description()

    class Meta:
        abstract = True

# Decorator Pattern: Concrete decorator for warranty
class WarrantyDecorator(ProductDecorator):
    warranty_duration = models.IntegerField(
        default=12,
        choices=[
            (12, '12 months'),  # $30
            (24, '24 months'),  # $60
            (36, '36 months')   # $90
        ]
    )

    def get_price(self):
        # Include both product price and warranty cost
        base_price = self.product.get_price()
        warranty_prices = {
            12: 30,  # $30 for 12 months
            24: 60,  # $60 for 24 months
            36: 90   # $90 for 36 months
        }
        warranty_cost = warranty_prices.get(self.warranty_duration, 0)
        return base_price + warranty_cost

    def get_description(self):
        return f"{self.product.get_description()} (with {self.warranty_duration}-month warranty)"

    class Meta:
        db_table = 'warranty_decorator'

# Decorator Pattern: Concrete decorator for gift wrapping
class GiftWrapDecorator(ProductDecorator):
    WRAP_CHOICES = [
        ('normal', 'Normal'),    # $10
        ('premium', 'Premium'),  # $15
        ('luxury', 'Luxury')     # $20
    ]
    gift_wrap_type = models.CharField(
        max_length=50,
        choices=WRAP_CHOICES,
        default='normal'
    )

    def get_price(self):
        # Include both product price and gift wrap cost
        base_price = self.product.get_price()
        gift_wrap_prices = {
            'normal': 10,    # $10 for normal
            'premium': 15,   # $15 for premium
            'luxury': 20     # $20 for luxury
        }
        gift_wrap_cost = gift_wrap_prices.get(self.gift_wrap_type, 10)
        return base_price + gift_wrap_cost

    def get_description(self):
        return f"{self.product.get_description()} (Gift wrapped - {self.get_gift_wrap_type_display()})"

    class Meta:
        db_table = 'gift_wrap_decorator'

# Factory Method Pattern: Base Payment class
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, choices=[
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ], default='PENDING')

    # Template Method Pattern: Subclasses must implement this method
    def process_payment(self):
        raise NotImplementedError("Subclasses should implement this method.")

    class Meta:
        db_table = 'payment'

# Factory Method Pattern: Concrete Payment type
class EWalletPayment(Payment):
    wallet_id = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def process_payment(self):
        print(f"Processing e-wallet payment with wallet ID {self.wallet_id}")

    class Meta:
        db_table = 'ewallet_payment'

# Factory Method Pattern: Another concrete Payment type
class CreditCardPayment(Payment):
    card_number = models.CharField(max_length=16)
    expiry_date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=4)

    def process_payment(self):
        print(f"Processing credit card payment with card number {self.card_number}")

    class Meta:
        db_table = 'credit_card_payment'

# Factory Method Pattern: Factory class for creating payments
class PaymentFactory:
    @staticmethod
    def create_payment(payment_type, **kwargs):
        if payment_type == 'EWallet':
            return EWalletPayment.objects.create(**kwargs)
        elif payment_type == 'CreditCard':
            return CreditCardPayment.objects.create(**kwargs)
        else:
            raise ValueError("Invalid payment type")

# Strategy Pattern: Base shipping method class
class ShippingMethod(models.Model):
    description = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_cost(self):
        """Base implementation returns the stored cost"""
        return self.cost

    def __str__(self):
        return f"{self.description} (${self.cost})"

    class Meta:
        db_table = 'shipping_method'

# Strategy Pattern: Concrete shipping strategy
class AirShipping(ShippingMethod):
    tracking_id = models.CharField(max_length=50, null=True, blank=True)
    shipping_date = models.DateField(null=True, blank=True)
    shipping_status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'air_shipping'

# Strategy Pattern: Another concrete shipping strategy
class GroundShipping(ShippingMethod):
    tracking_id = models.CharField(max_length=50, null=True, blank=True)
    shipping_date = models.DateField(null=True, blank=True)
    shipping_status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'ground_shipping'


# Single Responsibility Principle: Cart handles shopping cart functionality
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartProduct')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True, blank=True)
    
    def get_subtotal(self):
        """Get cart subtotal before shipping"""
        return sum(cart_product.get_total_price() for cart_product in self.cartproduct_set.all())
    
    def get_shipping_cost(self):
        """Get shipping cost if shipping method is selected"""
        if self.shipping_method:
            return self.shipping_method.calculate_cost()
        return 0
    
    def get_total(self):
        """Get cart total including products, decorators, and shipping"""
        subtotal = self.get_subtotal()
        shipping_cost = self.get_shipping_cost()
        return subtotal + shipping_cost
    
    class Meta:
        db_table = 'cart'

# Single Responsibility Principle: CartProduct handles the relationship between Cart and Product
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    warranty_duration = models.IntegerField(
        null=True, 
        blank=True,
        choices=[
            (12, '12 months'),  # $30
            (24, '24 months'),  # $60
            (36, '36 months')   # $90
        ]
    )
    gift_wrap_type = models.CharField(
        max_length=50,
        null=True, 
        blank=True,
        choices=[
            ('normal', 'Normal'),    # $10
            ('premium', 'Premium'),  # $15
            ('luxury', 'Luxury')     # $20
        ]
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def get_subtotal(self):
        """Get the base product price * quantity"""
        return self.product.get_price() * self.quantity

    def get_warranty_cost(self):
        """Get warranty cost if selected"""
        if self.warranty_duration:
            warranty_prices = {
                12: 30,  # $30 for 12 months
                24: 60,  # $60 for 24 months
                36: 90   # $90 for 36 months
            }
            return warranty_prices.get(self.warranty_duration, 0)
        return 0

    def get_gift_wrap_cost(self):
        """Get gift wrap cost if selected"""
        if self.gift_wrap_type:
            gift_wrap_prices = {
                'normal': 10,    # $10 for normal
                'premium': 15,   # $15 for premium
                'luxury': 20     # $20 for luxury
            }
            return gift_wrap_prices.get(self.gift_wrap_type, 0)
        return 0

    def update_total_price(self):
        """Calculate and update total price"""
        subtotal = self.get_subtotal()
        warranty_cost = self.get_warranty_cost()
        gift_wrap_cost = self.get_gift_wrap_cost()
        
        self.total_price = subtotal + warranty_cost + gift_wrap_cost
        self.save()

    def get_total_price(self):
        return self.total_price

    def __str__(self):
        base_desc = f"{self.quantity} x {self.product.name}"
        desc_parts = [
            f"Price: ${self.product.price}",
            f"Subtotal: ${self.get_subtotal()}"
        ]
        
        if self.warranty_duration:
            warranty_cost = self.get_warranty_cost()
            desc_parts.append(f"Warranty ({self.warranty_duration} months): +${warranty_cost}")
            
        if self.gift_wrap_type:
            gift_cost = self.get_gift_wrap_cost()
            desc_parts.append(f"Gift wrap ({self.gift_wrap_type}): +${gift_cost}")
            
        desc_parts.append(f"Total: ${self.total_price}")
        
        return f"{base_desc}\n" + "\n".join(desc_parts)


# Signal handlers for automatic profile creation
@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    # Only create customer profile for non-admin users
    if created and not instance.is_admin:
        CustomerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    # Only save/update customer profile for non-admin users
    if not instance.is_admin:
        try:
            instance.customer_profile.save()
        except CustomerProfile.DoesNotExist:
            CustomerProfile.objects.create(user=instance)

# Observer Pattern: Notification model for storing notifications
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'notification'