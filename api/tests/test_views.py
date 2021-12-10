from django.test import TestCase, Client
from django.urls import reverse


class APITest(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_information_required_parts(self):
        data = self._get('information')['Data']
        self.assertEqual(
            'github.com/omaha-consulting/winget-private-repository',
            data['SourceIdentifier']
        )
        self.assertEqual(['1.1.0'], data['ServerSupportedVersions'])

    def test_search_all_empty(self):
        data = self._post('manifestSearch', {'FetchAllManifests': True})['Data']
        self.assertEqual([], data)

    def _get(self, url_name, expect_status=200):
        response = self.client.get(reverse(f'api:{url_name}'))
        self.assertEqual(expect_status, response.status_code)
        return response.json()

    def _post(self, url_name, data, expect_status=200):
        path = reverse(f'api:{url_name}')
        response = self.client.post(path, data, content_type='application/json')
        self.assertEqual(expect_status, response.status_code)
        return response.json()
