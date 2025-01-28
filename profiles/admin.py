from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_available_for_commissions')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'role')



