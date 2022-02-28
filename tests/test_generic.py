# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import os
import random
import shutil
import string
import tempfile
import unittest

import nibabel

from dicom2nifti import settings
from dicom2nifti.convert_generic import generic_dicom_to_nifti
from dicom2nifti.common import read_dicom_directory
from dicom2nifti.compressed_dicom import is_dicom_file
from dicom2nifti.exceptions import ConversionError

from .test_data import *
from .test_tools import assert_compare_nifti, ground_thruth_filenames


class TestConversionGeneric(unittest.TestCase):
    def test_anatomical(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = generic_dicom_to_nifti(read_dicom_directory(GE_ANATOMICAL), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = generic_dicom_to_nifti(read_dicom_directory(GE_ANATOMICAL),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(GE_ANATOMICAL)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

        finally:
            shutil.rmtree(tmp_output_dir)

    def test_rgb(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            results = generic_dicom_to_nifti(read_dicom_directory(GENERIC_RGB), None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

            results = generic_dicom_to_nifti(read_dicom_directory(GENERIC_RGB),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(GENERIC_RGB)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

        finally:
            shutil.rmtree(tmp_output_dir)

    def test_single_slice(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            settings.disable_validate_slicecount()
            results = generic_dicom_to_nifti(read_dicom_directory(GE_ANATOMICAL_SINGLE_SLICE),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'], ground_thruth_filenames(GE_ANATOMICAL_SINGLE_SLICE)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)
        finally:
            settings.enable_validate_slicecount()
            shutil.rmtree(tmp_output_dir)

    @unittest.skip("Skip untill we figure out why it fails on circleci")
    def test_inconsistent_slice_increment_resampling(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            settings.disable_validate_orthogonal()
            settings.disable_validate_slice_increment()
            settings.enable_resampling()
            settings.set_resample_padding(0)
            settings.set_resample_spline_interpolation_order(1)
            results = generic_dicom_to_nifti(read_dicom_directory(FAILING_SLICEINCREMENT_2),
                                             os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                 ground_thruth_filenames(FAILING_SLICEINCREMENT_2)[0])
            self.assertIsInstance(results['NII'], nibabel.nifti1.Nifti1Image)

        finally:
            settings.disable_resampling()
            settings.enable_validate_slice_increment()
            settings.enable_validate_orientation()
            shutil.rmtree(tmp_output_dir)

    def test_not_a_volume(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            settings.disable_validate_orthogonal()
            with self.assertRaises(ConversionError) as exception:
                generic_dicom_to_nifti(read_dicom_directory(FAILING_NOTAVOLUME),
                                       os.path.join(tmp_output_dir, 'test.nii.gz'))
            self.assertEqual(str(exception.exception), 'NOT_A_VOLUME')
        finally:
            settings.enable_validate_orthogonal()
            shutil.rmtree(tmp_output_dir)

    def test_is_dicom_file(self):
        input_file = os.path.join(GENERIC_COMPRESSED, 'IM-0001-0001-0001.dcm')
        self.assertTrue(is_dicom_file(input_file))
        temporary_directory = tempfile.mkdtemp()
        try:
            # test for empty file
            non_dicom1 = os.path.join(temporary_directory, 'non_dicom.dcm')
            open(non_dicom1, 'a').close()
            self.assertFalse(is_dicom_file(non_dicom1))

            # test for non empty file
            non_dicom2 = os.path.join(temporary_directory, 'non_dicom2.dcm')
            with open(non_dicom2, 'w') as file_2:
                file_2.write(''.join(random.SystemRandom().choice(string.digits) for _ in range(300)))
            self.assertFalse(is_dicom_file(non_dicom2))
        finally:
            shutil.rmtree(temporary_directory)


if __name__ == '__main__':
    unittest.main()
