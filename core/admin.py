"""
core/admin.py
Register models in Django's built-in admin panel.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Opportunity, Application


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display   = ['email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter    = ['role', 'is_active', 'is_staff']
    search_fields  = ['email', 'first_name', 'last_name']
    ordering       = ['-created_at']
    fieldsets      = (
        (None,           {'fields': ('email', 'password')}),
        ('Personal',     {'fields': ('first_name', 'last_name')}),
        ('Role',         {'fields': ('role',)}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates',        {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'university', 'course', 'level', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'university']
    raw_id_fields = ['user']


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display   = ['title', 'company', 'type', 'mode', 'status', 'deadline', 'created_at']
    list_filter    = ['type', 'status', 'mode']
    search_fields  = ['title', 'company', 'location']
    ordering       = ['-created_at']
    list_editable  = ['status']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ['student', 'opportunity', 'status', 'applied_at']
    list_filter   = ['status']
    search_fields = ['student__email', 'opportunity__title', 'opportunity__company']
    ordering      = ['-applied_at']
    list_editable = ['status']
