# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import os
import logging
import shutil
import tempfile

import dicom2nifti.convert_dir as convert_directory
from dicom2nifti import settings, dicom_series_to_nifti


def run_convert_directory():

    tmp_output_dir = tempfile.mkdtemp()
    try:
        settings.enable_resampling()
        settings.set_resample_spline_interpolation_order(1)
        settings.set_resample_padding(-1000)
        settings.disable_validate_slice_increment()
        # settings.enable_validate_instance_number()
        settings.disable_validate_orthogonal()
        convert_directory.convert_directory("/Users/abrys/Downloads/scans",
                                            "/Users/abrys/Downloads/scans")

    finally:
        shutil.rmtree(tmp_output_dir)

def run_convert_directory2():
    logging.basicConfig(level=logging.DEBUG)
    tmp_output_dir = tempfile.mkdtemp()
    try:
        import pydicom
        # headers = dcmread("/Users/abrys/Downloads/failing_cases/test.dcm")
        convert_directory.convert_directory("/Users/abrys/Downloads/dti",
                                            "/Users/abrys/Downloads/dti")

    finally:
        shutil.rmtree(tmp_output_dir)

def run_convert_directory3():

    tmp_output_dir = tempfile.mkdtemp()
    try:
        import pydicom
        settings.disable_validate_slicecount()
        convert_directory.convert_directory("/Users/abrys/Downloads/CS-2390_TP1",
                                            "/Users/abrys/Downloads/CS-2390_TP1")

    finally:
        shutil.rmtree(tmp_output_dir)


if __name__ == '__main__':
    #dicom_series_to_nifti(os.path.expanduser("~/Downloads/CS-2390_t2"),
    #                      os.path.expanduser("~/Downloads/CS-2390_t2/dicom_download.nii.gz"))

    convert_directory.convert_directory("/Users/abrys/Downloads/CS-2390_TP1",
                                        "/Users/abrys/Downloads/CS-2390_TP1")



