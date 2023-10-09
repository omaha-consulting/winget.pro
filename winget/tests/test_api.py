from base64 import b64encode
from django.core.files import File
from django.urls import reverse
from rest_framework.test import APIClient
from winget.models import Package, Version, Installer
from winget.tests.util import TestCaseThatUploadsFiles, \
	MultiUploadInMemoryFile, create_tenant, get_file_contents

import json


class APITest(TestCaseThatUploadsFiles):
	def setUp(self):
		super().setUp()
		self.client = APIClient()
		self.credentials = ('user', 'pw')
		self.tenant = create_tenant(*self.credentials)
		self.other_credentials = ('user2', 'pw2')
		create_tenant(*self.other_credentials)
	def test_create_package(self):
		response = self._check_unauthorized_and_request(
			'post', 'package-list', _PACKAGE_PAYLOAD
		)
		self.assertEqual(201, response.status_code)
		package = Package.objects.get(id=response.json()['id'])
		self._assert_dict_obj_equal(_PACKAGE_PAYLOAD, package)
		self.assertEqual(self.tenant, package.tenant)
		return package
	def test_create_version(self, use_correct_credentials=True):
		package = self.test_create_package()
		payload = dict(_VERSION_PAYLOAD)
		payload['package'] = package.id
		response = self._check_unauthorized_and_request(
			'post', 'version-list', payload, use_correct_credentials
		)
		expected_status = 201 if use_correct_credentials else 400
		self.assertEqual(expected_status, response.status_code)
		if use_correct_credentials:
			version = Version.objects.get(id=response.json()['id'])
			self._assert_dict_obj_equal(payload, version)
			return version
	def test_create_installer(self, use_correct_credentials=True):
		version = self.test_create_version()
		payload = dict(_INSTALLER_PAYLOAD)
		payload['version'] = version.id
		response = self._check_unauthorized_and_request(
			'post', 'installer-list', payload, use_correct_credentials
		)
		expected_status = 201 if use_correct_credentials else 400
		self.assertEqual(expected_status, response.status_code)
		if use_correct_credentials:
			installer = Installer.objects.get(id=response.json()['id'])
			self._assert_dict_obj_equal(payload, installer)
			self.assertTrue(installer.sha256.startswith('6b86b273'))
			return installer
	def test_create_nested_installer(self):
		version = self.test_create_version()
		payload = dict(_INSTALLER_PAYLOAD)
		payload['version'] = version.id
		def send_payload(modifications=None):
			modified_payload = dict(payload)
			modified_payload.update(modifications or {})
			return self._check_unauthorized_and_request(
				'post', 'installer-list', modified_payload
			)
		def check_errors(payload_modifications, expected_errors):
			response = send_payload(payload_modifications)
			self.assertEqual(400, response.status_code)
			self.assertEqual(expected_errors, response.json())
		check_errors({'nested_installer': 'test.exe'}, {
			'nested_installer': [
				'Nested installer can only be set when type is "zip".'
			]
		})
		check_errors({'nested_installer_type': 'inno'}, {
			'nested_installer_type': [
				'Nested installer type can only be set when type is "zip".'
			]
		})
		payload['type'] = 'zip'
		check_errors({}, {
			'nested_installer': [
				'Nested installer is required when type is "zip".'
			],
			'nested_installer_type': [
				'Nested installer type is required when type is "zip".'
			]
		})
		check_errors({'nested_installer': 'nested.exe'}, {
			'nested_installer_type': [
				'Nested installer type is required when type is "zip".'
			]
		})
		check_errors({'nested_installer_type': 'exe'}, {
			'nested_installer': [
				'Nested installer is required when type is "zip".'
			]
		})
		payload['nested_installer'] = 'nested.msi'
		check_errors({'nested_installer_type': 'WRONG'}, {
			'nested_installer_type': ['"WRONG" is not a valid choice.']
		})
		payload['nested_installer_type'] = 'msi'
		response = send_payload()
		self.assertEqual(201, response.status_code)
		installer = Installer.objects.get(id=response.json()['id'])
		self._assert_dict_obj_equal(payload, installer)
		self.assertTrue(installer.sha256.startswith('6b86b273'))
	def test_edit_package(self, use_correct_credentials=True):
		package = self.test_create_package()
		payload = dict(_PACKAGE_PAYLOAD)
		payload['name'] = 'new name'
		response = self._check_unauthorized_and_request(
			'put', 'package-detail', payload, use_correct_credentials,
			{'pk': package.id}
		)
		expected_status = 200 if use_correct_credentials else 404
		self.assertEqual(
			expected_status, response.status_code, response.content
		)
		if use_correct_credentials:
			package.refresh_from_db()
			self._assert_dict_obj_equal(payload, package)
	def test_cannot_edit_other_tenants_packages(self):
		self.test_edit_package(use_correct_credentials=False)
	def test_edit_version(self, use_correct_credentials=True):
		version = self.test_create_version()
		payload = {
			'version': '0.0.2',
			'package': version.package.id
		}
		response = self._check_unauthorized_and_request(
			'put', 'version-detail', payload, use_correct_credentials,
			{'pk': version.id}
		)
		expected_status = 200 if use_correct_credentials else 404
		self.assertEqual(
			expected_status, response.status_code, response.content
		)
		if use_correct_credentials:
			version.refresh_from_db()
			self._assert_dict_obj_equal(payload, version)
	def test_cannot_edit_other_tenants_versions(self):
		self.test_edit_version(use_correct_credentials=False)
	def test_edit_installer(self, use_correct_credentials=True):
		installer = self.test_create_installer()
		payload = dict(_INSTALLER_PAYLOAD)
		payload['version'] = installer.version.id
		payload['file'] = MultiUploadInMemoryFile('file2.exe', b'2')
		response = self._check_unauthorized_and_request(
			'put', 'installer-detail', payload, use_correct_credentials,
			{'pk': installer.id}
		)
		expected_status = 200 if use_correct_credentials else 404
		self.assertEqual(
			expected_status, response.status_code, response.content
		)
		if use_correct_credentials:
			installer.refresh_from_db()
			self._assert_dict_obj_equal(payload, installer)
			self.assertTrue(
				installer.sha256.startswith('d4735e3a'), installer.sha256
			)
	def test_cannot_edit_other_tenants_installers(self):
		self.test_edit_installer(use_correct_credentials=False)
	def test_cannot_create_version_for_other_tenants_package(self):
		self.test_create_version(use_correct_credentials=False)
	def test_cannot_create_installer_for_other_tenants_version(self):
		self.test_create_installer(use_correct_credentials=False)
	def _check_unauthorized_and_request(
		self, method, view_name, data, use_correct_credentials=True,
		view_kwargs=None
	):
		self._check_unauthorized(method, view_name, data, view_kwargs)
		credentials = self.credentials if use_correct_credentials \
			else self.other_credentials
		return self._request(
			method, view_name, data, credentials, view_kwargs
		)
	def _check_unauthorized(self, method, view_name, data, view_kwargs=None):
		for credentials in (
			None, ('wrong', 'wrong'), (self.credentials[0], 'wrong'),
			('wrong', self.credentials[1])
		):
			response = \
				self._request(method, view_name, data, credentials, view_kwargs)
			self.assertEqual(403, response.status_code)
	def _request(
		self, method, view_name, data, credentials=None, view_kwargs=None
	):
		args, kwargs = self._get_request_args_kwargs(
			view_name, data, credentials, view_kwargs
		)
		return getattr(self.client, method)(*args, **kwargs)
	def _get_request_args_kwargs(
		self, view_name, data, credentials=None, view_kwargs=None
	):
		kwargs = {}
		if credentials:
			kwargs['HTTP_AUTHORIZATION'] = \
				'Basic ' + b64encode(':'.join(credentials).encode()).decode()
		if any(isinstance(v, File) for v in data.values()):
			kwargs['format'] = 'multipart'
		else:
			kwargs['content_type'] = 'application/json'
			data = json.dumps(data)
		url = reverse(f'winget:{view_name}', kwargs=view_kwargs)
		return (url, data), kwargs
	def _assert_dict_obj_equal(self, d, o):
		for key, expected in d.items():
			actual = getattr(o, key)
			if isinstance(expected, File):
				expected = get_file_contents(expected)
				actual = get_file_contents(actual)
			try:
				actual = actual.pk
			except AttributeError:
				pass
			self.assertEqual(expected, actual)

_PACKAGE_PAYLOAD = {
	'identifier': 'XP9KHM4BK9FZ7Q',
	'name': 'Visual Studio Code',
	'publisher': 'Microsoft',
	'description': 'Free code editor.'
}

_VERSION_PAYLOAD = {
	'version': '0.0.1'
}

_INSTALLER_PAYLOAD = {
	'architecture': 'x64',
	'type': 'exe',
	'scope': 'user',
	'file': MultiUploadInMemoryFile('file.exe', b'1')
}