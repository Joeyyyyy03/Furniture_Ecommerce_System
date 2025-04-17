from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('cart/delete/<int:cart_product_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('update-shipping/', views.update_shipping, name='update_shipping'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
