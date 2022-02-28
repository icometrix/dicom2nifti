# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import os
import shutil
import tempfile
import unittest

import nibabel

from dicom2nifti.common import get_vendor, Vendor
from dicom2nifti.convert_hitachi import hitachi_dicom_to_nifti
from dicom2nifti.common import read_dicom_directory

from .test_data import *
from .test_tools import assert_compare_nifti, ground_thruth_filenames


class TestConversionHitachi(unittest.TestCase):
    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = hitachi_dicom_to_nifti(read_dicom_directory(HITACHI_ANATOMICAL), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = hitachi_dicom_to_nifti(read_dicom_directory(HITACHI_ANATOMICAL),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(HITACHI_ANATOMICAL)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = hitachi_dicom_to_nifti(read_dicom_directory(HITACHI_ANATOMICAL_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(HITACHI_ANATOMICAL_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_is_hitachi(self):
        self.assertNotEqual(get_vendor(read_dicom_directory(SIEMENS_ANATOMICAL)), Vendor.HITACHI)
        self.assertNotEqual(get_vendor(read_dicom_directory(GE_ANATOMICAL)), Vendor.HITACHI)
        self.assertNotEqual(get_vendor(read_dicom_directory(PHILIPS_ANATOMICAL)), Vendor.HITACHI)
        self.assertNotEqual(get_vendor(read_dicom_directory(GENERIC_ANATOMICAL)), Vendor.HITACHI)
        self.assertEqual(get_vendor(read_dicom_directory(HITACHI_ANATOMICAL)), Vendor.HITACHI)


if __name__ == '__main__':
    unittest.main()
