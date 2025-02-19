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
import pydicom
from pydicom import dcmread

import dicom2nifti.common as common
import dicom2nifti.convert_siemens as convert_siemens
import tests.test_data as test_data
from dicom2nifti.common import read_dicom_directory
from tests.test_tools import assert_compare_nifti, assert_compare_bval, ground_thruth_filenames


class TestConversionSiemens(unittest.TestCase):
    def test_diffusion_imaging(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_DTI),
                                                     None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            self.assertTrue(results.get('BVAL_FILE') is None)
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            self.assertTrue(results.get('BVEC_FILE') is None)
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_DTI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_DTI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.SIEMENS_DTI)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.SIEMENS_DTI)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_DTI_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_DTI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.SIEMENS_DTI_IMPLICIT)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.SIEMENS_DTI_IMPLICIT)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_CLASSIC_DTI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_CLASSIC_DTI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.SIEMENS_CLASSIC_DTI)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.SIEMENS_CLASSIC_DTI)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_CLASSIC_DTI_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_CLASSIC_DTI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
            assert_compare_bval(results['BVAL_FILE'],
                                ground_thruth_filenames(test_data.SIEMENS_CLASSIC_DTI_IMPLICIT)[2])
            self.assertTrue(isinstance(results['BVAL'], numpy.ndarray))
            assert_compare_bval(results['BVEC_FILE'],
                                ground_thruth_filenames(test_data.SIEMENS_CLASSIC_DTI_IMPLICIT)[3])
            self.assertTrue(isinstance(results['BVEC'], numpy.ndarray))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_4d(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_FMRI),
                                                     None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_FMRI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_FMRI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_FMRI_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_FMRI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_CLASSIC_FMRI),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_CLASSIC_FMRI)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_CLASSIC_FMRI_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_CLASSIC_FMRI_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_ANATOMICAL),
                                                     None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_ANATOMICAL),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_ANATOMICAL)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_MULTIFRAME_ANATOMICAL),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_MULTIFRAME_ANATOMICAL)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_siemens.dicom_to_nifti(read_dicom_directory(test_data.SIEMENS_ANATOMICAL_IMPLICIT),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(test_data.SIEMENS_ANATOMICAL_IMPLICIT)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_is_mosaic(self):
        # test wit directory
        assert convert_siemens._is_mosaic(read_dicom_directory(test_data.SIEMENS_DTI))
        assert convert_siemens._is_mosaic(read_dicom_directory(test_data.SIEMENS_FMRI))
        assert not convert_siemens._is_mosaic(read_dicom_directory(test_data.SIEMENS_CLASSIC_DTI))
        assert not convert_siemens._is_mosaic(read_dicom_directory(test_data.SIEMENS_CLASSIC_FMRI))
        assert not convert_siemens._is_mosaic(read_dicom_directory(test_data.SIEMENS_ANATOMICAL))
        # test with grouped dicoms
        assert convert_siemens._is_mosaic(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_DTI)))
        assert convert_siemens._is_mosaic(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_FMRI)))
        assert not convert_siemens._is_mosaic(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_CLASSIC_DTI)))
        assert not convert_siemens._is_mosaic(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_CLASSIC_FMRI)))
        assert not convert_siemens._is_mosaic(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_ANATOMICAL)))

    def test_is_4d(self):
        assert convert_siemens._is_4d(read_dicom_directory(test_data.SIEMENS_DTI))
        assert convert_siemens._is_4d(read_dicom_directory(test_data.SIEMENS_FMRI))
        assert not convert_siemens._is_4d(read_dicom_directory(test_data.SIEMENS_CLASSIC_DTI))
        assert not convert_siemens._is_4d(read_dicom_directory(test_data.SIEMENS_CLASSIC_FMRI))
        assert not convert_siemens._is_4d(read_dicom_directory(test_data.SIEMENS_ANATOMICAL))

    def test_is_diffusion_imaging(self):
        assert convert_siemens._is_diffusion_imaging(read_dicom_directory(test_data.SIEMENS_DTI)[0])
        assert not convert_siemens._is_diffusion_imaging(read_dicom_directory(test_data.SIEMENS_FMRI)[0])
        assert convert_siemens._is_diffusion_imaging(read_dicom_directory(test_data.SIEMENS_CLASSIC_DTI)[0])
        assert not convert_siemens._is_diffusion_imaging(read_dicom_directory(test_data.SIEMENS_CLASSIC_FMRI)[0])
        assert not convert_siemens._is_diffusion_imaging(read_dicom_directory(test_data.SIEMENS_ANATOMICAL)[0])

    def test_is_classic_4d(self):
        assert not convert_siemens._is_classic_4d(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_DTI)))
        assert not convert_siemens._is_classic_4d(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_FMRI)))
        assert convert_siemens._is_classic_4d(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_CLASSIC_DTI)))
        assert convert_siemens._is_classic_4d(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_CLASSIC_FMRI)))
        assert not convert_siemens._is_classic_4d(
            convert_siemens._classic_get_grouped_dicoms(read_dicom_directory(test_data.SIEMENS_ANATOMICAL)))

    def test_is_siemens(self):
        assert not common.is_siemens(read_dicom_directory(test_data.PHILIPS_ANATOMICAL))
        assert common.is_siemens(read_dicom_directory(test_data.SIEMENS_ANATOMICAL))
        assert not common.is_siemens(read_dicom_directory(test_data.GE_ANATOMICAL))
        assert not common.is_siemens(read_dicom_directory(test_data.GENERIC_ANATOMICAL))
        assert not common.is_siemens(read_dicom_directory(test_data.HITACHI_ANATOMICAL))

    def test_get_asconv_headers(self):
        mosaic = dcmread(os.path.join(test_data.SIEMENS_FMRI, 'IM-0001-0001.dcm'))
        asconv_headers = convert_siemens._get_asconv_headers(mosaic)
        assert len(asconv_headers) == 64022


if __name__ == '__main__':
    unittest.main()
