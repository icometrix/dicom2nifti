# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import os
import shutil
import tempfile
import unittest

from dicom2nifti.exec import dicom2nifti

from .test_data import *


class TestConversionDicom(unittest.TestCase):
    def test_main_function(self):
        tmp_output_dir = tempfile.mkdtemp()
        script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'scripts', 'dicom2nifti')
        self.assertTrue(os.path.isfile(script_file))
        try:
            dicom2nifti([SIEMENS_ANATOMICAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii.gz")))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_gantry_option(self):
        tmp_output_dir = tempfile.mkdtemp()
        script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'scripts', 'dicom2nifti')
        self.assertTrue(os.path.isfile(script_file))
        try:
            dicom2nifti(['-G', FAILING_ORHTOGONAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii.gz")))
            dicom2nifti(['--allow-gantry-tilting', FAILING_ORHTOGONAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii.gz")))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_gantry_resampling(self):
        tmp_output_dir = tempfile.mkdtemp()
        script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'scripts', 'dicom2nifti')
        self.assertTrue(os.path.isfile(script_file))
        try:
            dicom2nifti(['-G', '-r', '-o', '1', '-p', '-1000', FAILING_ORHTOGONAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii.gz")))
            dicom2nifti(['--allow-gantry-tilting', '--resample', '--resample-order', '1',
                         '--resample-padding', '-1000', FAILING_ORHTOGONAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii.gz")))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_multiframe_option(self):
        tmp_output_dir = tempfile.mkdtemp()
        script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'scripts', 'dicom2nifti')
        self.assertTrue(os.path.isfile(script_file))
        try:
            dicom2nifti(['-M', PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "301_dicom2nifti.nii.gz")))
            dicom2nifti(['--allow-multiframe-implicit', PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "301_dicom2nifti.nii.gz")))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_compression_function(self):
        tmp_output_dir = tempfile.mkdtemp()
        script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'scripts', 'dicom2nifti')
        self.assertTrue(os.path.isfile(script_file))
        try:
            dicom2nifti(['-C', SIEMENS_ANATOMICAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii")))
            dicom2nifti(['--no-compression', SIEMENS_ANATOMICAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii")))
        finally:
            shutil.rmtree(tmp_output_dir)

    def test_reorientation_function(self):
        tmp_output_dir = tempfile.mkdtemp()
        script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'scripts', 'dicom2nifti')
        self.assertTrue(os.path.isfile(script_file))
        try:
            dicom2nifti(['-R', SIEMENS_ANATOMICAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii.gz")))
            dicom2nifti(['--no-reorientation', SIEMENS_ANATOMICAL, tmp_output_dir])
            self.assertTrue(os.path.isfile(os.path.join(tmp_output_dir, "4_dicom2nifti.nii.gz")))
        finally:
            shutil.rmtree(tmp_output_dir)


if __name__ == '__main__':
    unittest.main()
