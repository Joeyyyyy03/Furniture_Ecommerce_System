from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, CustomerProfile, Product, Order, Cart, CartProduct,
    Payment, EWalletPayment, CreditCardPayment,
    ShippingMethod, Notification
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_staff')
    list_filter = ('is_admin', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_admin',)}),
    )

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'shipping_address', 'contact_number')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity')
    search_fields = ('name', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_date', 'order_status']
    list_filter = ['order_status']
    search_fields = ['user__username', 'id']
    actions = ['make_processing', 'make_shipped', 'make_delivered', 'make_cancelled']

    def make_processing(self, request, queryset):
        for order in queryset:
            order.update_status('PROCESSING')
    make_processing.short_description = "Mark selected orders as Processing"

    def make_shipped(self, request, queryset):
        for order in queryset:
            order.update_status('SHIPPED')
    make_shipped.short_description = "Mark selected orders as Shipped"

    def make_delivered(self, request, queryset):
        for order in queryset:
            order.update_status('DELIVERED')
    make_delivered.short_description = "Mark selected orders as Delivered"

    def make_cancelled(self, request, queryset):
        for order in queryset:
            order.update_status('CANCELLED')
    make_cancelled.short_description = "Mark selected orders as Cancelled"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(CartProduct)
class CartProductAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount')

@admin.register(EWalletPayment)
class EWalletPaymentAdmin(PaymentAdmin):
    list_display = PaymentAdmin.list_display + ('wallet_id',)

@admin.register(CreditCardPayment)
class CreditCardPaymentAdmin(PaymentAdmin):
    list_display = PaymentAdmin.list_display + ('card_number',)

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('description', 'cost')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'order', 'created_at', 'is_read']
    list_filter = ['is_read']
    search_fields = ['user__username', 'order__id']
