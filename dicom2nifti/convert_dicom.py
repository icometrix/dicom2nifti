# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import logging
import os
import shutil
import tempfile

from nibabel.pydicom_compat import pydicom
from pydicom.tag import Tag

import dicom2nifti.common as common
import dicom2nifti.convert_ge as convert_ge
import dicom2nifti.convert_generic as convert_generic
import dicom2nifti.convert_philips as convert_philips
import dicom2nifti.convert_siemens as convert_siemens
import dicom2nifti.image_reorientation as image_reorientation
import dicom2nifti.resample as resample
import dicom2nifti.settings as settings
from dicom2nifti import convert_hitachi
from dicom2nifti.exceptions import ConversionValidationError, ConversionError

logger = logging.getLogger(__name__)


# Disable this warning as there is not reason for an init class in an enum
# pylint: disable=w0232, r0903, C0103


class Vendor(object):
    """
    Enum with the vendor
    """
    GENERIC = 0
    SIEMENS = 1
    GE = 2
    PHILIPS = 3
    HITACHI = 4


# pylint: enable=w0232, r0903, C0103
def dicom_series_to_nifti(original_dicom_directory, output_file=None, reorient_nifti=True):
    """ Converts dicom single series (see pydicom) to nifty, mimicking SPM

    Examples: See unit test


    will return a dictionary containing
    - the NIFTI under key 'NIFTI'
    - the NIFTI file path under 'NII_FILE'
    - the BVAL file path under 'BVAL_FILE' (only for dti)
    - the BVEC file path under 'BVEC_FILE' (only for dti)

    IMPORTANT:
    If no specific sequence type can be found it will default to anatomical and try to convert.
    You should check that the data you are trying to convert is supported by this code

    Inspired by http://nipy.sourceforge.net/nibabel/dicom/spm_dicom.html
    Inspired by http://code.google.com/p/pydicom/source/browse/source/dicom/contrib/pydicom_series.py

    :param reorient_nifti: if True the nifti affine and data will be updated so the data is stored LAS oriented
    :param output_file: file path to write to if not set to None
    :param original_dicom_directory: directory with the dicom files for a single series/scan
    :return nibabel image
    """
    # copy files so we can can modify without altering the original
    temp_directory = tempfile.mkdtemp()
    try:
        dicom_directory = os.path.join(temp_directory, 'dicom')
        shutil.copytree(original_dicom_directory, dicom_directory)

        dicom_input = common.read_dicom_directory(dicom_directory)

        return dicom_array_to_nifti(dicom_input, output_file, reorient_nifti)

    except AttributeError as exception:
        raise exception

    finally:
        # remove the copied data
        shutil.rmtree(temp_directory)


def dicom_array_to_nifti(dicom_list, output_file, reorient_nifti=True):
    """ Converts dicom single series (see pydicom) to nifty, mimicking SPM

    Examples: See unit test


    will return a dictionary containing
    - the NIFTI under key 'NIFTI'
    - the NIFTI file path under 'NII_FILE'
    - the BVAL file path under 'BVAL_FILE' (only for dti)
    - the BVEC file path under 'BVEC_FILE' (only for dti)

    IMPORTANT:
    If no specific sequence type can be found it will default to anatomical and try to convert.
    You should check that the data you are trying to convert is supported by this code

    Inspired by http://nipy.sourceforge.net/nibabel/dicom/spm_dicom.html
    Inspired by http://code.google.com/p/pydicom/source/browse/source/dicom/contrib/pydicom_series.py

    :param reorient_nifti: if True the nifti affine and data will be updated so the data is stored LAS oriented
    :param output_file: file path to write to
    :param dicom_list: list with uncompressed dicom objects as read by pydicom
    """
    # copy files so we can can modify without altering the original
    if not are_imaging_dicoms(dicom_list):
        raise ConversionValidationError('NON_IMAGING_DICOM_FILES')

    vendor = _get_vendor(dicom_list)

    if vendor == Vendor.GENERIC:
        results = convert_generic.dicom_to_nifti(dicom_list, output_file)
    elif vendor == Vendor.SIEMENS:
        results = convert_siemens.dicom_to_nifti(dicom_list, output_file)
    elif vendor == Vendor.GE:
        results = convert_ge.dicom_to_nifti(dicom_list, output_file)
    elif vendor == Vendor.PHILIPS:
        results = convert_philips.dicom_to_nifti(dicom_list, output_file)
    elif vendor == Vendor.HITACHI:
        results = convert_hitachi.dicom_to_nifti(dicom_list, output_file)
    else:
        raise ConversionValidationError("UNSUPPORTED_DATA")

    # do image reorientation if needed
    if reorient_nifti or settings.resample:
        results['NII'] = image_reorientation.reorient_image(results['NII'], results['NII_FILE'])

    # resampling needs to be after reorientation
    if settings.resample:
        if not common.is_orthogonal_nifti(results['NII']):
            results['NII'] = resample.resample_single_nifti(results['NII'], results['NII_FILE'])

    return results


def are_imaging_dicoms(dicom_input):
    """
    This function will check the dicom headers to see which type of series it is
    Possibilities are fMRI, DTI, Anatomical (if no clear type is found anatomical is used)

    :param dicom_input: directory with dicom files or a list of dicom objects
    """

    # if it is philips and multiframe dicom then we assume it is ok
    if common.is_multiframe_dicom(dicom_input):
        return True

    # for all others if there is image position patient we assume it is ok
    header = dicom_input[0]
    return Tag(0x0020, 0x0037) in header


def _get_vendor(dicom_input):
    """
    This function will check the dicom headers to see which type of series it is
    Possibilities are fMRI, DTI, Anatomical (if no clear type is found anatomical is used)
    """
    # check if it is siemens
    if common.is_siemens(dicom_input):
        logger.info('Found manufacturer: SIEMENS')
        return Vendor.SIEMENS
    # check if it is ge
    if common.is_ge(dicom_input):
        logger.info('Found manufacturer: GE')
        return Vendor.GE
    # check if it is philips
    if common.is_philips(dicom_input):
        logger.info('Found manufacturer: PHILIPS')
        return Vendor.PHILIPS
    # check if it is philips
    if common.is_hitachi(dicom_input):
        logger.info('Found manufacturer: HITACHI')
        return Vendor.HITACHI
    # generic by default
    logger.info('WARNING: Assuming generic vendor conversion (ANATOMICAL)')
    return Vendor.GENERIC


def _get_first_header(dicom_directory):
    """
    Function to get the first dicom file form a directory and return the header
    Useful to determine the type of data to convert

    :param dicom_directory: directory with dicom files
    """
    # looping over all files
    for root, _, file_names in os.walk(dicom_directory):
        # go over all the files and try to read the dicom header
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            # check wither it is a dicom file
            if not common.is_dicom_file(file_path):
                continue
            # read the headers
            return pydicom.read_file(file_path,
                                     stop_before_pixels=True,
                                     force=dicom2nifti.settings.pydicom_read_force)
    # no dicom files found
    raise ConversionError('NO_DICOM_FILES_FOUND')
