from django.test import TestCase, Client
from django.urls import reverse


class APITest(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_information_required_parts(self):
        response = self._get('information')
        self.assertEqual(200, response.status_code)
        data = response.json()['Data']
        self.assertEqual(
            'github.com/omaha-consulting/winget-private-repository',
            data['SourceIdentifier']
        )
        self.assertEqual(data['ServerSupportedVersions'], ['1.1.0'])

    def test_search_all_empty(self):
        response = self._post_json(
            'manifestSearch', {'FetchAllManifests': True}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual({'Data': []}, response.json())

    def _get(self, url_name):
        return self.client.get(reverse(f'api:{url_name}'))

    def _post_json(self, url_name, data):
        return self._post(url_name, data, content_type='application/json')

    def _post(self, url_name, *args, **kwargs):
        return self.client.post(reverse(f'api:{url_name}'), *args, **kwargs)
