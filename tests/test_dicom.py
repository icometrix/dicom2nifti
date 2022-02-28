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


from dicom2nifti import settings
from dicom2nifti.convert_dicom import dicom_series_to_nifti
from dicom2nifti.common import read_dicom_directory, get_vendor, Vendor, is_valid_imaging_dicom

from .test_data import *
from .test_tools import assert_compare_nifti, ground_thruth_filenames


class TestConversionDicom(unittest.TestCase):
    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = dicom_series_to_nifti(SIEMENS_ANATOMICAL, None, False)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            for idx, reorient in enumerate([False, True]):
                results = dicom_series_to_nifti(SIEMENS_ANATOMICAL,
                                                os.path.join(tmp_output_dir, 'test.nii.gz'), reorient)
                assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_ANATOMICAL)[idx])
                self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

                results = dicom_series_to_nifti(SIEMENS_ANATOMICAL_IMPLICIT,
                                                os.path.join(tmp_output_dir, 'test.nii.gz'),  reorient)
                assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_ANATOMICAL_IMPLICIT)[idx])
                self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

                results = dicom_series_to_nifti(GENERIC_ANATOMICAL,
                                                os.path.join(tmp_output_dir, 'test.nii.gz'), reorient)
                assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(GENERIC_ANATOMICAL)[idx])
                self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

                results = dicom_series_to_nifti(GENERIC_ANATOMICAL_IMPLICIT,
                                                os.path.join(tmp_output_dir, 'test.nii.gz'), reorient)
                assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(GENERIC_ANATOMICAL_IMPLICIT)[idx])
                self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

                results = dicom_series_to_nifti(GENERIC_COMPRESSED,
                                                os.path.join(tmp_output_dir, 'test.nii.gz'), reorient)
                assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(GENERIC_COMPRESSED)[idx])
                self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

                results = dicom_series_to_nifti(GENERIC_NON_ISOTROPIC,
                                                os.path.join(tmp_output_dir, 'test.nii.gz'), reorient)
                assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(GENERIC_NON_ISOTROPIC)[idx])
                self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

                results = dicom_series_to_nifti(HITACHI_ANATOMICAL,
                                                os.path.join(tmp_output_dir, 'test.nii.gz'), reorient)
                assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(HITACHI_ANATOMICAL)[idx])
                self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_are_imaging_dicoms(self):
        self.assertTrue(is_valid_imaging_dicom(read_dicom_directory(SIEMENS_ANATOMICAL)[0]))

    def test_get_vendor(self):
        self.assertEqual(get_vendor(read_dicom_directory(SIEMENS_ANATOMICAL)), Vendor.SIEMENS)
        self.assertEqual(get_vendor(read_dicom_directory(GE_ANATOMICAL)), Vendor.GE)
        self.assertEqual(get_vendor(read_dicom_directory(PHILIPS_ANATOMICAL)), Vendor.PHILIPS)
        self.assertEqual(get_vendor(read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL)), Vendor.PHILIPS)
        self.assertEqual(get_vendor(read_dicom_directory(GENERIC_ANATOMICAL)), Vendor.GENERIC)


class TestConversionGantryTilted(unittest.TestCase):
    def setUp(self):
        settings.disable_validate_orthogonal()
        settings.enable_resampling()
        settings.set_resample_padding(-1000)
        settings.set_resample_spline_interpolation_order(1)

    def tearDown(self):
        settings.disable_resampling()
        settings.enable_validate_orthogonal()

    def test_resampling(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = dicom_series_to_nifti(FAILING_ORHTOGONAL,
                                            os.path.join(tmp_output_dir, 'test.nii.gz'), False)
            self.assertTrue(os.path.isfile(results['NII_FILE']))
        finally:
            shutil.rmtree(tmp_output_dir)


if __name__ == '__main__':
    unittest.main()
