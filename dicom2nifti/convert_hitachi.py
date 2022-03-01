# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import logging

import pydicom.config as pydicom_config

from .common import initial_dicom_checks
from .convert_generic import generic_dicom_to_nifti

pydicom_config.enforce_valid_values = False
logger = logging.getLogger(__name__)


def hitachi_dicom_to_nifti(dicom_input, output_file=None):
    """
    This is the main dicom to nifti conversion fuction for hitachi images.
    As input hitachi images are required. It will then determine the type of images and do the correct conversion

    Examples: See unit test

    :param output_file: file path to the output nifti
    :param dicom_input: directory with dicom files for 1 scan
    """
    dicom_input = initial_dicom_checks(dicom_input)

    # TODO add validations and conversion for DTI and fMRI once testdata is available

    logger.info('Assuming anatomical data')
    return generic_dicom_to_nifti(dicom_input, output_file, False)
