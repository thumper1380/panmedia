from django.test import TestCase
from django.contrib.auth import get_user_model
from django_countries import countries

from .models import Affiliate, Postback
from apps.trafficdata.models import TrafficData

class AffiliateTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com', password='password')
        self.affiliate = Affiliate.objects.create(
            user=self.user,
            company_name='Test Company',
            country=countries.first()[0],
            telegram='test_telegram',
            skype='test_skype',
            status=True,
        )

    def test_username(self):
        self.assertEqual(self.affiliate.username, 'test@example.com')

    def test_first_name(self):
        self.assertEqual(self.affiliate.first_name, self.user.first_name)

    def test_last_name(self):
        self.assertEqual(self.affiliate.last_name, self.user.last_name)

    def test_email(self):
        self.assertEqual(self.affiliate.email, self.user.email)

    def test_is_active(self):
        self.assertEqual(self.affiliate.is_active, self.user.is_active)

    def test_str(self):
        self.assertEqual(str(self.affiliate), 'Test Company')

    def test_get_pixels(self):
        pixel = self.affiliate.pixels.create(
            name='Test Pixel', code='test_code', active=True)
        self.assertIn(pixel, self.affiliate.get_pixels())

    def test_fire_postback(self):
        lead = TrafficData.objects.last()
        postback = Postback.objects.create(
            goal='test_goal', url='http://example.com', active=True)
        Postback.objects.fire('test_goal', lead)
        self.assertIn(lead, postback.leads.all())

    def test_pending_postback(self):
        lead = TrafficData.objects.last()
        postback = Postback.objects.create(
            goal='test_goal', url='http://example.com', active=True)
        Postback.objects.pending('test_goal', lead)
        self.assertIn(lead, postback.pending_leads.all())
        