from django.test import TestCase, Client
from django.urls import reverse

from api.models import Package, Version, Installer


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
        # Simulate `winget search` without any extra parameters.
        data = self._post('manifestSearch', {'FetchAllManifests': True})['Data']
        self.assertEqual([], data)

    def test_search(self, request=None):
        if request is None:
            # Simulate `winget search 'visual studio code'`.
            request = {
                'Query': {
                    'KeyWord': 'visual studio code',
                    'MatchType': 'Substring'
                }
            }
        data = self._post('manifestSearch', request)['Data']
        self.assertEqual([], data)

        package, version = self._create_vscode()[:2]
        # Create another package that should not be returned:
        self._create_powertoys()
        data = self._post('manifestSearch', request)['Data']
        self.assertEqual(1, len(data))
        result, = data
        self.assertEqual(package.identifier, result['PackageIdentifier'])
        self.assertEqual(package.name, result['PackageName'])
        self.assertEqual(package.publisher, result['Publisher'])
        self.assertEqual(
            [{'PackageVersion': version.version}], result['Versions']
        )

    def _create_vscode(self):
        package = Package.objects.create(
            identifier='XP9KHM4BK9FZ7Q',
            name='Visual Studio Code',
            description='Free, lightweight, extensible code editor.',
            publisher='Microsoft Corporation'
        )
        version = Version.objects.create(version='Unknown', package=package)
        installer = Installer.objects.create(
            version=version, architecture='x64', type='exe',
            url='https://github.com/microsoft/vscode-winsta11er/releases/'
                'download/v0.0.5/vscode-winsta11er-x64.exe',
            sha256='9490453f2d73eb32f365c631bbad3b9d4837af27ce31ad6cb3dad56c50b'
                   '0a5fa'
        )
        return package, version, installer

    def _create_powertoys(self):
        package = Package.objects.create(
            identifier='XP89DCGQ3K6VLD', name='Microsoft PowerToys',
            description='A set of utilities for power users.',
            publisher='Microsoft Corporation'
        )
        version = Version.objects.create(version='Unknown', package=package)
        installer = Installer.objects.create(
            version=version, architecture='x64', type='exe',
            url='https://github.com/microsoft/PowerToys/releases/'
                'download/v0.51.1/PowerToysSetup-0.51.1-x64.exe',
            sha256='cdd2c65a30017da05a0bf5a8b144db8e523e17225fd180ffc3bd4c8b81f'
                   '72994'
        )
        return package, version, installer

    def test_search_during_install(self):
        # Simulate the search part of `winget install "visual studio code"`.
        request = {
            'Inclusions': [
                {
                    'PackageMatchField': 'PackageFamilyName',
                    'RequestMatch': {
                        'KeyWord': 'visual studio code',
                        'MatchType': 'Exact'
                    }
                },
                {
                    'PackageMatchField': 'ProductCode',
                    'RequestMatch': {
                        'KeyWord': 'visual studio code',
                        'MatchType': 'Exact'
                    }
                },
                {
                    'PackageMatchField': 'PackageIdentifier',
                    'RequestMatch': {
                        'KeyWord': 'visual studio code',
                        'MatchType': 'CaseInsensitive'
                    }
                },
                {
                    'PackageMatchField': 'PackageName',
                    'RequestMatch': {
                        'KeyWord': 'visual studio code',
                        'MatchType': 'CaseInsensitive'
                    }
                },
                {
                    'PackageMatchField': 'Moniker',
                    'RequestMatch': {
                        'KeyWord': 'visual studio code',
                        'MatchType': 'CaseInsensitive'
                    }
                }
            ]
        }
        self.test_search(request)

    def test_manifests_during_install(self):
        # Simulate /packageManifests/<Identifier> during `winget install ...`.
        package, version, installer = self._create_vscode()
        resp = self._get('packageManifests', identifier=package.identifier)
        result = resp['Data']
        self.assertEqual(package.identifier, result['PackageIdentifier'])
        self.assertEqual(1, len(result['Versions']))
        version_json, = result['Versions']
        self.assertEqual(version.version, version_json['PackageVersion'])
        locale = version_json['DefaultLocale']
        self.assertIn('PackageLocale', locale)
        self.assertEqual(package.publisher, locale['Publisher'])
        self.assertEqual(package.name, locale['PackageName'])
        self.assertEqual(package.description, locale['ShortDescription'])
        self.assertEqual(1, len(version_json['Installers']))
        installer_json, = version_json['Installers']
        self.assertEqual(installer.architecture, installer_json['Architecture'])
        self.assertEqual(installer.type, installer_json['InstallerType'])
        self.assertEqual(installer.url, installer_json['InstallerUrl'])
        self.assertEqual(installer.sha256, installer_json['InstallerSha256'])

    def _get(self, url_name, expect_status=200, **kwargs):
        response = self.client.get(reverse(f'api:{url_name}', kwargs=kwargs))
        self.assertEqual(expect_status, response.status_code)
        return response.json()

    def _post(self, url_name, data, expect_status=200):
        path = reverse(f'api:{url_name}')
        response = self.client.post(path, data, content_type='application/json')
        self.assertEqual(expect_status, response.status_code)
        return response.json()
