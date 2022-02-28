# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import os
import tempfile
import logging
import shutil

from .exceptions import ConversionValidationError
from .settings import Dicom2NiftiSettings as settings
from .common import get_vendor, Vendor, read_dicom_directory, is_orthogonal_nifti, is_valid_imaging_dicom
from .image_reorientation import reorient_image
from .resample import resample_single_nifti
from .convert_generic import generic_dicom_to_nifti
from .convert_siemens import siemens_dicom_to_nifti
from .convert_ge import ge_dicom_to_nifti
from .convert_philips import philips_dicom_to_nifti
from .convert_hitachi import hitachi_dicom_to_nifti

logger = logging.getLogger(__name__)


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

        dicom_input = read_dicom_directory(dicom_directory)

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
    if not is_valid_imaging_dicom(dicom_list[0]):
        raise ConversionValidationError('NON_IMAGING_DICOM_FILES')

    vendor = get_vendor(dicom_list)

    if vendor == Vendor.GENERIC:
        results = generic_dicom_to_nifti(dicom_list, output_file)
    elif vendor == Vendor.SIEMENS:
        results = siemens_dicom_to_nifti(dicom_list, output_file)
    elif vendor == Vendor.GE:
        results = ge_dicom_to_nifti(dicom_list, output_file)
    elif vendor == Vendor.PHILIPS:
        results = philips_dicom_to_nifti(dicom_list, output_file)
    elif vendor == Vendor.HITACHI:
        results = hitachi_dicom_to_nifti(dicom_list, output_file)
    else:
        raise ConversionValidationError("UNSUPPORTED_DATA")

    # do image reorientation if needed
    if reorient_nifti or settings.resample:
        results['NII'] = reorient_image(results['NII'], results['NII_FILE'])

    # resampling needs to be after reorientation
    if settings.resample:
        if not is_orthogonal_nifti(results['NII']):
            results['NII'] = resample_single_nifti(results['NII'], results['NII_FILE'])

    return results
