# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import os
import shutil
import tempfile
import unittest

import dicom2nifti
import tests.test_data as test_data
from dicom2nifti.common import read_dicom_directory, \
    validate_slice_increment, \
    validate_slicecount, \
    validate_orthogonal, \
    validate_orientation, \
    sort_dicoms, is_slice_increment_inconsistent
from dicom2nifti.convert_generic import dicom_to_nifti
from dicom2nifti.exceptions import ConversionValidationError


class TestConversionCommon(unittest.TestCase):
    def setUp(self):
        dicom2nifti.enable_validate_slice_increment()
        dicom2nifti.enable_validate_slicecount()
        dicom2nifti.enable_validate_orientation()
        dicom2nifti.enable_validate_orthogonal()

    def test_validate_slice_increment(self):
        validate_slice_increment(sort_dicoms(read_dicom_directory(test_data.GE_ANATOMICAL)))

        self.assertRaises(ConversionValidationError,
                          validate_slice_increment,
                          sort_dicoms(read_dicom_directory(test_data.FAILING_SLICEINCREMENT)))

    def test_validate_slice_increment_disabled(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            self.assertRaises(ConversionValidationError,
                              dicom_to_nifti,
                              read_dicom_directory(test_data.FAILING_SLICEINCREMENT),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            dicom2nifti.disable_validate_slice_increment()
            dicom_to_nifti(read_dicom_directory(test_data.FAILING_SLICEINCREMENT),
                           os.path.join(tmp_output_dir, 'test.nii.gz'))

        finally:
            dicom2nifti.enable_validate_slice_increment()
            shutil.rmtree(tmp_output_dir)

    def test_is_slice_increment_inconsistent(self):
        self.assertFalse(
            is_slice_increment_inconsistent(sort_dicoms(read_dicom_directory(test_data.GE_ANATOMICAL))))
        self.assertTrue(
            is_slice_increment_inconsistent(sort_dicoms(read_dicom_directory(test_data.FAILING_SLICEINCREMENT))))

    def test_multiframe_validate_missing_per_frame(self):
        # A dicom that reaches the multiframe validators without a
        # PerFrameFunctionalGroupsSequence must raise a descriptive
        # ConversionValidationError instead of an opaque AttributeError (issue #139).
        from pydicom.dataset import Dataset
        from dicom2nifti.common import multiframe_validate_orientation, \
            multiframe_validate_slicecount, \
            multiframe_validate_orthogonal
        dataset = Dataset()  # no PerFrameFunctionalGroupsSequence
        for validator in (multiframe_validate_orientation,
                          multiframe_validate_slicecount,
                          multiframe_validate_orthogonal):
            self.assertRaises(ConversionValidationError, validator, [dataset])

    def test_validate_slicecount(self):
        validate_slicecount(read_dicom_directory(test_data.GE_ANATOMICAL))

        self.assertRaises(ConversionValidationError,
                          validate_slicecount,
                          read_dicom_directory(test_data.FAILING_SLICECOUNT))

    def test_validate_slicecount_disabled(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            self.assertRaises(ConversionValidationError,
                              dicom_to_nifti,
                              read_dicom_directory(test_data.FAILING_SLICECOUNT),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            dicom2nifti.disable_validate_slicecount()
            dicom_to_nifti(read_dicom_directory(test_data.FAILING_SLICECOUNT),
                           os.path.join(tmp_output_dir, 'test.nii.gz'))

        finally:
            dicom2nifti.enable_validate_slicecount()
            shutil.rmtree(tmp_output_dir)

    def test_validate_orthogonal(self):
        validate_orthogonal(read_dicom_directory(test_data.GE_ANATOMICAL))

        self.assertRaises(ConversionValidationError,
                          validate_orthogonal,
                          read_dicom_directory(test_data.FAILING_ORHTOGONAL))

    def test_validate_orthogonal_disabled(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            dicom2nifti.disable_validate_slicecount()
            self.assertRaises(ConversionValidationError,
                              dicom_to_nifti,
                              read_dicom_directory(test_data.FAILING_ORHTOGONAL),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            dicom2nifti.disable_validate_orthogonal()
            dicom_to_nifti(read_dicom_directory(test_data.FAILING_ORHTOGONAL),
                           os.path.join(tmp_output_dir, 'test.nii.gz'))

        finally:
            dicom2nifti.enable_validate_orthogonal()
            shutil.rmtree(tmp_output_dir)

    def test_validate_orientation(self):
        validate_orientation(read_dicom_directory(test_data.GE_ANATOMICAL))

        self.assertRaises(ConversionValidationError,
                          validate_orientation,
                          read_dicom_directory(test_data.FAILING_ORIENTATION))

    def test_validate_orientation_disabled(self):
        tmp_output_dir = tempfile.mkdtemp()
        try:
            dicom2nifti.disable_validate_orthogonal()  # this will also fail on this data
            dicom2nifti.disable_validate_slice_increment()  # this will also fail on this data
            dicom2nifti.disable_validate_slicecount()
            self.assertRaises(ConversionValidationError,
                              dicom_to_nifti,
                              read_dicom_directory(test_data.FAILING_ORIENTATION),
                              os.path.join(tmp_output_dir, 'test.nii.gz'))
            dicom2nifti.disable_validate_orientation()
            dicom_to_nifti(read_dicom_directory(test_data.FAILING_ORIENTATION),
                           os.path.join(tmp_output_dir, 'test.nii.gz'))

        finally:
            dicom2nifti.enable_validate_orientation()
            shutil.rmtree(tmp_output_dir)


if __name__ == '__main__':
    unittest.main()
