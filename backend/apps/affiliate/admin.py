from .models import FacebookPixel, Proxy
from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.contrib.admin.widgets import AdminTextInputWidget
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from apps.users.models import User
from config.adminsites import affiliate_site, network_site

from .models import (APIToken, Affiliate, AffiliateRequestLog, 
                     TelegramProfile, EventNotification,
                     IPWhitelist, Pixel, Postback, )


from django.utils.translation import gettext_lazy as _




class AdminFooWidget(AdminTextInputWidget):

    def lead_fields(self):
        from apps.trafficdata.serializers import TrafficDataPublicSerializer
        return TrafficDataPublicSerializer.Meta.fields

    def list_to_string(self):
        # create string in the format of {{field_name}}
        # nbps
        return '{{' + '}} {{'.join(self.lead_fields()) + '}}'

    def render(self, name, value, attrs=None, renderer=None):
        s = super(AdminTextInputWidget, self).render(name, value, attrs)
        # click to copy
        button = f'<div class="foo">{s}</div><br><span>{self.list_to_string()}</span>'
        return mark_safe(button)


class PostbackTabularInlineForm(forms.ModelForm):

    class Meta:
        model = Postback
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(PostbackTabularInlineForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = AdminFooWidget()


class PostbackTabularInline(NestedTabularInline):
    model = Postback
    form = PostbackTabularInlineForm
    extra = 0
    fields = ('goal', 'method', 'content', 'active')
    readonly_fields = ('created_at', 'updated_at')


class IPWhitelistTabularInline(NestedStackedInline):
    model = IPWhitelist
    extra = 0
    fields = ('ip_address',)


class APITokenTabularInline(NestedStackedInline):
    model = APIToken
    extra = 0
    inlines = [IPWhitelistTabularInline, ]
    readonly_fields = ('token',)


class PixelTabularInline(NestedTabularInline):
    model = Pixel
    extra = 0
    fields = ('goal', 'type', 'content', 'active')
    readonly_fields = ('created_at', 'updated_at')

    

class EventNotificationTabularInline(NestedStackedInline):
    model = EventNotification
    extra = 0


class TelegramProfileInline(NestedStackedInline):
    model = TelegramProfile
    extra = 0
    inlines = [EventNotificationTabularInline, ]


class AffiliateAdminForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput, required=False,)

    class Meta:
        model = Affiliate
        fields = '__all__'
        exclude = ('user',)  # Exclude user field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def clean_password2(self):
        # Check that the two password entries match, password can be blank
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and (password1 != password2):
            raise forms.ValidationError(
                "Password fields didn't match.", code='password_mismatch')
        return password2

    def save(self, commit=True):
        affiliate = super().save(commit=False)
        password = self.cleaned_data['password1']
        if not affiliate.user_id:
            user = User.objects.create(email=self.cleaned_data['email'],
                                       first_name=self.cleaned_data['first_name'],
                                       last_name=self.cleaned_data['last_name'])
            if password:
                user.password = make_password(password)
            user.save()
            affiliate.user = user
        else:
            user = affiliate.user
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            if password:
                user.password = make_password(password)
            user.save()
        affiliate.save()
        return affiliate


@admin.register(Affiliate)
class AffiliateAdmin(NestedModelAdmin):
    form = AffiliateAdminForm
    filter_horizontal = ()
    list_filter = ()
    inlines = [APITokenTabularInline,
               PixelTabularInline, PostbackTabularInline, TelegramProfileInline]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Affiliate.objects.all()
        return Affiliate.objects.filter(id=request.user.id)

    list_display = ('id', 'company_name', 'is_active', 'first_name',
                    'last_name', 'email', 'country', 'telegram', 'skype')

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Affiliates'}
        return super(AffiliateAdmin, self).changelist_view(request, extra_context=extra_context)


class PostbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'goal', 'affiliate', 'method', 'active')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Postbacks'}
        return super(PostbackAdmin, self).changelist_view(request, extra_context=extra_context)


class APITokenAdmin(NestedModelAdmin):
    list_display = ('id', 'affiliate', 'token')
    readonly_fields = ('token', )

    def get_queryset(self, request):
        if request.user.is_superuser:
            return APIToken.objects.all()
        return APIToken.objects.filter(affiliate=request.user.affiliate)

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'API Tokens'}
        return super(APITokenAdmin, self).changelist_view(request, extra_context=extra_context)

    inlines = [IPWhitelistTabularInline, ]


class AffiliateRequestLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'get_affiliate', 'request_method', 'request_url',
                    'request_referrer', 'short_request_input', 'short_token', 'created_at')
    readonly_fields = ('id', 'get_affiliate', 'request_method', 'request_url', 'request_headers',
                       'request_referrer', 'lead', 'request_input', 'response', 'get_code', 'token', 'created_at')

    exclude = ('code', )
    # filter
    list_filter = ('token__affiliate', 'request_method', )

    def get_code(self, obj):
        if obj.code >= 200 and obj.code <= 299:
            return format_html('<span style="color: green;">{}</span>', obj.code)
        elif obj.code >= 500 and obj.code <= 599:
            return format_html('<span style="color: red;">{}</span>', obj.code)
        else:
            return format_html('<span style="color: yellow;">{}</span>', obj.code)

    get_code.short_description = 'code'

    def get_affiliate(self, obj):
        return obj.affiliate

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Affiliate Request Logs'}
        return super(AffiliateRequestLogAdmin, self).changelist_view(request, extra_context=extra_context)

    def short_request_input(self, obj):
        return Truncator(obj.request_input).chars(20)

    short_request_input.short_description = 'request input'

    def short_token(self, obj):
        return Truncator(obj.token).chars(25)

    short_token.short_description = 'token'


@admin.register(Postback, site=affiliate_site)
class AffiliatePostbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'goal', 'method', 'content', 'active')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['affiliate'].initial = request.user.affiliate
        # hidden
        form.base_fields['affiliate'].widget = forms.HiddenInput()
        return form

    def save_model(self, request, obj, form, change):
        obj.affiliate = request.user.affiliate
        super().save_model(request, obj, form, change)

    # list_filter = ('status', 'created_at', 'updated_at')
    # search_fields = ('email', 'phone')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Affiliate Postbacks'}
        return super(AffiliatePostbackAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        return Postback.objects.filter(affiliate=request.user.affiliate)


@admin.register(Pixel, site=affiliate_site)
class AffiliatePixelAdmin(admin.ModelAdmin):
    list_display = ('id', 'goal', 'type', 'content', 'active')
    # list_filter = ('status', 'created_at', 'updated_at')
    # search_fields = ('email', 'phone')
    search_fields = ('goal', 'type', 'content', 'active')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['affiliate'].initial = request.user.affiliate
        # hidden
        form.base_fields['affiliate'].widget = forms.HiddenInput()
        return form

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Affiliate Pixels'}
        return super(AffiliatePixelAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        return Pixel.objects.filter(affiliate=request.user.affiliate)


# NetworkAdminSite.register(Affiliate, AffiliateAdmin)

admin.site.register(APIToken, APITokenAdmin)
admin.site.register(Postback, PostbackAdmin)
admin.site.register(Pixel)
admin.site.register(AffiliateRequestLog, AffiliateRequestLogAdmin)


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = ('id', 'protocol', 'host', 'port',
                    'username', 'password', 'user_agent')
    # list_filter = ('status', 'created_at', 'updated_at')
    # search_fields = ('email', 'phone')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Proxies'}
        return super(ProxyAdmin, self).changelist_view(request, extra_context=extra_context)


@admin.register(FacebookPixel)
class FacebookPixelAdmin(NestedModelAdmin):
    # list_display = ('id', 'pixel_id', 'active', 'created_at', 'updated_at')
    # inlines = [ProxyTabularInline, ]

    list_display = ('id', 'name', 'pixel_id', 'active',
                    'created_at', 'updated_at')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Facebook Pixels'}
        return super(FacebookPixelAdmin, self).changelist_view(request, extra_context=extra_context)
