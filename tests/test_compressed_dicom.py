# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import os
import shutil
import tempfile
import unittest

from dicom2nifti.compressed_dicom import read_file, _is_compressed

from .test_data import *


class TestCompressedDicom(unittest.TestCase):

    def test_is_compressed(self):
        self.assertTrue(_is_compressed(os.path.join(GENERIC_COMPRESSED, 'IM-0001-0001-0001.dcm')))
        self.assertFalse(_is_compressed(os.path.join(GENERIC_ANATOMICAL, 'IM-0001-0001-0001.dcm')))

    def test_read_file(self):
        temporary_directory = tempfile.mkdtemp()
        try:
            dicom_file = os.path.join(temporary_directory, 'IM-0001-0001-0001.dcm')
            input_file = os.path.join(GENERIC_COMPRESSED, 'IM-0001-0001-0001.dcm')
            shutil.copy(input_file, dicom_file)
            dicom_headers = read_file(dicom_file)
            pixel_data = dicom_headers.pixel_array
            self.assertIsNotNone(pixel_data)
        finally:
            shutil.rmtree(temporary_directory)


if __name__ == '__main__':
    unittest.main()
