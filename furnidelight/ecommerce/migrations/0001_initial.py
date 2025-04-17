# Generated by Django 4.2.18 on 2025-01-27 06:29

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='custom_user_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='custom_user_set', to='auth.permission')),
            ],
            options={
                'db_table': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'cart',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('order_status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], max_length=50)),
                ('observers', models.ManyToManyField(related_name='observed_orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'order',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING', max_length=50)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.order')),
            ],
            options={
                'db_table': 'payment',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
            ],
            options={
                'db_table': 'product',
            },
        ),
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'shipping_method',
            },
        ),
        migrations.CreateModel(
            name='AirShipping',
            fields=[
                ('shippingmethod_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ecommerce.shippingmethod')),
                ('tracking_id', models.CharField(max_length=50)),
                ('shipping_date', models.DateField()),
                ('shipping_status', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'air_shipping',
            },
            bases=('ecommerce.shippingmethod',),
        ),
        migrations.CreateModel(
            name='CreditCardPayment',
            fields=[
                ('payment_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ecommerce.payment')),
                ('card_number', models.CharField(max_length=16)),
                ('expiry_date', models.CharField(max_length=5)),
                ('cvv', models.CharField(max_length=4)),
            ],
            options={
                'db_table': 'credit_card_payment',
            },
            bases=('ecommerce.payment',),
        ),
        migrations.CreateModel(
            name='EWalletPayment',
            fields=[
                ('payment_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ecommerce.payment')),
                ('wallet_id', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'ewallet_payment',
            },
            bases=('ecommerce.payment',),
        ),
        migrations.CreateModel(
            name='GroundShipping',
            fields=[
                ('shippingmethod_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ecommerce.shippingmethod')),
                ('tracking_id', models.CharField(max_length=50)),
                ('shipping_date', models.DateField()),
                ('shipping_status', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'ground_shipping',
            },
            bases=('ecommerce.shippingmethod',),
        ),
        migrations.CreateModel(
            name='WarrantyDecorator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warranty_duration', models.IntegerField(default=12)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.product')),
            ],
            options={
                'db_table': 'warranty_decorator',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.shippingmethod'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notification',
            },
        ),
        migrations.CreateModel(
            name='GiftWrapDecorator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gift_wrap_type', models.CharField(choices=[('standard', 'Standard'), ('premium', 'Premium'), ('luxury', 'Luxury')], default='standard', max_length=50)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.product')),
            ],
            options={
                'db_table': 'gift_wrap_decorator',
            },
        ),
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipping_address', models.CharField(blank=True, max_length=255)),
                ('contact_number', models.CharField(blank=True, max_length=15)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'customer_profile',
            },
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('warranty_duration', models.IntegerField(blank=True, choices=[(12, '12 months'), (24, '24 months'), (36, '36 months')], null=True)),
                ('gift_wrap_type', models.CharField(blank=True, choices=[('normal', 'Normal'), ('premium', 'Premium'), ('luxury', 'Luxury')], max_length=50, null=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(through='ecommerce.CartProduct', to='ecommerce.product'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
