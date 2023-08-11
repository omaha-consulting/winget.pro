from unittest import TestCase
from winget.util import randomize_filename

class RandomizeFilenameTest(TestCase):
    def test_randomize_filename(self):
        self.assertEqual(
            randomize_filename('installer.exe', seed=1631548913),
            'installer-v34EnYOkYJ.exe'
        )