from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from tempfile import TemporaryDirectory

"""
When a test case uploads files, they by default get placed into media/. This
folder (out of the box) is not cleaned up after the test case is run.
TestCaseThatUploadsFiles fixes this. It makes sure that files are uploaded into
a temporary directory. This directory is cleaned up when the Python interpreter
exits. This is achieved by keeping a global reference to the TemporaryDirectory
instance. Once this instance goes out of scope, Python guarantees that the
temporary directory (and its contents) are removed.
"""
_MEDIA_ROOT = TemporaryDirectory()
@override_settings(MEDIA_ROOT=_MEDIA_ROOT.name)
class TestCaseThatUploadsFiles(TestCase):
	pass

class MultiUploadInMemoryFile(SimpleUploadedFile):
	"""
	Transmitting a SimpleUploadedFile multiple times makes subsequent
	invocations send 0 bytes. This is inconvenient in tests, where we may want
	to use the same test object multiple times. This class fixes that.
	"""
	def read(self):
		self.seek(0)
		return super().read()