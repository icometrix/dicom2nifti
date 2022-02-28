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
import numpy

from dicom2nifti import settings
from dicom2nifti.common import get_vendor, Vendor, read_dicom_directory, is_multiframe_dicom
from dicom2nifti.convert_philips import philips_dicom_to_nifti, _is_multiframe_diffusion_imaging, \
    _is_multiframe_4d, _is_multiframe_anatomical, _is_singleframe_4d, \
    _is_singleframe_diffusion_imaging, _get_grouped_dicoms
from dicom2nifti.exceptions import ConversionError

from .test_data import *
from .test_tools import assert_compare_nifti, assert_compare_bval, ground_thruth_filenames


class TestConversionPhilips(unittest.TestCase):

    def test_diffusion_imaging(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_DTI), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            self.assertTrue(results.get('BVAL_FILE') is None)
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            self.assertTrue(results.get('BVEC_FILE') is None)
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_DTI),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_DTI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(PHILIPS_DTI)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(PHILIPS_DTI)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_DTI_002),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_DTI_002)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(PHILIPS_DTI_002)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(PHILIPS_DTI_002)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_ENHANCED_DTI),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_ENHANCED_DTI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(PHILIPS_ENHANCED_DTI)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(PHILIPS_ENHANCED_DTI)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_DTI_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(PHILIPS_DTI_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(PHILIPS_DTI_IMPLICIT)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(PHILIPS_DTI_IMPLICIT)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_DTI_IMPLICIT_002),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_DTI_IMPLICIT_002)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(PHILIPS_DTI_IMPLICIT_002)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(PHILIPS_DTI_IMPLICIT_002)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            self.assertRaises(ConversionError,
                              philips_dicom_to_nifti,
                              read_dicom_directory(PHILIPS_ENHANCED_DTI_IMPLICIT),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_4d(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_FMRI), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_FMRI),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_FMRI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_FMRI_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_FMRI_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_ENHANCED_FMRI),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_ENHANCED_FMRI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            self.assertRaises(ConversionError,
                              philips_dicom_to_nifti,
                              read_dicom_directory(PHILIPS_ENHANCED_FMRI_IMPLICIT),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_ANATOMICAL), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_ANATOMICAL),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_ANATOMICAL)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_ANATOMICAL_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_ANATOMICAL_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(PHILIPS_ENHANCED_ANATOMICAL)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            self.assertRaises(ConversionError,
                              philips_dicom_to_nifti,
                              read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_anatomical_implicit(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            settings.disable_validate_multiframe_implicit()
            results = philips_dicom_to_nifti(read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            settings.enable_validate_multiframe_implicit()
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_is_philips(self):
        self.assertEqual(get_vendor(read_dicom_directory(PHILIPS_ANATOMICAL)), Vendor.PHILIPS)
        self.assertNotEqual(get_vendor(read_dicom_directory(SIEMENS_ANATOMICAL)), Vendor.PHILIPS)
        self.assertNotEqual(get_vendor(read_dicom_directory(GE_ANATOMICAL)), Vendor.PHILIPS)
        self.assertNotEqual(get_vendor(read_dicom_directory(GENERIC_ANATOMICAL)), Vendor.PHILIPS)
        self.assertNotEqual(get_vendor(read_dicom_directory(HITACHI_ANATOMICAL)), Vendor.PHILIPS)

    def test_is_multiframe_dicom(self):
        self.assertTrue(is_multiframe_dicom(read_dicom_directory(PHILIPS_ENHANCED_DTI)))
        self.assertFalse(is_multiframe_dicom(read_dicom_directory(PHILIPS_DTI)))
        self.assertTrue(is_multiframe_dicom(read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL)))
        self.assertFalse(is_multiframe_dicom(read_dicom_directory(PHILIPS_ANATOMICAL)))
        self.assertTrue(is_multiframe_dicom(read_dicom_directory(PHILIPS_ENHANCED_FMRI)))
        self.assertFalse(is_multiframe_dicom(read_dicom_directory(PHILIPS_FMRI)))

    def test_is_multiframe_diffusion_imaging(self):
        self.assertTrue(_is_multiframe_diffusion_imaging(read_dicom_directory(PHILIPS_ENHANCED_DTI)))
        self.assertFalse(_is_multiframe_diffusion_imaging(read_dicom_directory(PHILIPS_DTI)))
        self.assertFalse(_is_multiframe_diffusion_imaging(read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL)))
        self.assertFalse(_is_multiframe_diffusion_imaging(read_dicom_directory(PHILIPS_ANATOMICAL)))
        self.assertFalse(_is_multiframe_diffusion_imaging(read_dicom_directory(PHILIPS_ENHANCED_FMRI)))
        self.assertFalse(_is_multiframe_diffusion_imaging(read_dicom_directory(PHILIPS_FMRI)))

    def test_is_multiframe_4d(self):
        self.assertTrue(_is_multiframe_4d(read_dicom_directory(PHILIPS_ENHANCED_DTI)))
        self.assertFalse(_is_multiframe_4d(read_dicom_directory(PHILIPS_DTI)))
        self.assertFalse(_is_multiframe_4d(read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL)))
        self.assertFalse(_is_multiframe_4d(read_dicom_directory(PHILIPS_ANATOMICAL)))
        self.assertTrue(_is_multiframe_4d(read_dicom_directory(PHILIPS_ENHANCED_FMRI)))
        self.assertFalse(_is_multiframe_4d(read_dicom_directory(PHILIPS_FMRI)))

    def test_is_multiframe_anatomical(self):
        self.assertFalse(_is_multiframe_anatomical(read_dicom_directory(PHILIPS_ENHANCED_DTI)))
        self.assertFalse(_is_multiframe_anatomical(read_dicom_directory(PHILIPS_DTI)))
        self.assertTrue(_is_multiframe_anatomical(read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL)))
        self.assertFalse(_is_multiframe_anatomical(read_dicom_directory(PHILIPS_ANATOMICAL)))
        self.assertFalse(_is_multiframe_anatomical(read_dicom_directory(PHILIPS_ENHANCED_FMRI)))
        self.assertFalse(_is_multiframe_anatomical(read_dicom_directory(PHILIPS_FMRI)))

    def test_is_singleframe_4d(self):
        self.assertFalse(_is_singleframe_4d(read_dicom_directory(PHILIPS_ENHANCED_DTI)))
        self.assertTrue(_is_singleframe_4d(read_dicom_directory(PHILIPS_DTI)))
        self.assertFalse(_is_singleframe_4d(read_dicom_directory(PHILIPS_ENHANCED_ANATOMICAL)))
        self.assertFalse(_is_singleframe_4d(read_dicom_directory(PHILIPS_ANATOMICAL)))
        self.assertFalse(_is_singleframe_4d(read_dicom_directory(PHILIPS_ENHANCED_FMRI)))
        self.assertTrue(_is_singleframe_4d(read_dicom_directory(PHILIPS_FMRI)))

    def test_is_singleframe_diffusion_imaging(self):
        self.assertTrue(
            _is_singleframe_diffusion_imaging(_get_grouped_dicoms(read_dicom_directory(PHILIPS_DTI)))
        )
        self.assertFalse(
            _is_singleframe_diffusion_imaging(_get_grouped_dicoms(read_dicom_directory(PHILIPS_ANATOMICAL)))
        )
        self.assertFalse(
            _is_singleframe_diffusion_imaging(_get_grouped_dicoms(read_dicom_directory(PHILIPS_FMRI)))
        )


if __name__ == '__main__':
    unittest.main()
