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

from dicom2nifti.common import get_vendor, Vendor, read_dicom_directory
from dicom2nifti.compressed_dicom import read_file
from dicom2nifti.convert_siemens import siemens_dicom_to_nifti, _is_mosaic, \
    _is_diffusion_imaging, _is_classic_4d, _classic_get_grouped_dicoms, _get_asconv_headers


from .test_data import *
from .test_tools import assert_compare_nifti, assert_compare_bval, ground_thruth_filenames


class TestConversionSiemens(unittest.TestCase):
    def test_diffusion_imaging(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_DTI), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            self.assertTrue(results.get('BVAL_FILE') is None)
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            self.assertTrue(results.get('BVEC_FILE') is None)
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_DTI),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_DTI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(SIEMENS_DTI)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(SIEMENS_DTI)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_DTI_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_DTI_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(SIEMENS_DTI_IMPLICIT)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(SIEMENS_DTI_IMPLICIT)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_CLASSIC_DTI),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_CLASSIC_DTI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(SIEMENS_CLASSIC_DTI)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(SIEMENS_CLASSIC_DTI)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_CLASSIC_DTI_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_CLASSIC_DTI_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            assert_compare_bval(results['BVAL_FILE'], ground_thruth_filenames(SIEMENS_CLASSIC_DTI_IMPLICIT)[2])
            self.assertIsInstance(results['BVAL'], numpy.ndarray)
            assert_compare_bval(results['BVEC_FILE'], ground_thruth_filenames(SIEMENS_CLASSIC_DTI_IMPLICIT)[3])
            self.assertIsInstance(results['BVEC'], numpy.ndarray)
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_4d(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_FMRI), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_FMRI),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_FMRI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_FMRI_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_FMRI_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_CLASSIC_FMRI),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_CLASSIC_FMRI)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_CLASSIC_FMRI_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_CLASSIC_FMRI_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_ANATOMICAL), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_ANATOMICAL),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_ANATOMICAL)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_MULTIFRAME_ANATOMICAL),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_MULTIFRAME_ANATOMICAL)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = siemens_dicom_to_nifti(read_dicom_directory(SIEMENS_ANATOMICAL_IMPLICIT),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(SIEMENS_ANATOMICAL_IMPLICIT)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
            
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_is_mosaic(self):
        # test with directory
        self.assertTrue(_is_mosaic(read_dicom_directory(SIEMENS_DTI)))
        self.assertTrue(_is_mosaic(read_dicom_directory(SIEMENS_FMRI)))
        self.assertFalse(_is_mosaic(read_dicom_directory(SIEMENS_CLASSIC_DTI)))
        self.assertFalse(_is_mosaic(read_dicom_directory(SIEMENS_CLASSIC_FMRI)))
        self.assertFalse(_is_mosaic(read_dicom_directory(SIEMENS_ANATOMICAL)))

        # test with grouped dicoms
        self.assertTrue(_is_mosaic(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_DTI))))
        self.assertTrue(_is_mosaic(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_FMRI))))
        self.assertFalse(_is_mosaic(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_CLASSIC_DTI))))
        self.assertFalse(_is_mosaic(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_CLASSIC_FMRI))))
        self.assertFalse(_is_mosaic(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_ANATOMICAL))))

    def test_is_diffusion_imaging(self):
        self.assertTrue(_is_diffusion_imaging(read_dicom_directory(SIEMENS_DTI)[0]))
        self.assertFalse(_is_diffusion_imaging(read_dicom_directory(SIEMENS_FMRI)[0]))
        self.assertTrue(_is_diffusion_imaging(read_dicom_directory(SIEMENS_CLASSIC_DTI)[0]))
        self.assertFalse(_is_diffusion_imaging(read_dicom_directory(SIEMENS_CLASSIC_FMRI)[0]))
        self.assertFalse(_is_diffusion_imaging(read_dicom_directory(SIEMENS_ANATOMICAL)[0]))

    def test_is_classic_4d(self):
        self.assertFalse(_is_classic_4d(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_DTI))))
        self.assertFalse(_is_classic_4d(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_FMRI))))
        self.assertTrue(_is_classic_4d(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_CLASSIC_DTI))))
        self.assertTrue(_is_classic_4d(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_CLASSIC_FMRI))))
        self.assertFalse(_is_classic_4d(_classic_get_grouped_dicoms(read_dicom_directory(SIEMENS_ANATOMICAL))))

    def test_is_siemens(self):
        self.assertNotEqual(get_vendor(read_dicom_directory(PHILIPS_ANATOMICAL)), Vendor.SIEMENS)
        self.assertEqual(get_vendor(read_dicom_directory(SIEMENS_ANATOMICAL)), Vendor.SIEMENS)
        self.assertNotEqual(get_vendor(read_dicom_directory(GE_ANATOMICAL)), Vendor.SIEMENS)
        self.assertNotEqual(get_vendor(read_dicom_directory(GENERIC_ANATOMICAL)), Vendor.SIEMENS)
        self.assertNotEqual(get_vendor(read_dicom_directory(HITACHI_ANATOMICAL)), Vendor.SIEMENS)

    def test_get_asconv_headers(self):
        mosaic = read_file(os.path.join(SIEMENS_FMRI, 'IM-0001-0001.dcm'))
        asconv_headers = _get_asconv_headers(mosaic)
        self.assertEqual(len(asconv_headers), 64022)


if __name__ == '__main__':
    unittest.main()
