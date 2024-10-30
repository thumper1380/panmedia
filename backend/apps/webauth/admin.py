from django.contrib import admin

# Register your models here.
from .models import WebauthnCredentials, WebauthnRegistration, WebauthnAuthentication, WebAuthDevice


admin.site.register(WebauthnCredentials)
admin.site.register(WebauthnRegistration)
admin.site.register(WebauthnAuthentication)
admin.site.register(WebAuthDevice)