# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import os
import tempfile
import unittest

import nibabel

import dicom2nifti.convert_generic as convert_generic
import tests.test_data as test_data
from dicom2nifti.common import read_dicom_directory
from tests.test_tools import assert_compare_nifti, ground_thruth_filenames


class TestConversionHyperfine(unittest.TestCase):
    def test_anatomical(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            results = convert_generic.dicom_to_nifti(read_dicom_directory(test_data.HYPERFINE_ANATOMICAL),
                                                     None)
            self.assertTrue(results.get('NII_FILE') is None)
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))

            results = convert_generic.dicom_to_nifti(read_dicom_directory(test_data.HYPERFINE_ANATOMICAL),
                                                     os.path.join(tmp_output_dir, 'test.nii.gz'))
            assert_compare_nifti(results['NII_FILE'],
                                        ground_thruth_filenames(test_data.HYPERFINE_ANATOMICAL)[0])
            self.assertTrue(isinstance(results['NII'], nibabel.nifti1.Nifti1Image))



if __name__ == '__main__':
    unittest.main()
