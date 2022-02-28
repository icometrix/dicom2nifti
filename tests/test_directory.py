# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import os
import shutil
import tempfile
import unittest

from dicom2nifti.convert_dir import convert_directory, _remove_accents

from .test_data import *


class TestConversionDirectory(unittest.TestCase):

    def test_convert_directory(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            convert_directory(GENERIC_ANATOMICAL, tmp_output_dir)
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, '4_dicom2nifti.nii.gz')))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_remove_accents(self):
        self.assertEqual(_remove_accents(u'êén_ölîfānt@'), 'een_olifant')
        self.assertEqual(_remove_accents(')(*&^%$#@!][{}\\"|,./?><'), '')


if __name__ == '__main__':
    unittest.main()
