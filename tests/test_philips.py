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

import dicom2nifti.common as common
import dicom2nifti.convert_philips as convert_philips
import dicom2nifti.settings as settings
from dicom2nifti.common import read_dicom_directory
from dicom2nifti.exceptions import ConversionError
from tests.test_tools import assert_compare_nifti, assert_compare_bval, assert_compare_bvec, ground_thruth_filenames


class TestConversionPhilips(unittest.TestCase):

    def test_diffusion_imaging(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_DTI),
                                                     None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            self.assertTrue(results.get('BVAL_FILE') is None)
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            self.assertTrue(results.get('BVEC_FILE') is None)
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            # check PHILIPS_DTI
            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_DTI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_DTI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_DTI)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_DTI)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            # check PHILIPS_DTI_002
            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_DTI_002),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_DTI_002)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_DTI_002)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_DTI_002)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            # check PHILIPS_ENHANCED_DTI
            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ENHANCED_DTI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ENHANCED_DTI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_ENHANCED_DTI)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_ENHANCED_DTI)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            # check PHILIPS_DTI_IMPLICIT
            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_DTI_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_DTI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_DTI_IMPLICIT)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_DTI_IMPLICIT)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            # check PHILIPS_DTI_IMPLICIT_002
            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_DTI_IMPLICIT_002),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_DTI_IMPLICIT_002)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_DTI_IMPLICIT_002)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_DTI_IMPLICIT_002)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))



            # check PHILIPS_DTI_IMPLICIT_002
            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ENHANCED_DTI_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ENHANCED_DTI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_ENHANCED_DTI_IMPLICIT)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.PHILIPS_ENHANCED_DTI_IMPLICIT)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

        finally:
            shutil.rmtree(tmp_output_dir)

    def test_4d(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_FMRI),
                                                     None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_FMRI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_FMRI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_FMRI_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_FMRI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ENHANCED_FMRI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ENHANCED_FMRI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ENHANCED_FMRI_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ENHANCED_FMRI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

        finally:
            shutil.rmtree(tmp_output_dir)

    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ANATOMICAL),
                                                     None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ANATOMICAL),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ANATOMICAL)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ANATOMICAL_SWI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ANATOMICAL_SWI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ANATOMICAL_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ANATOMICAL_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ENHANCED_ANATOMICAL),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ENHANCED_ANATOMICAL)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_philips.dicom_to_nifti(read_dicom_directory(test_data.PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_anatomical_implicit(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            settings.disable_validate_multiframe_implicit()
            results = convert_philips.dicom_to_nifti(read_dicom_directory(
                test_data.PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT),
                os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            settings.enable_validate_multiframe_implicit()
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_is_philips(self):
        assert common.is_philips(read_dicom_directory(test_data.PHILIPS_ANATOMICAL))
        assert not common.is_philips(read_dicom_directory(test_data.SIEMENS_ANATOMICAL))
        assert not common.is_philips(read_dicom_directory(test_data.GE_ANATOMICAL))
        assert not common.is_philips(read_dicom_directory(test_data.GENERIC_ANATOMICAL))
        assert not common.is_philips(read_dicom_directory(test_data.HITACHI_ANATOMICAL))

    def test_is_multiframe_dicom(self):
        assert common.is_multiframe_dicom(read_dicom_directory(test_data.PHILIPS_ENHANCED_DTI))
        assert not common.is_multiframe_dicom(read_dicom_directory(test_data.PHILIPS_DTI))
        assert common.is_multiframe_dicom(read_dicom_directory(test_data.PHILIPS_ENHANCED_ANATOMICAL))
        assert not common.is_multiframe_dicom(read_dicom_directory(test_data.PHILIPS_ANATOMICAL))
        assert common.is_multiframe_dicom(read_dicom_directory(test_data.PHILIPS_ENHANCED_FMRI))
        assert not common.is_multiframe_dicom(read_dicom_directory(test_data.PHILIPS_FMRI))

    def test_is_multiframe_diffusion_imaging(self):
        assert convert_philips._is_multiframe_diffusion_imaging(read_dicom_directory(test_data.PHILIPS_ENHANCED_DTI))
        assert not convert_philips._is_multiframe_diffusion_imaging(read_dicom_directory(test_data.PHILIPS_DTI))
        assert not convert_philips._is_multiframe_diffusion_imaging(read_dicom_directory(
            test_data.PHILIPS_ENHANCED_ANATOMICAL))
        assert not convert_philips._is_multiframe_diffusion_imaging(read_dicom_directory(test_data.PHILIPS_ANATOMICAL))
        assert not convert_philips._is_multiframe_diffusion_imaging(read_dicom_directory(
            test_data.PHILIPS_ENHANCED_FMRI))
        assert not convert_philips._is_multiframe_diffusion_imaging(read_dicom_directory(test_data.PHILIPS_FMRI))

    def test_is_multiframe_4d(self):
        assert convert_philips._is_multiframe_4d(read_dicom_directory(test_data.PHILIPS_ENHANCED_DTI))
        assert not convert_philips._is_multiframe_4d(read_dicom_directory(test_data.PHILIPS_DTI))
        assert not convert_philips._is_multiframe_4d(read_dicom_directory(test_data.PHILIPS_ENHANCED_ANATOMICAL))
        assert not convert_philips._is_multiframe_4d(read_dicom_directory(test_data.PHILIPS_ANATOMICAL))
        assert convert_philips._is_multiframe_4d(read_dicom_directory(test_data.PHILIPS_ENHANCED_FMRI))
        assert not convert_philips._is_multiframe_4d(read_dicom_directory(test_data.PHILIPS_FMRI))

    def test_is_multiframe_anatomical(self):
        assert not convert_philips._is_multiframe_anatomical(read_dicom_directory(test_data.PHILIPS_ENHANCED_DTI))
        assert not convert_philips._is_multiframe_anatomical(read_dicom_directory(test_data.PHILIPS_DTI))
        assert convert_philips._is_multiframe_anatomical(read_dicom_directory(test_data.PHILIPS_ENHANCED_ANATOMICAL))
        assert not convert_philips._is_multiframe_anatomical(read_dicom_directory(test_data.PHILIPS_ANATOMICAL))
        assert not convert_philips._is_multiframe_anatomical(read_dicom_directory(test_data.PHILIPS_ENHANCED_FMRI))
        assert not convert_philips._is_multiframe_anatomical(read_dicom_directory(test_data.PHILIPS_FMRI))

    def test_is_singleframe_4d(self):
        assert not convert_philips._is_singleframe_4d(read_dicom_directory(test_data.PHILIPS_ENHANCED_DTI))
        assert convert_philips._is_singleframe_4d(read_dicom_directory(test_data.PHILIPS_DTI))
        assert not convert_philips._is_singleframe_4d(read_dicom_directory(test_data.PHILIPS_ENHANCED_ANATOMICAL))
        assert not convert_philips._is_singleframe_4d(read_dicom_directory(test_data.PHILIPS_ANATOMICAL))
        assert not convert_philips._is_singleframe_4d(read_dicom_directory(test_data.PHILIPS_ENHANCED_FMRI))
        assert convert_philips._is_singleframe_4d(read_dicom_directory(test_data.PHILIPS_FMRI))

    def test_is_singleframe_diffusion_imaging(self):
        assert convert_philips._is_singleframe_diffusion_imaging(
            convert_philips._get_grouped_dicoms(read_dicom_directory(test_data.PHILIPS_DTI)))
        assert not convert_philips._is_singleframe_diffusion_imaging(
            convert_philips._get_grouped_dicoms(read_dicom_directory(test_data.PHILIPS_ANATOMICAL)))
        assert not convert_philips._is_singleframe_diffusion_imaging(
            convert_philips._get_grouped_dicoms(read_dicom_directory(test_data.PHILIPS_FMRI)))


if __name__ == '__main__':
    unittest.main()
