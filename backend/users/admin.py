from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
        'role',)
    list_editable = ('role',)
    search_fields = ('username', 'email')
    list_filter = ()
    list_display_links = ('username',)
    empty_value_display = 'Не задано'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',)
    # list_editable = ('user',)
    search_fields = ('user', 'author')
    list_filter = ()
    # list_display_links = ('user',)
    empty_value_display = 'Не задано'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
