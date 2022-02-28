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

import tests.test_data as test_data

from dicom2nifti.convert_ge import ge_dicom_to_nifti, _get_grouped_dicoms, _is_4d, _is_diffusion_imaging
from dicom2nifti.common import get_vendor, Vendor, read_dicom_directory
from .test_tools import assert_compare_nifti, assert_compare_bval, ground_thruth_filenames


class TestConversionGE(unittest.TestCase):
    def test_diffusion_images(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = ge_dicom_to_nifti(read_dicom_directory(test_data.GE_DTI), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            self.assertTrue(results.get('BVAL_FILE') is None)
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            self.assertTrue(results.get('BVEC_FILE') is None)
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = ge_dicom_to_nifti(read_dicom_directory(test_data.GE_DTI),
                                        os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(test_data.GE_DTI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(test_data.GE_DTI)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(test_data.GE_DTI)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            ge_dicom_to_nifti(read_dicom_directory(test_data.GE_DTI_IMPLICIT),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(test_data.GE_DTI_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(test_data.GE_DTI_IMPLICIT)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(test_data.GE_DTI_IMPLICIT)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_diffusion_images_old(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = ge_dicom_to_nifti(read_dicom_directory(test_data.GE_DTI_OLD),
                                        os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(test_data.GE_DTI_OLD)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_4d(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = ge_dicom_to_nifti(read_dicom_directory(test_data.GE_FMRI),
                                        os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(test_data.GE_FMRI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = ge_dicom_to_nifti(read_dicom_directory(test_data.GE_FMRI_IMPLICIT),
                                        os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(test_data.GE_FMRI_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = ge_dicom_to_nifti(read_dicom_directory(test_data.GE_ANATOMICAL), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = ge_dicom_to_nifti(read_dicom_directory(test_data.GE_ANATOMICAL),
                                        os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(test_data.GE_ANATOMICAL)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = ge_dicom_to_nifti(read_dicom_directory(test_data.GE_ANATOMICAL_IMPLICIT),
                                        os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(test_data.GE_ANATOMICAL_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_is_ge(self):
        self.assertNotEqual(get_vendor(read_dicom_directory(test_data.SIEMENS_ANATOMICAL)), Vendor.GE)
        self.assertEqual(get_vendor(read_dicom_directory(test_data.GE_ANATOMICAL)), Vendor.GE)
        self.assertNotEqual(get_vendor(read_dicom_directory(test_data.PHILIPS_ANATOMICAL)), Vendor.GE)
        self.assertNotEqual(get_vendor(read_dicom_directory(test_data.GENERIC_ANATOMICAL)), Vendor.GE)
        self.assertNotEqual(get_vendor(read_dicom_directory(test_data.HITACHI_ANATOMICAL)), Vendor.GE)

    def test_is_4d(self):
        self.assertTrue(_is_4d(_get_grouped_dicoms(read_dicom_directory(test_data.GE_DTI))))
        self.assertTrue(_is_4d(_get_grouped_dicoms(read_dicom_directory(test_data.GE_FMRI))))
        self.assertFalse(_is_4d(_get_grouped_dicoms(read_dicom_directory(test_data.GE_ANATOMICAL))))

    def test_is_diffusion_imaging(self):
        self.assertTrue(_is_diffusion_imaging(_get_grouped_dicoms(read_dicom_directory(test_data.GE_DTI))))
        self.assertFalse(_is_diffusion_imaging(_get_grouped_dicoms(read_dicom_directory(test_data.GE_FMRI))))
        self.assertFalse(_is_diffusion_imaging(_get_grouped_dicoms(read_dicom_directory(test_data.GE_ANATOMICAL))))


if __name__ == '__main__':
    unittest.main()
