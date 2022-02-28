# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import logging

import pydicom.config as pydicom_config

from .common import get_vendor, Vendor
from .convert_generic import generic_dicom_to_nifti, remove_duplicate_slices, \
    remove_localizers_by_imagetype, remove_localizers_by_orientation
from dicom2nifti.exceptions import ConversionValidationError

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

    assert get_vendor(dicom_input) == Vendor.HITACHI

    # remove duplicate slices based on position and data
    dicom_input = remove_duplicate_slices(dicom_input)

    # remove localizers based on image type
    dicom_input = remove_localizers_by_imagetype(dicom_input)

    # remove_localizers based on image orientation (only valid if slicecount is validated)
    dicom_input = remove_localizers_by_orientation(dicom_input)

    # if no dicoms remain raise exception
    if not dicom_input:
        raise ConversionValidationError('TOO_FEW_SLICES/LOCALIZER')
    # TODO add validations and conversion for DTI and fMRI once testdata is available

    logger.info('Assuming anatomical data')
    return generic_dicom_to_nifti(dicom_input, output_file)


