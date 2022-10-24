# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import os
import traceback

import logging
import nibabel
import numpy

import pydicom.config as pydicom_config
from pydicom.tag import Tag

import dicom2nifti.common as common
import dicom2nifti.settings as settings
import dicom2nifti.convert_generic as convert_generic
from dicom2nifti.exceptions import ConversionError, ConversionValidationError

pydicom_config.enforce_valid_values = False
logger = logging.getLogger(__name__)

def dicom_to_nifti(dicom_input, output_file=None):
    """
    This is the main dicom to nifti conversion fuction for philips images.
    As input philips images are required. It will then determine the type of images and do the correct conversion

    Examples: See unit test

    :param output_file: file path to the output nifti
    :param dicom_input: directory with dicom files for 1 scan
    """

    assert common.is_philips(dicom_input)

    # remove duplicate slices based on position and data
    dicom_input = convert_generic.remove_duplicate_slices(dicom_input)

    # remove localizers based on image type
    dicom_input = convert_generic.remove_localizers_by_imagetype(dicom_input)

    # remove_localizers based on image orientation (only valid if slicecount is validated)
    dicom_input = convert_generic.remove_localizers_by_orientation(dicom_input)

    # if no dicoms remain raise exception
    if not dicom_input:
        raise ConversionValidationError('TOO_FEW_SLICES/LOCALIZER')

    if common.is_multiframe_dicom(dicom_input):
        _assert_explicit_vr(dicom_input)
        logger.info('Found multiframe dicom')
        if _is_multiframe_4d(dicom_input):
            logger.info('Found sequence type: MULTIFRAME 4D')
            return _multiframe_to_nifti(dicom_input, output_file)

        if _is_multiframe_anatomical(dicom_input):
            logger.info('Found sequence type: MULTIFRAME ANATOMICAL')
            return convert_generic.multiframe_to_nifti(dicom_input, output_file)
    else:
        logger.info('Found singleframe dicom')
        grouped_dicoms = _get_grouped_dicoms(dicom_input)
        if _is_singleframe_4d(dicom_input):
            logger.info('Found sequence type: SINGLEFRAME 4D')
            return _singleframe_to_nifti(grouped_dicoms, output_file)

    logger.info('Assuming anatomical data')
    return convert_generic.dicom_to_nifti(dicom_input, output_file)


def _assert_explicit_vr(dicom_input):
    """
    Assert that explicit vr is used
    """
    if settings.validate_multiframe_implicit:
        header = dicom_input[0]
        if header.file_meta[0x0002, 0x0010].value == '1.2.840.10008.1.2':
            raise ConversionError('IMPLICIT_VR_ENHANCED_DICOM')


def _is_multiframe_diffusion_imaging(dicom_input):
    """
    Use this function to detect if a dicom series is a philips multiframe dti dataset
    NOTE: We already assue this is a 4D dataset as input
    """
    header = dicom_input[0]

    if "PerFrameFunctionalGroupsSequence" not in header:
        return False

    # check if there is diffusion info in the frame
    found_diffusion = False
    diffusion_tag = Tag(0x0018, 0x9117)
    for frame in header.PerFrameFunctionalGroupsSequence:
        if diffusion_tag in frame:
            found_diffusion = True
            break
    if not found_diffusion:
        return False

    return True


def _is_multiframe_4d(dicom_input):
    """
    Use this function to detect if a dicom series is a philips multiframe 4D dataset
    """
    # check if it is multi frame dicom
    if not common.is_multiframe_dicom(dicom_input):
        return False

    number_of_stacks, _ = common.multiframe_get_stack_count(dicom_input)
    if number_of_stacks <= 1:
        return False

    return True


def _is_multiframe_anatomical(dicom_input):
    """
    Use this function to detect if a dicom series is a philips multiframe anatomical dataset
    NOTE: Only the first slice will be checked so you can only provide an already sorted dicom directory
    (containing one series)
    """
    # check if it is multi frame dicom
    if not common.is_multiframe_dicom(dicom_input):
        return False

    number_of_stacks, _ = common.multiframe_get_stack_count(dicom_input)

    if number_of_stacks > 1:
        return False

    return True


def _is_singleframe_4d(dicom_input):
    """
    Use this function to detect if a dicom series is a philips singleframe 4D dataset
    """
    header = dicom_input[0]

    # check if there are stack information
    slice_number_mr_tag = Tag(0x2001, 0x100a)
    if slice_number_mr_tag not in header:
        return False

    # check if there are multiple timepoints
    grouped_dicoms = _get_grouped_dicoms(dicom_input)
    if len(grouped_dicoms) <= 1:
        return False

    return True


def _is_singleframe_diffusion_imaging(grouped_dicoms):
    """
    Use this function to detect if a dicom series is a philips singleframe dti dataset
    NOTE: We already assume singleframe 4D input
    """
    # check that there is bval information
    if _is_bval_type_b(grouped_dicoms):
        return True
    if _is_bval_type_a(grouped_dicoms):
        return True

    return False


def _is_bval_type_a(grouped_dicoms):
    """
    Check if the bvals are stored in the first of 2 currently known ways for single frame dti
    """
    bval_tag = Tag(0x2001, 0x1003)
    bvec_x_tag = Tag(0x2005, 0x10b0)
    bvec_y_tag = Tag(0x2005, 0x10b1)
    bvec_z_tag = Tag(0x2005, 0x10b2)
    for group in grouped_dicoms:
        if bvec_x_tag in group[0] and _is_float(common.get_fl_value(group[0][bvec_x_tag])) and \
                bvec_y_tag in group[0] and _is_float(common.get_fl_value(group[0][bvec_y_tag])) and \
                bvec_z_tag in group[0] and _is_float(common.get_fl_value(group[0][bvec_z_tag])) and \
                bval_tag in group[0] and _is_float(common.get_fl_value(group[0][bval_tag])) and \
                common.get_fl_value(group[0][bval_tag]) != 0:
            return True
    return False


def _is_bval_type_b(grouped_dicoms):
    """
    Check if the bvals are stored in the second of 2 currently known ways for single frame dti
    """
    bval_tag = Tag(0x0018, 0x9087)
    bvec_tag = Tag(0x0018, 0x9089)
    for group in grouped_dicoms:
        if bvec_tag in group[0] and bval_tag in group[0]:
            bvec = common.get_fd_array_value(group[0][bvec_tag], 3)
            bval = common.get_fd_value(group[0][bval_tag])
            if _is_float(bvec[0]) and _is_float(bvec[1]) and _is_float(bvec[2]) and _is_float(bval) and bval != 0:
                return True
    return False


def _is_float(value):
    """
    Check if float
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def _multiframe_to_nifti(dicom_input, output_file):
    """
    This function will convert philips 4D or anatomical multiframe series to a nifti
    """

    # Read the multiframe dicom file
    logger.info('Read dicom file')
    multiframe_dicom = dicom_input[0]

    # Create mosaic block
    logger.info('Creating data block')
    full_block = common.multiframe_to_block(multiframe_dicom)

    logger.info('Creating affine')

    # Create the nifti header info
    affine, max_slice_increment = common.multiframe_create_affine([multiframe_dicom], full_block)
    logger.info('Creating nifti')

    # Convert to nifti
    if full_block.ndim > 3:  # do not squeeze single slice data
        full_block = full_block.squeeze()
    nii_image = nibabel.Nifti1Image(full_block, affine)
    try:
        timing_parameters = multiframe_dicom.SharedFunctionalGroupsSequence[0].MRTimingAndRelatedParametersSequence[0]
        first_frame = multiframe_dicom[Tag(0x5200, 0x9230)][0]
        common.set_tr_te(nii_image, float(timing_parameters.RepetitionTime),
                         float(first_frame.MREchoSequence[0].EchoTime))
    except:
        logger.info('Unable to set timing info')

    # Save to disk
    if output_file is not None:
        logger.info('Saving nifti to disk %s' % output_file)
        nii_image.header.set_slope_inter(1, 0)
        nii_image.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
        nii_image.to_filename(output_file)

    if _is_multiframe_diffusion_imaging(dicom_input):
        bval_file = None
        bvec_file = None
        if output_file is not None:
            # Create the bval en bvec files
            base_path = os.path.dirname(output_file)
            base_name = os.path.splitext(os.path.splitext(os.path.basename(output_file))[0])[0]
            logger.info('Creating bval en bvec files')
            bval_file = '%s/%s.bval' % (base_path, base_name)
            bvec_file = '%s/%s.bvec' % (base_path, base_name)
        bval, bvec, bval_file, bvec_file = _create_bvals_bvecs(multiframe_dicom, bval_file, bvec_file, nii_image,
                                                               output_file)

        return {'NII_FILE': output_file,
                'BVAL_FILE': bval_file,
                'BVEC_FILE': bvec_file,
                'NII': nii_image,
                'BVAL': bval,
                'BVEC': bvec}

    return {'NII_FILE': output_file,
            'NII': nii_image,
            'MAX_SLICE_INCREMENT': max_slice_increment}


def _singleframe_to_nifti(grouped_dicoms, output_file):
    """
    This function will convert a philips singleframe series to a nifti
    """

    # Create mosaic block
    logger.info('Creating data block')
    full_block = _singleframe_to_block(grouped_dicoms)

    logger.info('Creating affine')
    # Create the nifti header info
    affine, slice_increment = common.create_affine(grouped_dicoms[0])

    logger.info('Creating nifti')
    # Convert to nifti
    if full_block.ndim > 3:  # do not squeeze single slice data
        full_block = full_block.squeeze()
    nii_image = nibabel.Nifti1Image(full_block, affine)
    common.set_tr_te(nii_image, float(grouped_dicoms[0][0].RepetitionTime), float(grouped_dicoms[0][0].EchoTime))

    if output_file is not None:
        # Save to disk
        logger.info('Saving nifti to disk %s' % output_file)
        nii_image.header.set_slope_inter(1, 0)
        nii_image.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
        nii_image.to_filename(output_file)

    if _is_singleframe_diffusion_imaging(grouped_dicoms):
        bval_file = None
        bvec_file = None
        # Create the bval en bvec files
        if output_file is not None:
            base_name = os.path.splitext(output_file)[0]
            if base_name.endswith('.nii'):
                base_name = os.path.splitext(base_name)[0]

            logger.info('Creating bval en bvec files')
            bval_file = '%s.bval' % base_name
            bvec_file = '%s.bvec' % base_name
        nii_image, bval, bvec, bval_file, bvec_file = _create_singleframe_bvals_bvecs(grouped_dicoms,
                                                                                      bval_file,
                                                                                      bvec_file,
                                                                                      nii_image,
                                                                                      output_file)

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


def _singleframe_to_block(grouped_dicoms):
    """
    Generate a full datablock containing all timepoints
    """
    # For each slice / mosaic create a data volume block
    data_blocks = []
    for index in range(0, len(grouped_dicoms)):
        logger.info('Creating block %s of %s' % (index + 1, len(grouped_dicoms)))
        current_block = _stack_to_block(grouped_dicoms[index])
        current_block = current_block[:, :, :, numpy.newaxis]
        data_blocks.append(current_block)

    try:
        full_block = numpy.concatenate(data_blocks, axis=3)
    except:
        traceback.print_exc()
        raise ConversionError("MISSING_DICOM_FILES")

    # Apply the rescaling if needed
    common.apply_scaling(full_block, grouped_dicoms[0][0])

    return full_block


def _stack_to_block(timepoint_dicoms):
    """
    Convert a mosaic slice to a block of data by reading the headers, splitting the mosaic and appending
    """
    return common.get_volume_pixeldata(timepoint_dicoms)


def _get_grouped_dicoms(dicom_input):
    """
    Search all dicoms in the dicom directory, sort and validate them

    fast_read = True will only read the headers not the data
    """
    # if all dicoms have an instance number try sorting by instance number else by position
    if [d for d in dicom_input if 'InstanceNumber' in d]:
        dicoms = sorted(dicom_input, key=lambda x: x.InstanceNumber)
    else:
        dicoms = common.sort_dicoms(dicom_input)
    # now group per stack
    grouped_dicoms = [[]]  # list with first element a list
    timepoint_index = 0
    previous_stack_position = -1

    # loop over all sorted dicoms
    stack_position_tag = Tag(0x2001, 0x100a)  # put this there as this is a slow step and used a lot
    for index in range(0, len(dicoms)):
        dicom_ = dicoms[index]
        stack_position = 0
        if stack_position_tag in dicom_:
            stack_position = common.get_is_value(dicom_[stack_position_tag])
        if previous_stack_position == stack_position:
            # if the stack number is the same we move to the next timepoint
            timepoint_index += 1
            if len(grouped_dicoms) <= timepoint_index:
                grouped_dicoms.append([])
        else:
            # if it changes move back to the first timepoint
            timepoint_index = 0
        grouped_dicoms[timepoint_index].append(dicom_)
        previous_stack_position = stack_position

    return grouped_dicoms


def _create_bvals_bvecs(multiframe_dicom, bval_file, bvec_file, nifti, nifti_file):
    """
    Write the bvals from the sorted dicom files to a bval file
    Inspired by https://github.com/IBIC/ibicUtils/blob/master/ibicBvalsBvecs.py
    """

    # create the empty arrays
    number_of_stacks, number_of_stack_slices = common.multiframe_get_stack_count([multiframe_dicom])

    bvals = numpy.zeros([number_of_stacks], dtype=numpy.int32)
    bvecs = numpy.zeros([number_of_stacks, 3])

    # loop over all timepoints and create a list with all bvals and bvecs
    for stack_index in range(0, number_of_stacks):
        stack = multiframe_dicom[Tag(0x5200, 0x9230)][stack_index]
        if str(stack[Tag(0x0018, 0x9117)][0][Tag(0x0018, 0x9075)].value) == 'DIRECTIONAL':
            bvals[stack_index] = common.get_fd_value(stack[Tag(0x0018, 0x9117)][0][Tag(0x0018, 0x9087)])
            bvecs[stack_index, :] = common.get_fd_array_value(stack[Tag(0x0018, 0x9117)][0]
                                                              [Tag(0x0018, 0x9076)][0][Tag(0x0018, 0x9089)], 3)

    # truncate nifti if needed
    nifti, bvals, bvecs = _fix_diffusion_images(bvals, bvecs, nifti, nifti_file)

    # save the found bvecs to the file
    if numpy.count_nonzero(bvals) > 0 or numpy.count_nonzero(bvecs) > 0:
        common.write_bval_file(bvals, bval_file)
        common.write_bvec_file(bvecs, bvec_file)
    else:
        bval_file = None
        bvec_file = None
        bvals = None
        bvecs = None

    return bvals, bvecs, bval_file, bvec_file


def _fix_diffusion_images(bvals, bvecs, nifti, nifti_file):
    """
    This function will remove the last timepoint from the nifti, bvals and bvecs if the last vector is 0,0,0
    This is sometimes added at the end by philips
    """
    # if all zero continue of if the last bvec is not all zero continue
    if numpy.count_nonzero(bvecs) == 0 or not numpy.count_nonzero(bvals[-1]) == 0:
        # nothing needs to be done here
        return nifti, bvals, bvecs
    # remove last elements from bvals and bvecs
    bvals = bvals[:-1]
    bvecs = bvecs[:-1]

    # remove last elements from the nifti
    new_nifti = nibabel.Nifti1Image(common.get_nifti_data(nifti)[:, :, :, :-1].squeeze(), nifti.affine)
    new_nifti.header.set_slope_inter(1, 0)
    new_nifti.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
    new_nifti.to_filename(nifti_file)

    return new_nifti, bvals, bvecs


def _create_singleframe_bvals_bvecs(grouped_dicoms, bval_file, bvec_file, nifti, nifti_file):
    """
    Write the bvals from the sorted dicom files to a bval file
    """

    # create the empty arrays
    bvals = numpy.zeros([len(grouped_dicoms)], dtype=numpy.int32)
    bvecs = numpy.zeros([len(grouped_dicoms), 3])

    # loop over all timepoints and create a list with all bvals and bvecs
    if _is_bval_type_a(grouped_dicoms):
        bval_tag = Tag(0x2001, 0x1003)
        bvec_x_tag = Tag(0x2005, 0x10b0)
        bvec_y_tag = Tag(0x2005, 0x10b1)
        bvec_z_tag = Tag(0x2005, 0x10b2)
        for stack_index in range(0, len(grouped_dicoms)):
            bvals[stack_index] = common.get_fl_value(grouped_dicoms[stack_index][0][bval_tag])
            bvecs[stack_index, :] = [common.get_fl_value(grouped_dicoms[stack_index][0][bvec_x_tag]),
                                     common.get_fl_value(grouped_dicoms[stack_index][0][bvec_y_tag]),
                                     common.get_fl_value(grouped_dicoms[stack_index][0][bvec_z_tag])]
    elif _is_bval_type_b(grouped_dicoms):
        bval_tag = Tag(0x0018, 0x9087)
        bvec_tag = Tag(0x0018, 0x9089)
        for stack_index in range(0, len(grouped_dicoms)):
            bvals[stack_index] = common.get_fd_value(grouped_dicoms[stack_index][0][bval_tag])
            bvecs[stack_index, :] = common.get_fd_array_value(grouped_dicoms[stack_index][0][bvec_tag], 3)

    # truncate nifti if needed
    nifti, bvals, bvecs = _fix_diffusion_images(bvals, bvecs, nifti, nifti_file)

    # save the found bvecs to the file
    if numpy.count_nonzero(bvals) > 0 or numpy.count_nonzero(bvecs) > 0:
        common.write_bval_file(bvals, bval_file)
        common.write_bvec_file(bvecs, bvec_file)
    else:
        bval_file = None
        bvec_file = None
        bvals = None
        bvecs = None
    return nifti, bvals, bvecs, bval_file, bvec_file
