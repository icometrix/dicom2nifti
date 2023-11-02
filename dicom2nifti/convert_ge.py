# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
from dicom2nifti.exceptions import ConversionError

import itertools
import os
from math import pow

import logging
import nibabel
import numpy

from pydicom.tag import Tag

import dicom2nifti.common as common
import dicom2nifti.convert_generic as convert_generic

logger = logging.getLogger(__name__)


def dicom_to_nifti(dicom_input, output_file=None):
    """
    This is the main dicom to nifti conversion fuction for ge images.
    As input ge images are required. It will then determine the type of images and do the correct conversion

    Examples: See unit test

    :param output_file: the filepath to the output nifti file
    :param dicom_input: list with dicom objects
    """
    assert common.is_ge(dicom_input)

    # remove duplicate slices based on position and data
    dicom_input = convert_generic.remove_duplicate_slices(dicom_input)

    # remove localizers based on image type
    dicom_input = convert_generic.remove_localizers_by_imagetype(dicom_input)

    # remove_localizers based on image orientation (only valid if slicecount is validated)
    dicom_input = convert_generic.remove_localizers_by_orientation(dicom_input)

    logger.info('Reading and sorting dicom files')
    grouped_dicoms = convert_generic.get_grouped_dicoms(dicom_input)

    if convert_generic.is_4d(grouped_dicoms):
        logger.info('Found sequence type: 4D')
        return _four_d_to_nifti(grouped_dicoms, output_file)

    logger.info('Assuming anatomical data')
    return convert_generic.dicom_to_nifti(dicom_input, output_file)


def _is_diffusion_imaging(grouped_dicoms):
    """
    Use this function to detect if a dicom series is a ge dti dataset
    NOTE: We already assume this is a 4D dataset
    """
    # we already assume 4D images as input

    # check if contains dti bval information
    bval_tag = Tag(0x0043, 0x1039)  # put this there as this is a slow step and used a lot
    found_bval = False
    for header in list(itertools.chain.from_iterable(grouped_dicoms)):
        if bval_tag in header and int(header[bval_tag].value[0]) != 0:
            found_bval = True
            break
    if not found_bval:
        return False

    return True


def _four_d_to_nifti(grouped_dicoms, output_file):
    """
    This function will convert ge 4d series to a nifti
    """

    # Create mosaic block
    result = convert_generic.four_d_to_nifti(grouped_dicoms, output_file)

    if _is_diffusion_imaging(grouped_dicoms):
        bval_file = None
        bvec_file = None
        # Create the bval en bevec files
        if output_file is not None:
            base_path = os.path.dirname(output_file)
            base_name = os.path.splitext(os.path.splitext(os.path.basename(output_file))[0])[0]

            logger.info('Creating bval en bvec files')
            bval_file = '%s/%s.bval' % (base_path, base_name)
            bvec_file = '%s/%s.bvec' % (base_path, base_name)
        bval, bvec = _create_bvals_bvecs(grouped_dicoms, bval_file, bvec_file)
        return {
            'NII_FILE': output_file,
            'BVAL_FILE': bval_file,
            'BVEC_FILE': bvec_file,
            'NII': result['NII'],
            'BVAL': bval,
            'BVEC': bvec,
            'MAX_SLICE_INCREMENT': result['MAX_SLICE_INCREMENT']
        }
    return result


def _get_bvals_bvecs(grouped_dicoms):
    """
    Write the bvals from the sorted dicom files to a bval file
    """
    # loop over all timepoints and create a list with all bvals and bvecs
    bvals = numpy.zeros([len(grouped_dicoms)], dtype=numpy.int32)
    bvecs = numpy.zeros([len(grouped_dicoms), 3])

    for group_index in range(0, len(grouped_dicoms)):
        dicom_ = grouped_dicoms[group_index][0]
        # 0019:10bb: Diffusion X
        # 0019:10bc: Diffusion Y
        # 0019:10bd: Diffusion Z
        # 0043:1039: B-values (4 values, 1st value is actual B value)

        # bval can be stored both in string as number format in dicom so implement both
        # some workarounds needed for implicit transfer syntax to work
        if isinstance(dicom_[Tag(0x0043, 0x1039)].value, str):  # this works for python2.7
            original_bval = float(dicom_[Tag(0x0043, 0x1039)].value.split('\\')[0])
        elif isinstance(dicom_[Tag(0x0043, 0x1039)].value, bytes):  # this works for python3.o
            original_bval = float(dicom_[Tag(0x0043, 0x1039)].value.decode("utf-8").split('\\')[0])
        else:
            original_bval = dicom_[Tag(0x0043, 0x1039)][0]
        original_bvec = numpy.array([0, 0, 0], dtype=numpy.float32)
        original_bvec[0] = -float(dicom_[Tag(0x0019, 0x10bb)].value)  # invert based upon mricron output
        original_bvec[1] = float(dicom_[Tag(0x0019, 0x10bc)].value)
        original_bvec[2] = float(dicom_[Tag(0x0019, 0x10bd)].value)

        # Add calculated B Value
        if original_bval != 0:  # only normalize if there is a value
            corrected_bval = original_bval * pow(numpy.linalg.norm(original_bvec), 2)
            if numpy.linalg.norm(original_bvec) != 0:
                normalized_bvec = original_bvec / numpy.linalg.norm(original_bvec)
            else:
                normalized_bvec = original_bvec
        else:
            corrected_bval = original_bval
            normalized_bvec = original_bvec

        bvals[group_index] = int(round(corrected_bval))  # we want the original numbers back as in the protocol
        bvecs[group_index, :] = normalized_bvec

    return bvals, bvecs


def _create_bvals_bvecs(grouped_dicoms, bval_file, bvec_file):
    """
    Write the bvals from the sorted dicom files to a bval file
    """

    # get the bvals and bvecs
    bvals, bvecs = _get_bvals_bvecs(grouped_dicoms)

    # save the found bvecs to the file
    common.write_bval_file(bvals, bval_file)
    common.write_bvec_file(bvecs, bvec_file)

    return bvals, bvecs
