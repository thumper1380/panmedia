from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from apps.users.models import User
from apps.users.forms import UserChangeForm, UserCreationForm
from django.contrib.admin import AdminSite








class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['email', 'is_admin']
    fieldsets = [
        ['Auth', {'fields': ['email', 'password']}],
        ['Settings', {'fields': ['is_admin', 'is_active',
                                 'is_staff', 'is_superuser', 'groups']}],
        ['Important dates', {'fields': ['last_login', 'registered_at']}],
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        [None, {'classes': ['wide'],
                'fields': ['email', 'first_name', 'last_name', 'password1', 'password2']}],
    ]
    search_fields = ['email']
    ordering = ['email']
    readonly_fields = ['last_login', 'registered_at']




# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# Unregister the Group model from admin.

# admin.site.unregister(Group)


