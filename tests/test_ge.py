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

import convert_generic
import tests.test_data as test_data

import dicom2nifti.convert_ge as convert_ge
import dicom2nifti.common as common
from dicom2nifti.common import read_dicom_directory
from tests.test_tools import assert_compare_nifti, assert_compare_bval, assert_compare_bvec, ground_thruth_filenames


class TestConversionGE(unittest.TestCase):
    def test_diffusion_images(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_DTI),
                                                None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            self.assertTrue(results.get('BVAL_FILE') is None)
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            self.assertTrue(results.get('BVEC_FILE') is None)
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            results = convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_DTI),
                                                os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                        ground_thruth_filenames(test_data.GE_DTI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                       ground_thruth_filenames(test_data.GE_DTI)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                       ground_thruth_filenames(test_data.GE_DTI)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_DTI_IMPLICIT),
                                      os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                        ground_thruth_filenames(test_data.GE_DTI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                       ground_thruth_filenames(test_data.GE_DTI_IMPLICIT)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                       ground_thruth_filenames(test_data.GE_DTI_IMPLICIT)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_diffusion_images_old(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_DTI_OLD),
                                                os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                        ground_thruth_filenames(test_data.GE_DTI_OLD)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

        finally:
            shutil.rmtree(tmp_output_dir)

    def test_4d(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_FMRI),
                                                os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                        ground_thruth_filenames(test_data.GE_FMRI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            results = convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_FMRI_IMPLICIT),
                                                os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                        ground_thruth_filenames(test_data.GE_FMRI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_ANATOMICAL),
                                                None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_ANATOMICAL),
                                                os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                        ground_thruth_filenames(test_data.GE_ANATOMICAL)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            results = convert_ge.dicom_to_nifti(read_dicom_directory(test_data.GE_ANATOMICAL_IMPLICIT),
                                                os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                        ground_thruth_filenames(test_data.GE_ANATOMICAL_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_is_ge(self):
        assert not common.is_ge(read_dicom_directory(test_data.SIEMENS_ANATOMICAL))
        assert common.is_ge(read_dicom_directory(test_data.GE_ANATOMICAL))
        assert not common.is_ge(read_dicom_directory(test_data.PHILIPS_ANATOMICAL))
        assert not common.is_ge(read_dicom_directory(test_data.GENERIC_ANATOMICAL))
        assert not common.is_ge(read_dicom_directory(test_data.HITACHI_ANATOMICAL))

    def test_is_4d(self):
        diffusion_group = convert_generic.get_grouped_dicoms(read_dicom_directory(test_data.GE_DTI))
        _4d_group = convert_generic.get_grouped_dicoms(read_dicom_directory(test_data.GE_FMRI))
        anatomical_group = convert_generic.get_grouped_dicoms(read_dicom_directory(test_data.GE_ANATOMICAL))
        self.assertTrue(convert_generic.is_4d(diffusion_group))
        self.assertTrue(convert_generic.is_4d(_4d_group))
        self.assertFalse(convert_generic.is_4d(anatomical_group))

    def test_is_diffusion_imaging(self):
        diffusion_group = convert_generic.get_grouped_dicoms(read_dicom_directory(test_data.GE_DTI))
        _4d_group = convert_generic.get_grouped_dicoms(read_dicom_directory(test_data.GE_FMRI))
        anatomical_group = convert_generic.get_grouped_dicoms(read_dicom_directory(test_data.GE_ANATOMICAL))
        assert convert_ge._is_diffusion_imaging(diffusion_group)
        assert not convert_ge._is_diffusion_imaging(_4d_group)
        assert not convert_ge._is_diffusion_imaging(anatomical_group)


if __name__ == '__main__':
    unittest.main()
