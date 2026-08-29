from django.contrib import admin
from main.models.user_manager import UserManager
from main.models.user_app import UserApp
from main.models.restaurant import Restaurant


@admin.register(UserManager)
class UserManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'restaurant_count', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'restaurant_count')


@admin.register(UserApp)
class UserAppAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'last_login')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cnpj', 'manager', 'contact_phone', 'created_at')
    search_fields = ('name', 'cnpj', 'address', 'contact_phone')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
