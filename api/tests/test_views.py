from django.test import TestCase, Client
from django.urls import reverse

class APITest(TestCase):
    def setUp(self):
    	super().setUp()
    	self.client = Client()
    def test_information_required_parts(self):
    	response = self.client.get(reverse('api:information'))
    	data = response.json()['Data']
    	self.assertEqual(
    		'github.com/omaha-consulting/winget-private-repository',
    		data['SourceIdentifier']
    	)
    	self.assertEqual(data['ServerSupportedVersions'], ['1.1.0'])