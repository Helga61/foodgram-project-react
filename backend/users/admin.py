from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User

from . import models


class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "is_staff",
    )


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')
    list_filter = ('author', 'user')


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
