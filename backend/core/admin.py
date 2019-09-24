from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import *
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils.safestring import mark_safe

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'api_key', 'api_secret_key', 'currency' )

class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'api_key', 'api_secret_key', 'currency', 'password')}),
        (_('Personal info'), {'fields': ()}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','api_key', 'api_secret_key', 'currency',  'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email',  'api_key','api_secret_key', 'currency', 'is_staff',)
    search_fields = ('email',)
    ordering = ('email',)

class SymbolAdmin(admin.ModelAdmin):
    #list_display = [field.name for field in Symbol._meta.get_fields()]
    list_display = ['symbol', 'from_currency', 'to_currency', 'side']

class OrderSequenceAdmin(admin.ModelAdmin):
    list_display = ['t1', 't2', 't3']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'order_id', 'quantity', 'quote_quantity', 'price', 'time', 'status']


class OrderSequenceResultAdmin(admin.ModelAdmin):
    list_display = ['master', 't1_result', 't2_result', 't3_result', 'profit']


admin.site.register(User, MyUserAdmin)
admin.site.register(Symbol, SymbolAdmin)
admin.site.register(OrderSequence, OrderSequenceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderSequenceResult, OrderSequenceResultAdmin)