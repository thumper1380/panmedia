from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.trafficdata.models import TrafficData
from apps.traffic_distribution.models import Advertiser, Provider
from apps.affiliate.models import Affiliate
from apps.offer.models import Offer


class TrafficDataAPITestCase(APITestCase):
    def setUp(self):
        # Similar to the model test case, create necessary instances for the foreign keys
        provider = Provider.objects.first()

        advertiser = Advertiser.objects.create(
            id=1,
            name='Advertiser1',
            default_currency='USD',
            active=True,
            is_test=False,
            created_at='2023-01-01 00:00:00',
            provider=provider
            # assuming the necessary provider object is created and passed here
        )

        affiliate = Affiliate.objects.create(
            user_ptr_id=1,
            company_name='Company1',
            country='US',
            telegram='telegram',
            skype='skype',
            status=True
        )

        offer = Offer.objects.create(
            id=1,
            name='Offer1',
            language='English',
            active=True,
            created_at='2023-01-01 00:00:00',
            updated_at='2023-01-02 00:00:00',
            # assuming the necessary landing page and settings form objects are created and passed here
        )

        TrafficData.objects.create(
            first_name='John',
            last_name='Doe',
            country='US',
            region='New York',
            city='New York',
            ip_address='192.168.1.1',
            bot=False,
            connection_type='Wifi',
            mobile_operator='Verizon',
            isp='Verizon',
            proxy=False,
            is_unique=True,
            retry_count=0,
            advertiser=advertiser,
            affiliate=affiliate,
            funnel=offer
            # add other necessary fields here
        )

    def test_list_trafficdata(self):
        url = reverse('trafficdata-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        first_trafficdata = response.data[0]

        self.assertEqual(first_trafficdata['first_name'], 'John')
        self.assertEqual(first_trafficdata['last_name'], 'Doe')
        self.assertEqual(first_trafficdata['city'], 'New York')
        # similarly, you can assert other fields in the response
