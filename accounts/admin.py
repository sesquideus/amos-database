from admin_decorators import short_description
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from . import models

class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class ProfileAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'getLocation']

    @short_description('Location')
    def getLocation(self, instance):
        return instance.profile.formatLocation()
        
    def get_inline_instances(self, request, obj = None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, ProfileAdmin)


# Register your models here.
