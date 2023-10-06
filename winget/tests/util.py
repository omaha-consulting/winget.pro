from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from tempfile import TemporaryDirectory

from tenants.models import Tenant

"""
When a test case uploads files, they by default get placed into media/. This
folder (out of the box) is not cleaned up after the test case is run.
TestCaseThatUploadsFiles fixes this. It makes sure that files are uploaded into
a temporary directory. This directory is cleaned up at the end of each test.
"""
class TestCaseThatUploadsFiles(TestCase):
	def setUp(self):
		super().setUp()
		self.media_root = TemporaryDirectory()
		media_root_path = self.media_root.name
		self.settings_override = override_settings(MEDIA_ROOT=media_root_path)
		self.settings_override.enable()
	def tearDown(self):
		super().tearDown()
		self.settings_override.disable()
		self.media_root.cleanup()

class MultiUploadInMemoryFile(SimpleUploadedFile):
	"""
	Transmitting a SimpleUploadedFile multiple times makes subsequent
	invocations send 0 bytes. This is inconvenient in tests, where we may want
	to use the same test object multiple times. This class fixes that.
	"""
	def read(self):
		self.seek(0)
		return super().read()

def create_tenant(username='user@gmail.com', password=None):
	user = User.objects.create_user(username, password=password)
	tenant = Tenant.objects.create()
	tenant.users.add(user)
	return tenant

def get_file_contents(f):
	if f.closed:
		f.open()
		try:
			return f.read()
		finally:
			# Make sure we're not accidentally leaving the file open. This is
			# especially important on Windows, where open files cannot be
			# deleted. If we leave them opened, then the test case teardown
			# logic fails with nasty errors when it tries to delete the test's
			# temporary files.
			f.close()
	else:
		position_before = f.tell()
		f.seek(0)
		result = f.read()
		f.seek(position_before)
		return result