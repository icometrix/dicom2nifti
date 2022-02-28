# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import os
import shutil
import tempfile
import unittest

from dicom2nifti import settings
from dicom2nifti.common import read_dicom_directory, validate_slice_increment, \
    validate_slicecount, validate_orthogonal, validate_orientation, \
    sort_dicoms, is_slice_increment_inconsistent
from dicom2nifti.convert_generic import generic_dicom_to_nifti
from dicom2nifti.exceptions import ConversionValidationError

from .test_data import *


class TestConversionCommon(unittest.TestCase):
    def setUp(self):
        settings.enable_validate_slice_increment()
        settings.enable_validate_slicecount()
        settings.enable_validate_orientation()
        settings.enable_validate_orthogonal()

    def test_validate_slice_increment(self):
        validate_slice_increment(sort_dicoms(read_dicom_directory(GE_ANATOMICAL)))
        self.assertRaises(ConversionValidationError,
                          validate_slice_increment,
                          sort_dicoms(read_dicom_directory(FAILING_SLICEINCREMENT)))

    def test_validate_slice_increment_disabled(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            self.assertRaises(ConversionValidationError,
                              generic_dicom_to_nifti,
                              read_dicom_directory(FAILING_SLICEINCREMENT),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            settings.disable_validate_slice_increment()
            generic_dicom_to_nifti(read_dicom_directory(FAILING_SLICEINCREMENT),
                                   os.path.join(tmp_output_dir, 'test.nii.gz'))
        finally:
            settings.enable_validate_slice_increment()
            shutil.rmtree(tmp_output_dir)

    def test_is_slice_increment_inconsistent(self):
        self.assertFalse(
            is_slice_increment_inconsistent(sort_dicoms(read_dicom_directory(GE_ANATOMICAL)))
        )
        self.assertTrue(
            is_slice_increment_inconsistent(sort_dicoms(read_dicom_directory(FAILING_SLICEINCREMENT)))
        )

    def test_validate_slicecount(self):
        validate_slicecount(read_dicom_directory(GE_ANATOMICAL))
        self.assertRaises(ConversionValidationError,
                          validate_slicecount,
                          read_dicom_directory(FAILING_SLICECOUNT))

    def test_validate_slicecount_disabled(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            self.assertRaises(ConversionValidationError,
                              generic_dicom_to_nifti,
                              read_dicom_directory(FAILING_SLICECOUNT),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            settings.disable_validate_slicecount()
            generic_dicom_to_nifti(read_dicom_directory(FAILING_SLICECOUNT),
                                   os.path.join(tmp_output_dir, 'test.nii.gz'))
        finally:
            settings.enable_validate_slicecount()
            shutil.rmtree(tmp_output_dir)

    def test_validate_orthogonal(self):
        validate_orthogonal(read_dicom_directory(GE_ANATOMICAL))
        self.assertRaises(ConversionValidationError,
                          validate_orthogonal,
                          read_dicom_directory(FAILING_ORHTOGONAL))

    def test_validate_orthogonal_disabled(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            settings.disable_validate_slicecount()
            self.assertRaises(ConversionValidationError,
                              generic_dicom_to_nifti,
                              read_dicom_directory(FAILING_ORHTOGONAL),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            settings.disable_validate_orthogonal()
            generic_dicom_to_nifti(read_dicom_directory(FAILING_ORHTOGONAL),
                                   os.path.join(tmp_output_dir, 'test.nii.gz'))

        finally:
            settings.enable_validate_orthogonal()
            shutil.rmtree(tmp_output_dir)

    def test_validate_orientation(self):
        validate_orientation(read_dicom_directory(GE_ANATOMICAL))

        self.assertRaises(ConversionValidationError,
                          validate_orientation,
                          read_dicom_directory(FAILING_ORIENTATION))

    def test_validate_orientation_disabled(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            settings.disable_validate_orthogonal()  # this will also fail on this data
            settings.disable_validate_slice_increment()  # this will also fail on this data
            settings.disable_validate_slicecount()
            self.assertRaises(ConversionValidationError,
                              generic_dicom_to_nifti,
                              read_dicom_directory(FAILING_ORIENTATION),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            settings.disable_validate_orientation()
            generic_dicom_to_nifti(read_dicom_directory(FAILING_ORIENTATION),
                                   os.path.join(tmp_output_dir, 'test.nii.gz'))

        finally:
            settings.enable_validate_orientation()
            shutil.rmtree(tmp_output_dir)


if __name__ == '__main__':
    unittest.main()
