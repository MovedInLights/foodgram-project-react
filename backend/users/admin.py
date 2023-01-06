from django.contrib import admin
from .models import User


class UserAdm(admin.ModelAdmin):
    model = User
    list_display = ('username', 'first_name', 'last_name', 'email',)
    list_display_links = ('username',)
    list_filter = ['username', 'email']


admin.site.register(User, UserAdm)
