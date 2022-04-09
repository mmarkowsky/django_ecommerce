from django.contrib import admin
from accounts.models import Account
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ("email","first_name","last_name","username","last_login","data_joined","is_active")
    list_display_link = ("email","first_name","last_name")
    readonly_fields = ("last_login","data_joined")
    ordering = ("-data_joined",)

    filter_horizontal = ()
    list_filter = () 
    fieldsets = ()

admin.site.register(Account,AccountAdmin)