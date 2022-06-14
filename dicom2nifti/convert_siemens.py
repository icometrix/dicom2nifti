# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import os
import re
import traceback

import logging
from math import ceil, sqrt

import nibabel
import numpy

from pydicom.tag import Tag

import dicom2nifti.common as common
import dicom2nifti.convert_generic as convert_generic
from dicom2nifti.exceptions import ConversionValidationError, ConversionError

logger = logging.getLogger(__name__)


# Disable this warning as there is not reason for an init class in an enum
# pylint: disable=w0232, r0903, E1101


class MosaicType(object):
    """
    Enum for the possible types of mosaic data
    """
    ASCENDING = 1
    DESCENDING = 2


# pylint: enable=w0232, r0903


def dicom_to_nifti(dicom_input, output_file=None):
    """
    This is the main dicom to nifti conversion function for ge images.
    As input ge images are required. It will then determine the type of images and do the correct conversion

    :param output_file: filepath to the output nifti
    :param dicom_input: directory with dicom files for 1 scan
    """

    assert common.is_siemens(dicom_input)

    # remove duplicate slices based on position and data
    dicom_input = convert_generic.remove_duplicate_slices(dicom_input)

    # remove localizers based on image type
    dicom_input = convert_generic.remove_localizers_by_imagetype(dicom_input)

    # remove_localizers based on image orientation (only valid if slicecount is validated)
    dicom_input = convert_generic.remove_localizers_by_orientation(dicom_input)

    # if no dicoms remain raise exception
    if not dicom_input:
        raise ConversionValidationError('TOO_FEW_SLICES/LOCALIZER')

    if _is_4d(dicom_input):
        logger.info('Found sequence type: MOSAIC 4D')
        return _mosaic_4d_to_nifti(dicom_input, output_file)

    if common.is_multiframe_dicom(dicom_input):
        logger.info('Found sequence type: MULTIFRAME')
        return convert_generic.multiframe_to_nifti(dicom_input, output_file)

    grouped_dicoms = _classic_get_grouped_dicoms(dicom_input)
    if _is_classic_4d(grouped_dicoms):
        logger.info('Found sequence type: CLASSIC 4D')
        return _classic_4d_to_nifti(grouped_dicoms, output_file)

    logger.info('Assuming anatomical data')
    return convert_generic.dicom_to_nifti(dicom_input, output_file)


def _is_mosaic(dicom_input):
    """
    Use this function to detect if a dicom series is a siemens 4d dataset
    NOTE: Only the first slice will be checked so you can only provide an already sorted dicom directory
    (containing one series)
    """
    # for grouped dicoms
    if type(dicom_input) is list and type(dicom_input[0]) is list:
        header = dicom_input[0][0]
    else:  # all the others
        header = dicom_input[0]

    # check if image type contains m and mosaic
    if 'ImageType' not in header or 'MOSAIC' not in header.ImageType:
        return False

    if 'AcquisitionMatrix' not in header or header.AcquisitionMatrix is None:
        return False

    return True


def _is_4d(dicom_input):
    """
    Use this function to detect if a dicom series is a siemens 4d dataset
    NOTE: Only the first slice will be checked so you can only provide an already sorted dicom directory
    (containing one series)
    """
    if not _is_mosaic(dicom_input):
        return False

    return True


def _is_classic_4d(grouped_dicoms):
    """
    Use this function to detect if a dicom series is a siemens 4d dataset
    NOTE: Only the first slice will be checked so you can only provide an already sorted dicom directory
    (containing one series)
    """

    if _is_mosaic(grouped_dicoms):
        return False

    if len(grouped_dicoms) <= 1:
        return False

    return True


def _is_diffusion_imaging(header_input):
    """
    Use this function to detect if a dicom series is a siemens dti dataset
    NOTE: Only the first slice will be checked so you can only provide an already sorted dicom directory
    (containing one series)
    """

    # bval and bvec should be present
    if Tag(0x0019, 0x100c) not in header_input:
        return False

    return True


def _mosaic_4d_to_nifti(dicom_input, output_file):
    """
    This function will convert siemens 4d series to a nifti
    Some inspiration on which fields can be used was taken from
    http://slicer.org/doc/html/DICOMDiffusionVolumePlugin_8py_source.html
    """
    # Get the sorted mosaics
    logger.info('Sorting dicom slices')
    sorted_mosaics = _get_sorted_mosaics(dicom_input)
    common.validate_orientation(sorted_mosaics)

    # Create mosaic block
    logger.info('Creating data block')
    full_block = _mosaic_get_full_block(sorted_mosaics)

    logger.info('Creating affine')
    # Create the nifti header info
    affine = _create_affine_siemens_mosaic(dicom_input)
    logger.info('Creating nifti')
    # Convert to nifti
    if full_block.ndim > 3:
        full_block = full_block.squeeze()
    nii_image = nibabel.Nifti1Image(full_block, affine)
    common.set_tr_te(nii_image, float(sorted_mosaics[0].RepetitionTime), float(sorted_mosaics[0].EchoTime))
    logger.info('Saving nifti to disk')
    # Save to disk
    if output_file is not None:
        nii_image.header.set_slope_inter(1, 0)
        nii_image.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
        nii_image.to_filename(output_file)

    if _is_diffusion_imaging(dicom_input[0]):
        # Create the bval en bvec files
        logger.info('Creating bval en bvec')
        bval_file = None
        bvec_file = None
        if output_file is not None:
            base_path = os.path.dirname(output_file)
            base_name = os.path.splitext(os.path.splitext(os.path.basename(output_file))[0])[0]
            logger.info('Saving bval en bvec files')
            bval_file = '%s/%s.bval' % (base_path, base_name)
            bvec_file = '%s/%s.bvec' % (base_path, base_name)
        bvals = _create_bvals(sorted_mosaics, bval_file)
        bvecs = _create_bvecs(sorted_mosaics, bvec_file)

        return {'NII_FILE': output_file,
                'BVAL_FILE': bval_file,
                'BVEC_FILE': bvec_file,
                'NII': nii_image,
                'BVAL': bvals,
                'BVEC': bvecs}

    return {'NII_FILE': output_file,
            'NII': nii_image}


def _classic_4d_to_nifti(grouped_dicoms, output_file):
    """
    This function will convert siemens 4d series to a nifti
    Some inspiration on which fields can be used was taken from
    http://slicer.org/doc/html/DICOMDiffusionVolumePlugin_8py_source.html
    """
    # Get the sorted mosaics
    all_dicoms = [i for sl in grouped_dicoms for i in sl]  # combine into 1 list for validating
    common.validate_orientation(all_dicoms)

    # Create mosaic block
    logger.info('Creating data block')
    full_block = _classic_get_full_block(grouped_dicoms)

    logger.info('Creating affine')
    # Create the nifti header info
    affine, slice_increment = common.create_affine(grouped_dicoms[0])

    logger.info('Creating nifti')
    # Convert to nifti
    if full_block.ndim > 3:  # do not squeeze single slice data
        full_block = full_block.squeeze()
    nii_image = nibabel.Nifti1Image(full_block, affine)
    common.set_tr_te(nii_image, float(grouped_dicoms[0][0].RepetitionTime), float(grouped_dicoms[0][0].EchoTime))
    logger.info('Saving nifti to disk')
    # Save to disk
    if output_file is not None:
        nii_image.header.set_slope_inter(1, 0)
        nii_image.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
        nii_image.to_filename(output_file)

    if _is_diffusion_imaging(grouped_dicoms[0][0]):
        logger.info('Creating bval en bvec')
        bval_file = None
        bvec_file = None
        if output_file is not None:
            base_path = os.path.dirname(output_file)
            base_name = os.path.splitext(os.path.splitext(os.path.basename(output_file))[0])[0]
            logger.info('Creating bval en bvec files')
            bval_file = '%s/%s.bval' % (base_path, base_name)
            bvec_file = '%s/%s.bvec' % (base_path, base_name)

        bval = _create_bvals(grouped_dicoms, bval_file)
        bvec = _create_bvecs(grouped_dicoms, bvec_file)

        return {'NII_FILE': output_file,
                'BVAL_FILE': bval_file,
                'BVEC_FILE': bvec_file,
                'NII': nii_image,
                'BVAL': bval,
                'BVEC': bvec,
                'MAX_SLICE_INCREMENT': slice_increment}

    return {'NII_FILE': output_file,
            'NII': nii_image,
            'MAX_SLICE_INCREMENT': slice_increment}

def _classic_get_grouped_dicoms(dicom_input):
    """
    Search all dicoms in the dicom directory, sort and validate them

    fast_read = True will only read the headers not the data
    """

    # Order all dicom files by InstanceNumber
    dicoms = sorted(dicom_input, key=lambda x: x.InstanceNumber)

    # now group per stack
    grouped_dicoms = [[]]  # list with first element a list
    stack_index = 0

    # loop over all sorted dicoms and sort them by stack
    # for this we use the position and direction of the slices so we can detect a new stack easily
    previous_position = None
    previous_direction = None
    for dicom_ in dicoms:
        current_direction = None
        # if the stack number decreases we moved to the next stack
        if previous_position is not None:
            current_direction = numpy.array(dicom_.ImagePositionPatient) - previous_position
            current_direction = current_direction / numpy.linalg.norm(current_direction)
        if current_direction is not None and \
                previous_direction is not None and \
                not numpy.allclose(current_direction, previous_direction, rtol=0.05, atol=0.05):
            previous_position = numpy.array(dicom_.ImagePositionPatient)
            previous_direction = None
            stack_index += 1
        else:
            previous_position = numpy.array(dicom_.ImagePositionPatient)
            previous_direction = current_direction

        if stack_index >= len(grouped_dicoms):
            grouped_dicoms.append([])
        grouped_dicoms[stack_index].append(dicom_)

    return grouped_dicoms

# old function that was replaced by the new one for icometrix/dicom2nifti#70 will keep it for now
# def _classic_get_grouped_dicoms(dicom_input):
#     """
#     Search all dicoms in the dicom directory, sort and validate them
#
#     fast_read = True will only read the headers not the data
#     """
#     # Loop overall files and build dict
#     # Order all dicom files by InstanceNumber
#     if [d for d in dicom_input if 'InstanceNumber' in d]:
#         dicoms = sorted(dicom_input, key=lambda x: x.InstanceNumber)
#     else:
#         dicoms = common.sort_dicoms(dicom_input)
#
#     # now group per stack
#     grouped_dicoms = []
#
#     # loop over all sorted dicoms
#     stack_position_tag = Tag(0x0020, 0x0012)  # in this case it is the acquisition number
#     for index in range(0, len(dicoms)):
#         dicom_ = dicoms[index]
#         if stack_position_tag not in dicom_:
#             stack_index = 0
#         else:
#             stack_index = dicom_[stack_position_tag].value - 1
#         while len(grouped_dicoms) <= stack_index:
#             grouped_dicoms.append([])
#         grouped_dicoms[stack_index].append(dicom_)
#
#     return grouped_dicoms


def _classic_get_full_block(grouped_dicoms):
    """
    Generate a full datablock containing all timepoints
    """
    # For each slice / mosaic create a data volume block
    data_blocks = []
    for index in range(0, len(grouped_dicoms)):
        logger.info('Creating block %s of %s' % (index + 1, len(grouped_dicoms)))
        data_blocks.append(_classic_timepoint_to_block(grouped_dicoms[index]))

    # Add the data_blocks together to one 4d block
    size_x = numpy.shape(data_blocks[0])[0]
    size_y = numpy.shape(data_blocks[0])[1]
    size_z = numpy.shape(data_blocks[0])[2]
    size_t = len(data_blocks)
    full_block = numpy.zeros((size_x, size_y, size_z, size_t), dtype=data_blocks[0].dtype)
    for index in range(0, size_t):
        full_block[:, :, :, index] = data_blocks[index]

    return full_block


def _classic_timepoint_to_block(timepoint_dicoms):
    """
    Convert slices to a block of data by reading the headers and appending
    """
    # similar way of getting the block to anatomical however here we are creating the dicom series our selves
    return common.get_volume_pixeldata(timepoint_dicoms)


def _mosaic_get_full_block(sorted_mosaics):
    """
    Generate a full datablock containing all timepoints
    """
    # For each slice / mosaic create a data volume block
    data_blocks = []
    for index in range(0, len(sorted_mosaics)):
        data_blocks.append(_mosaic_to_block(sorted_mosaics[index]))

    # Add the data_blocks together to one 4d block
    size_x = numpy.shape(data_blocks[0])[0]
    size_y = numpy.shape(data_blocks[0])[1]
    size_z = numpy.shape(data_blocks[0])[2]
    size_t = len(data_blocks)
    full_block = numpy.zeros((size_x, size_y, size_z, size_t), dtype=data_blocks[0].dtype)
    for index in range(0, size_t):
        full_block[:, :, :, index] = data_blocks[index]

    # Apply the rescaling if needed
    common.apply_scaling(full_block, sorted_mosaics[0])

    return full_block


def _get_sorted_mosaics(dicom_input):
    """
    Search all mosaics in the dicom directory, sort and validate them
    """
    # Order all dicom files by acquisition number
    sorted_mosaics = sorted(dicom_input, key=lambda x: x.AcquisitionNumber)

    for index in range(0, len(sorted_mosaics) - 1):
        # Validate that there are no duplicate AcquisitionNumber
        if sorted_mosaics[index].AcquisitionNumber >= sorted_mosaics[index + 1].AcquisitionNumber:
            raise ConversionValidationError("INCONSISTENT_ACQUISITION_NUMBERS")

    return sorted_mosaics


def _get_asconv_headers(mosaic):
    """
    Getter for the asconv headers (asci header info stored in the dicom)
    """
    asconv_headers = re.findall(r'### ASCCONV BEGIN(.*)### ASCCONV END ###',
                                mosaic[Tag(0x0029, 0x1020)].value.decode(encoding='ISO-8859-1'),
                                re.DOTALL)[0]

    return asconv_headers


def _get_mosaic_type(mosaic):
    """
    Check the extra ascconv headers for the mosaic type based on the slice position
    We always assume axial in this case
    the implementation resembles the last lines of documentation in
    https://www.icts.uiowa.edu/confluence/plugins/viewsource/viewpagesrc.action?pageId=54756326
    """

    ascconv_headers = _get_asconv_headers(mosaic)

    try:
        size = int(re.findall(r'sSliceArray\.lSize\s*=\s*(\d+)', ascconv_headers)[0])

        # get the locations of the slices
        slice_location = [None] * size
        for index in range(size):
            axial_result = re.findall(
                r'sSliceArray\.asSlice\[%s\]\.sPosition\.dTra\s*=\s*([-+]?[0-9]*\.?[0-9]*)' % index,
                ascconv_headers)
            if len(axial_result) > 0:
                axial = float(axial_result[0])
            else:
                axial = 0.0
            slice_location[index] = axial

        # should we invert (https://www.icts.uiowa.edu/confluence/plugins/viewsource/viewpagesrc.action?pageId=54756326)
        invert = False
        invert_result = re.findall(r'sSliceArray\.ucImageNumbTra\s*=\s*([-+]?0?x?[0-9]+)', ascconv_headers)
        if len(invert_result) > 0:
            invert_value = int(invert_result[0], 16)
            if invert_value >= 0:
                invert = True

        # return the correct slice types
        if slice_location[0] <= slice_location[1]:
            if not invert:
                return MosaicType.ASCENDING
            else:
                return MosaicType.DESCENDING
        else:
            if not invert:
                return MosaicType.DESCENDING
            else:
                return MosaicType.ASCENDING
    except:
        traceback.print_exc()
        raise ConversionError("MOSAIC_TYPE_NOT_SUPPORTED")


def _get_mosaic_block_dimensions(mosaic):
    """
    # get the dimensions of one tile format is 64p*64 or 80*80 or something similar
    :param mosaic:
    :return: (rows, columns, nr of slices)
    """
    ascconv_headers = _get_asconv_headers(mosaic)

    size_z = int(re.findall(r'sSliceArray\.lSize\s*=\s*(\d+)', ascconv_headers)[0])

    # get the number of rows and columns
    number_x = number_y = ceil(sqrt(size_z))
    size_x = int(mosaic.Columns / number_x)
    size_y = int(mosaic.Rows / number_y)
    return number_x, number_y, size_x, size_y, size_z

def _mosaic_to_block(mosaic):
    """
    Convert a mosaic slice to a block of data by reading the headers, splitting the mosaic and appending
    """
    # get the mosaic type
    mosaic_type = _get_mosaic_type(mosaic)
    number_x, number_y, size_x, size_y, size_z = _get_mosaic_block_dimensions(mosaic)

    # recreate 2d slice
    data_2d = mosaic.pixel_array
    # create 3d block
    data_3d = numpy.zeros((size_z, size_y, size_x), dtype=data_2d.dtype)
    # fill 3d block by taking the correct portions of the slice
    z_index = 0
    for y_index in range(0, number_y):
        if z_index >= size_z:
            break
        for x_index in range(0, number_x):
            if mosaic_type == MosaicType.ASCENDING:
                data_3d[z_index, :, :] = data_2d[size_y * y_index:size_y * (y_index + 1),
                                         size_x * x_index:size_x * (x_index + 1)]
            else:
                data_3d[size_z - (z_index + 1), :, :] = data_2d[size_y * y_index:size_y * (y_index + 1),
                                                         size_x * x_index:size_x * (x_index + 1)]
            z_index += 1
            if z_index >= size_z:
                break
    # reorient the block of data
    data_3d = numpy.transpose(data_3d, (2, 1, 0))

    return data_3d


def _create_affine_siemens_mosaic(dicom_input):
    """
    Function to create the affine matrix for a siemens mosaic dataset
    This will work for siemens dti and 4d if in mosaic format
    """
    # read dicom series with pds
    dicom_header = dicom_input[0]

    # Create affine matrix (http://nipy.sourceforge.net/nibabel/dicom/dicom_orientation.html#dicom-slice-affine)
    image_orient1 = numpy.array(dicom_header.ImageOrientationPatient)[0:3]
    image_orient2 = numpy.array(dicom_header.ImageOrientationPatient)[3:6]

    normal = numpy.cross(image_orient1, image_orient2)

    delta_r = float(dicom_header.PixelSpacing[0])
    delta_c = float(dicom_header.PixelSpacing[1])

    image_pos = dicom_header.ImagePositionPatient

    delta_s = dicom_header.SpacingBetweenSlices
    affine = numpy.array(
        [[-image_orient1[0] * delta_c, -image_orient2[0] * delta_r, -delta_s * normal[0], -image_pos[0]],
         [-image_orient1[1] * delta_c, -image_orient2[1] * delta_r, -delta_s * normal[1], -image_pos[1]],
         [image_orient1[2] * delta_c, image_orient2[2] * delta_r, delta_s * normal[2], image_pos[2]],
         [0, 0, 0, 1]])

    # The ImagePositionPatient in mosaic dicom refers to the top left voxel of the mosaic rather than the center
    # of the first (unpacked) slice. The correction is described in https://nipy.org/nibabel/dicom/dicom_mosaic.html
    _, _, size_x, size_y, _ = _get_mosaic_block_dimensions(dicom_input[0])
    affine[0:3, [3]] += numpy.dot(affine[0:3, 0:2],
                                  numpy.array([[(dicom_header.Columns - size_x) / 2],
                                               [(dicom_header.Rows - size_y) / 2]]))

    return affine


def _create_bvals(sorted_dicoms, bval_file):
    """
    Write the bvals from the sorted dicom files to a bval file
    """
    bvals = []
    for index in range(0, len(sorted_dicoms)):
        if type(sorted_dicoms[0]) is list:
            dicom_headers = sorted_dicoms[index][0]
        else:
            dicom_headers = sorted_dicoms[index]

        bvals.append(common.get_is_value(dicom_headers[Tag(0x0019, 0x100c)]))
    # save the found bvecs to the file
    common.write_bval_file(bvals, bval_file)
    return numpy.array(bvals)


def _create_bvecs(sorted_dicoms, bvec_file):
    """
    Calculate the bvecs and write the to a bvec file
    # inspired by dicom2nii from mricron
    # see  http://users.fmrib.ox.ac.uk/~robson/internal/Dicom2Nifti111.m
    """
    if type(sorted_dicoms[0]) is list:
        dicom_headers = sorted_dicoms[0][0]
    else:
        dicom_headers = sorted_dicoms[0]

    # get the patient orientation
    image_orientation = dicom_headers.ImageOrientationPatient
    read_vector = numpy.array([float(image_orientation[0]), float(image_orientation[1]), float(image_orientation[2])])
    phase_vector = numpy.array([float(image_orientation[3]), float(image_orientation[4]), float(image_orientation[5])])
    mosaic_vector = numpy.cross(read_vector, phase_vector)

    # normalize the vectors
    read_vector /= numpy.linalg.norm(read_vector)
    phase_vector /= numpy.linalg.norm(phase_vector)
    mosaic_vector /= numpy.linalg.norm(mosaic_vector)
    # create an empty array for the new bvecs
    bvecs = numpy.zeros([len(sorted_dicoms), 3])
    # for each slice calculate the new bvec
    for index in range(0, len(sorted_dicoms)):
        if type(sorted_dicoms[0]) is list:
            dicom_headers = sorted_dicoms[index][0]
        else:
            dicom_headers = sorted_dicoms[index]

        # get the bval als this is needed in some checks
        bval = common.get_is_value(dicom_headers[Tag(0x0019, 0x100c)])
        # get the bvec if it exists in the headers
        bvec = numpy.array([0, 0, 0])
        if Tag(0x0019, 0x100e) in dicom_headers:
            # in case of implicit VR the private field cannot be split into an array, we do this here
            bvec = numpy.array(common.get_fd_array_value(dicom_headers[Tag(0x0019, 0x100e)], 3))
        # if bval is 0 or the vector is 0 no projection is needed and the vector is 0,0,0
        new_bvec = numpy.array([0, 0, 0])

        if bval > 0 and not (bvec == [0, 0, 0]).all():
            # project the bvec and invert the y direction
            new_bvec = numpy.array(
                [numpy.dot(bvec, read_vector), -numpy.dot(bvec, phase_vector), numpy.dot(bvec, mosaic_vector)])
            # normalize the bvec
            new_bvec /= numpy.linalg.norm(new_bvec)
        bvecs[index, :] = new_bvec
    # save the found bvecs to the file
    common.write_bvec_file(bvecs, bvec_file)
    return numpy.array(bvecs)
