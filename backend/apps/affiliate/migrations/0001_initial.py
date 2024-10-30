# Generated by Django 4.2.3 on 2023-07-25 19:04

import apps.utils.models
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=30)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('telegram', models.CharField(max_length=30)),
                ('skype', models.CharField(max_length=30)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Affiliate',
                'verbose_name_plural': 'Affiliates',
            },
        ),
        migrations.CreateModel(
            name='AffiliateRequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_method', models.CharField(max_length=50)),
                ('request_url', models.CharField(max_length=255)),
                ('request_referrer', models.CharField(blank=True, max_length=255, null=True)),
                ('request_input', models.TextField()),
                ('response', models.TextField()),
                ('code', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Affiliate Request Log',
                'verbose_name_plural': 'Affiliate Request Logs',
            },
        ),
        migrations.CreateModel(
            name='APIToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Enabled')),
                ('can_see_real_status', models.BooleanField(default=False, help_text='Whether this affiliate can see real status of leads', verbose_name='Can see real status')),
                ('can_see_lead_info', models.BooleanField(default=False, help_text='Whether this affiliate can see lead info', verbose_name='Can see lead info')),
                ('token', models.CharField(help_text='Token to be used in API requests', max_length=255, unique=True, verbose_name='Token')),
                ('duplication_strategy', models.CharField(choices=[('disable', 'Disable'), ('global_week_window', 'Global Week Window'), ('current_token_week_window', 'Current Token Week Window')], default='disable', help_text='Duplication strategy to be used in API requests', max_length=255, verbose_name='Duplication Strategy')),
                ('duplication_field', models.CharField(choices=[('disable', 'Disable'), ('email', 'Email'), ('phone_number', 'Phone Number'), ('ip_address', 'Ip Address')], default='email', help_text='Duplication field to be used in API requests', max_length=255, verbose_name='Duplication Field')),
                ('phone_validation', models.BooleanField(default=False, help_text='Whether this affiliate needs to validate phone number', verbose_name='Phone validation')),
                ('email_validation', models.BooleanField(default=False, help_text='Whether this affiliate needs to validate email', verbose_name='Email validation')),
                ('affiliate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_tokens', to='affiliate.affiliate')),
            ],
            options={
                'verbose_name': 'API Token',
                'verbose_name_plural': 'API Tokens',
            },
        ),
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol', models.CharField(choices=[('http', 'Http'), ('https', 'Https'), ('socks5', 'Socks5')], default='http', max_length=6)),
                ('host', models.CharField(max_length=255)),
                ('port', models.IntegerField()),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Proxy',
                'verbose_name_plural': 'Proxies',
            },
        ),
        migrations.CreateModel(
            name='TelegramProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(blank=True, max_length=50, null=True)),
                ('affiliate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='telegram_profile', to='affiliate.affiliate')),
            ],
        ),
        migrations.CreateModel(
            name='Postback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST')], default='GET', max_length=4)),
                ('content', models.CharField(max_length=255)),
                ('goal', models.CharField(choices=[('click', 'Click'), ('click_landed', 'Click Landed'), ('lead', 'Lead'), ('lead_queued', 'Lead Queued'), ('lead_pushed', 'Lead Pushed'), ('lead_declined', 'Lead Declined'), ('sale', 'Sale')], default='lead_pushed', max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('affiliate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postbacks', to='affiliate.affiliate')),
            ],
            options={
                'verbose_name': 'Postback',
                'verbose_name_plural': 'Postbacks',
            },
            bases=(apps.utils.models.LogModel, models.Model),
        ),
        migrations.CreateModel(
            name='Pixel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('goal', models.CharField(choices=[('click', 'Click'), ('click_landed', 'Click Landed'), ('lead', 'Lead'), ('lead_queued', 'Lead Queued'), ('lead_pushed', 'Lead Pushed'), ('lead_declined', 'Lead Declined'), ('sale', 'Sale')], default='lead_pushed', max_length=20)),
                ('type', models.CharField(choices=[('body_html_insert', 'Body Html Insert'), ('script_evaluate', 'Script Evaluate'), ('inline_iframe_url', 'Inline Iframe Url'), ('inline_script_url', 'Inline Script Url'), ('inline_script_img', 'Inline Script Img')], default='body_html_insert', max_length=30, verbose_name='Pixel Type')),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('affiliate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pixels', to='affiliate.affiliate')),
            ],
            options={
                'verbose_name': 'Pixel',
                'verbose_name_plural': 'Pixels',
            },
            bases=(apps.utils.models.LogModel, models.Model),
        ),
        migrations.CreateModel(
            name='IPWhitelist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=30, verbose_name='IP Address')),
                ('api_token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ip_whitelist', to='affiliate.apitoken')),
            ],
            options={
                'verbose_name': 'IP',
                'verbose_name_plural': 'IP Addresses',
            },
        ),
        migrations.CreateModel(
            name='FacebookPixel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('pixel_id', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('goal', models.CharField(choices=[('click', 'Click'), ('click_landed', 'Click Landed'), ('lead', 'Lead'), ('lead_queued', 'Lead Queued'), ('lead_pushed', 'Lead Pushed'), ('lead_declined', 'Lead Declined'), ('sale', 'Sale')], default='lead', max_length=255)),
                ('event_name', models.CharField(choices=[('AddPaymentInfo', 'Add Payment Info'), ('AddToCart', 'Add To Cart'), ('AddToWishlist', 'Add To Wishlist'), ('CompleteRegistration', 'Complete Registration'), ('Contact', 'Contact'), ('CustomizeProduct', 'Customize Product'), ('Donate', 'Donate'), ('FindLocation', 'Find Location'), ('InitiateCheckout', 'Initiate Checkout'), ('Lead', 'Lead'), ('PageView', 'Page View'), ('Purchase', 'Purchase'), ('Schedule', 'Schedule'), ('Search', 'Search'), ('StartTrial', 'Start Trial'), ('SubmitApplication', 'Submit Application'), ('Subscribe', 'Subscribe'), ('ViewContent', 'View Content')], default='AddPaymentInfo', max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('affiliate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='facebook_pixels', to='affiliate.affiliate')),
                ('proxy', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='facebook_pixel', to='affiliate.proxy')),
            ],
            options={
                'verbose_name': 'Facebook Pixel',
                'verbose_name_plural': 'Facebook Pixels',
            },
        ),
        migrations.CreateModel(
            name='EventNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('click', 'Click'), ('click_landed', 'Click Landed'), ('lead', 'Lead'), ('lead_queued', 'Lead Queued'), ('lead_pushed', 'Lead Pushed'), ('lead_declined', 'Lead Declined'), ('sale', 'Sale')], default='lead_pushed', max_length=20)),
                ('message', models.TextField()),
                ('topic', models.CharField(max_length=255)),
                ('telegram_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_notifications', to='affiliate.telegramprofile')),
            ],
        ),
    ]