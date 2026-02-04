
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# class CustomUserAdmin(UserAdmin):
#     list_display = ('email', 'phone', 'role', 'is_staff')  # Fields to show in the table
#     list_filter = ('role', 'is_staff', 'is_superuser')    # Filters on the right
#     search_fields = ('email', 'phone')                    # Searchable fields
#     ordering = ('email',)                                 # Default ordering

#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal Info', {'fields': ('phone', 'role')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important Dates', {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'phone', 'role', 'password1', 'password2'),
#         }),
#     )

# admin.site.register(CustomUser, CustomUserAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone_number', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'phone_number', 'role', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)