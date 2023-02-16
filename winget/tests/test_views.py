from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from tenants.models import Tenant
from winget.models import Package, Version, Installer


class APITest(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.tenant = Tenant.objects.create(
            user=User.objects.create_user('user@gmail.com')
        )

    def test_information_required_parts(self):
        data = self._get('information')['Data']
        self.assertEqual('api.winget.pro', data['SourceIdentifier'])
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

        # Test that the package isn't returned when it has no version. The
        # motivation for this is that `winget search` gives an error when the
        # REST source returns a package with 'Versions' empty or nonexistent.
        version.delete()
        data = self._post('manifestSearch', request)['Data']
        self.assertEqual([], data)

    def test_list_source(self):
        # Simulate `winget list` without any extra parameters.

        # Create some apps to test that we do not return superfluous results:
        self._create_vscode()
        self._create_powertoys()

        data = self._post('manifestSearch', {
            'Inclusions': [
                {
                    'PackageMatchField': 'ProductCode',
                    'RequestMatch': {
                        'KeyWord': 'microsoft edge',
                        'MatchType': 'Exact'
                    }
                },
                {
                    'PackageMatchField': 'NormalizedPackageNameAndPublisher',
                    'RequestMatch': {
                        'KeyWord': 'microsoftedge',
                        'MatchType': 'Exact'
                    }
                }
            ]
        })['Data']
        self.assertEqual([], data)

        data = self._post('manifestSearch', {
            'Inclusions': [
                {
                    'PackageMatchField': 'PackageFamilyName',
                    'RequestMatch': {
                        'KeyWord':
                            'microsoft.microsoftedge.stable_8wekyb3d8bbwe',
                        'MatchType': 'Exact'
                    }
                }
            ]
        })['Data']
        self.assertEqual([], data)

    def _create_vscode(self, scope='machine'):
        package = Package.objects.create(
            tenant=self.tenant, identifier='XP9KHM4BK9FZ7Q',
            name='Visual Studio Code',
            description='Free, lightweight, extensible code editor.',
            publisher='Microsoft Corporation'
        )
        version = Version.objects.create(version='Unknown', package=package)
        installer = Installer.objects.create(
            version=version, architecture='x64', type='exe', scope=scope,
            file=SimpleUploadedFile('vscode-winsta11er-x64.exe', b'1'),
            sha256='6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb78'
                   '75b4b'
        )
        return package, version, installer

    def _create_powertoys(self):
        package = Package.objects.create(
            tenant=self.tenant, identifier='XP89DCGQ3K6VLD',
            name='Microsoft PowerToys',
            description='A set of utilities for power users.',
            publisher='Microsoft Corporation'
        )
        version = Version.objects.create(version='Unknown', package=package)
        installer = Installer.objects.create(
            version=version, architecture='x64', type='exe',
            file=SimpleUploadedFile('PowerToysSetup-0.51.1-x64.exe', b'2'),
            sha256='d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec1'
                   '3ab35'
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
        installer_json, = version_json['Installers']
        self._check_vscode_installer_json(installer, installer_json)

    def _check_vscode_installer_json(
        self, installer, installer_json, scope=None
    ):
        if scope is None:
            scope = installer.scope
        self.assertEqual(installer.architecture, installer_json['Architecture'])
        self.assertEqual(installer.type, installer_json['InstallerType'])
        self.assertEqual(
            f'http://testserver{installer.file.url}',
            installer_json['InstallerUrl']
        )
        self.assertEqual(installer.sha256, installer_json['InstallerSha256'])
        self.assertEqual(scope, installer_json['Scope'])

    def test_scope_both(self):
        package, version, installer = self._create_vscode(scope='both')
        resp = self._get('packageManifests', identifier=package.identifier)
        version_json, = resp['Data']['Versions']
        installers_json = version_json['Installers']
        self.assertEqual(2, len(installers_json))  # One for each scope
        machine, user = sorted(installers_json, key=lambda i: i['Scope'])
        self._check_vscode_installer_json(installer, machine, 'machine')
        self._check_vscode_installer_json(installer, user, 'user')

    def _get(self, url_name, expect_status=200, **kwargs):
        response = self.client.get(self._reverse(url_name, kwargs))
        self.assertEqual(expect_status, response.status_code)
        return response.json()

    def _post(self, url_name, data, expect_status=200):
        path = self._reverse(url_name)
        response = self.client.post(path, data, content_type='application/json')
        self.assertEqual(expect_status, response.status_code)
        return response.json()

    def _reverse(self, url_name, kwargs=None):
        new_kwargs = dict(kwargs or {})
        new_kwargs['tenant_uuid'] = str(self.tenant.uuid)
        return reverse(f'winget:{url_name}', kwargs=new_kwargs)