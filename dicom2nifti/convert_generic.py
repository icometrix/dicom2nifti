# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import logging
import nibabel
import numpy

from pydicom.tag import Tag

import dicom2nifti.common as common
import dicom2nifti.settings as settings
import dicom2nifti.resample as resample
from dicom2nifti.exceptions import ConversionError, ConversionValidationError

logger = logging.getLogger(__name__)

def get_grouped_dicoms(dicom_input):
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

def is_4d(grouped_dicoms):
    """
    Use this function to detect if a dicom series is a ge 4d dataset
    NOTE: Only the first slice will be checked so you can only provide an already sorted dicom directory
    (containing one series)
    """
    # read dicom header
    header = grouped_dicoms[0][0]

    # check if contains multiple stacks
    if len(grouped_dicoms) > 1:
        return True

    return False

def four_d_to_nifti(grouped_dicoms, output_file):
    """
    This function will convert ge 4d series to a nifti
    """

    # Create mosaic block
    logger.info('Creating data block')
    full_block = _get_full_block(grouped_dicoms)

    logger.info('Creating affine')
    # Create the nifti header info
    affine, slice_increment = common.create_affine(grouped_dicoms[0])

    logger.info('Creating nifti')
    # Convert to nifti
    nii_image = nibabel.Nifti1Image(full_block, affine)
    common.set_tr_te(nii_image, grouped_dicoms[0][0].RepetitionTime, grouped_dicoms[0][0].EchoTime)
    logger.info('Saving nifti to disk %s' % output_file)

    # Save to disk
    if output_file is not None:
        nii_image.header.set_slope_inter(1, 0)
        nii_image.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
        nii_image.to_filename(output_file)

    return {'NII_FILE': output_file,
            'NII': nii_image,
            'MAX_SLICE_INCREMENT': slice_increment}

def _get_full_block(grouped_dicoms):
    """
    Generate a full datablock containing all timepoints
    """
    # For each slice / mosaic create a data volume block
    data_blocks = []
    for index in range(0, len(grouped_dicoms)):
        logger.info('Creating block %s of %s' % (index + 1, len(grouped_dicoms)))
        data_blocks.append(_timepoint_to_block(grouped_dicoms[index]))

    # Add the data_blocks together to one 4d block
    size_x = numpy.shape(data_blocks[0])[0]
    size_y = numpy.shape(data_blocks[0])[1]
    size_z = numpy.shape(data_blocks[0])[2]
    size_t = len(data_blocks)
    full_block = numpy.zeros((size_x, size_y, size_z, size_t), dtype=data_blocks[0].dtype)
    for index in range(0, size_t):
        if full_block[:, :, :, index].shape != data_blocks[index].shape:
            logger.warning('Missing slices (slice count mismatch between timepoint %s and %s)' % (index - 1, index))
            logger.warning('---------------------------------------------------------')
            logger.warning(full_block[:, :, :, index].shape)
            logger.warning(data_blocks[index].shape)
            logger.warning('---------------------------------------------------------')
            raise ConversionError("MISSING_DICOM_FILES")
        full_block[:, :, :, index] = data_blocks[index]

    return full_block

def _timepoint_to_block(timepoint_dicoms):
    """
    Convert slices to a block of data by reading the headers and appending
    """
    # similar way of getting the block to anatomical however here we are creating the dicom series our selves
    return common.get_volume_pixeldata(timepoint_dicoms)

def multiframe_to_nifti(dicom_input, output_file):
    """
    This function will convert an anatomical dicom series to a nifti

    Examples: See unit test

    :param output_file: filepath to the output nifti
    :param dicom_input: directory with the dicom files for a single scan, or list of read in dicoms
    """
    if len(dicom_input) <= 0:
        raise ConversionError('NO_DICOM_FILES_FOUND')

    if settings.validate_slicecount:
        common.multiframe_validate_slicecount(dicom_input)
    if settings.validate_orientation:
        # validate that all slices have the same orientation
        common.multiframe_validate_orientation(dicom_input)
    if settings.validate_orthogonal:
        # validate that we have an orthogonal image (to detect gantry tilting etc)
        common.multiframe_validate_orthogonal(dicom_input)

    # validate slice increment inconsistent
    slice_increment_inconsistent = False
    if settings.validate_slice_increment:
        # validate that all slices have a consistent slice increment
        common.multiframe_validate_slice_increment(dicom_input)
    elif common.multiframe_is_slice_increment_inconsistent(dicom_input):
        slice_increment_inconsistent = True

    # if inconsistent increment and we allow resampling then do the resampling based conversion to maintain the correct geometric shape
    if slice_increment_inconsistent and settings.resample:
        raise Exception('Conversion of inconsistent slice increment with resampling not supported for mutlframe')
        # TODO add support for this if it actually exists
    # do the normal conversion
    else:
        # Get data; originally z,y,x, transposed to x,y,z
        data = common.multiframe_to_block(dicom_input[0])

        affine, max_slice_increment = common.multiframe_create_affine(dicom_input, data)

        # Convert to nifti
        if data.ndim > 3:  # do not squeeze single slice data
            data = data.squeeze()
        if dicom_input[0].PhotometricInterpretation == 'RGB':
            nii_image = create_rgba_nifti(data, affine)
        else:
            nii_image = nibabel.Nifti1Image(data, affine)

    # Set TR and TE if available
    if Tag(0x0018, 0x0080) in dicom_input[0] and Tag(0x0018, 0x0081) in dicom_input[0]:
        common.set_tr_te(nii_image, dicom_input[0].RepetitionTime, dicom_input[0].EchoTime)

    # Save to disk
    if output_file is not None:
        logger.info('Saving nifti to disk %s' % output_file)
        nii_image.header.set_slope_inter(1, 0)
        nii_image.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
        nii_image.to_filename(output_file)

    return {'NII_FILE': output_file,
            'NII': nii_image,
            'MAX_SLICE_INCREMENT': max_slice_increment}

def dicom_to_nifti(dicom_input, output_file):
    """
    This function will convert an anatomical dicom series to a nifti

    Examples: See unit test

    :param output_file: filepath to the output nifti
    :param dicom_input: directory with the dicom files for a single scan, or list of read in dicoms
    """
    if len(dicom_input) <= 0:
        raise ConversionError('NO_DICOM_FILES_FOUND')

    # remove non imaging slices based on missing pixel data
    dicom_input = remove_non_imaging_slices(dicom_input)

    # remove duplicate slices based on position and data
    dicom_input = remove_duplicate_slices(dicom_input)

    # remove localizers based on image type
    dicom_input = remove_localizers_by_imagetype(dicom_input)

    # convert
    if common.is_multiframe_dicom(dicom_input):
        logger.info('Found sequence type: MULTIFRAME')
        return multiframe_to_nifti(dicom_input, output_file)

    # if no dicoms remain we should raise exception
    if len(dicom_input) < 1:
        raise ConversionValidationError('TOO_FEW_SLICES/LOCALIZER')

    if settings.validate_slicecount:
        common.validate_slicecount(dicom_input)
        # remove_localizers based on image orientation (only valid if slicecount is validated)
        dicom_input = remove_localizers_by_orientation(dicom_input)

        # validate all the dicom files for correct orientations
        common.validate_slicecount(dicom_input)
    if settings.validate_orientation:
        # validate that all slices have the same orientation
        common.validate_orientation(dicom_input)
    if settings.validate_orthogonal:
        # validate that we have an orthogonal image (to detect gantry tilting etc)
        common.validate_orthogonal(dicom_input)

    logger.info('Reading and sorting dicom files')
    grouped_dicoms = get_grouped_dicoms(dicom_input)

    if is_4d(grouped_dicoms):
        del dicom_input
        logger.info('Found sequence type: 4D')
        return four_d_to_nifti(grouped_dicoms, output_file)

    del grouped_dicoms

    # sort the dicoms
    dicom_input = common.sort_dicoms(dicom_input)

    # validate slice increment inconsistent
    slice_increment_inconsistent = False
    if settings.validate_slice_increment:
        # validate that all slices have a consistent slice increment
        common.validate_slice_increment(dicom_input)
    elif common.is_slice_increment_inconsistent(dicom_input):
        slice_increment_inconsistent = True

    if settings.validate_instance_number:
        # validate that all slices have a consistent instance_number
        common.validate_instance_number(dicom_input)

    # if inconsistent increment and we allow resampling then do the resampling based conversion to maintain the correct geometric shape
    if slice_increment_inconsistent and settings.resample:
        nii_image, max_slice_increment = _convert_slice_incement_inconsistencies(dicom_input)
    # do the normal conversion
    else:
        # Get data; originally z,y,x, transposed to x,y,z
        data = common.get_volume_pixeldata(dicom_input)

        affine, max_slice_increment = common.create_affine(dicom_input)

        # Convert to nifti
        if data.ndim > 3:  # do not squeeze single slice data
            data = data.squeeze()
        if dicom_input[0].PhotometricInterpretation == 'RGB':
            nii_image = create_rgba_nifti(data, affine)
        else:
            nii_image = nibabel.Nifti1Image(data, affine)

    # Set TR and TE if available
    if Tag(0x0018, 0x0080) in dicom_input[0] and Tag(0x0018, 0x0081) in dicom_input[0]:
        common.set_tr_te(nii_image, dicom_input[0].RepetitionTime, dicom_input[0].EchoTime)

    # Save to disk
    if output_file is not None:
        logger.info('Saving nifti to disk %s' % output_file)
        nii_image.header.set_slope_inter(1, 0)
        nii_image.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
        nii_image.to_filename(output_file)

    return {'NII_FILE': output_file,
            'NII': nii_image,
            'MAX_SLICE_INCREMENT': max_slice_increment}


def create_rgba_nifti(rgb_data, affine):
    # ras_pos is a 4-d numpy array, with the last dim holding RGB
    shape_3d = rgb_data.shape[0:3]
    # we generate using rgb for speed data but export rgba in order for the frontend to support it
    rgba_data = numpy.full(shape_3d + (4,), 255, dtype=numpy.uint8)
    rgba_data[:, :, :, :3] = rgb_data
    rgba_dtype = numpy.dtype([('R', 'u1'), ('G', 'u1'), ('B', 'u1'), ('A', 'u1')])
    # copy used to force fresh internal structure
    rgba_data = rgba_data.copy().view(dtype=rgba_dtype).reshape(shape_3d)
    return nibabel.Nifti1Image(rgba_data, affine)


def remove_non_imaging_slices(dicoms):
    """
    Search dicoms for localizers and delete them
    """
    # Loop overall files and build dict

    filtered_dicoms = []
    # in case of multiframe this check cannot be done
    if 'ImageOrientationPatient' not in dicoms[0]:
        return dicoms
    if 'ImagePositionPatient' not in dicoms[0]:
        return dicoms

    for dicom_ in dicoms:
        if "PixelData" not in dicom_:
            logger.warning('Removing non imaging slice from series')
        else:
            filtered_dicoms.append(dicom_)
    return filtered_dicoms

def remove_duplicate_slices(dicoms):
    """
    Search dicoms for localizers and delete them
    """
    # Loop overall files and build dict

    dicoms_dict = {}
    filtered_dicoms = []
    # in case of multiframe this check cannot be done
    if 'ImageOrientationPatient' not in dicoms[0]:
        return dicoms
    if 'ImagePositionPatient' not in dicoms[0]:
        return dicoms

    for dicom_ in dicoms:
        if tuple(dicom_.ImagePositionPatient) not in dicoms_dict:
            dicoms_dict[tuple(dicom_.ImagePositionPatient)] = dicom_
            filtered_dicoms.append(dicom_)
        else:
            if numpy.array_equal(dicom_.pixel_array,
                                 dicoms_dict[tuple(dicom_.ImagePositionPatient)].pixel_array):
                logger.warning('Removing duplicate slice from series')
            else:
                filtered_dicoms.append(dicom_)
    return filtered_dicoms


def remove_localizers_by_imagetype(dicoms):
    """
    Search dicoms for localizers and delete them
    """
    # Loop overall files and build dict
    filtered_dicoms = []
    for dicom_ in dicoms:
        if 'ImageType' in dicom_ and 'LOCALIZER' in dicom_.ImageType:
            continue
        # 'Projection Image' are Localizers for CT only see MSMET-234
        if 'CT' in dicom_.Modality and 'ImageType' in dicom_ and 'PROJECTION IMAGE' in dicom_.ImageType:
            continue
        filtered_dicoms.append(dicom_)
    return filtered_dicoms


def remove_localizers_by_orientation(dicoms):
    """
    Removing localizers based on the orientation.
    This is needed as in some cases with ct data there are some localizer/projection type images that cannot
    be distiguished by the dicom headers. This is why we kick out all orientations that do not have more than 4 files
    4 is the limit anyway for converting to nifti on our case
    """
    orientations = []
    sorted_dicoms = {}

    # in case of multiframe this check cannot be done
    if 'ImageOrientationPatient' not in dicoms[0]:
        return dicoms

    # Loop overall files and build dict
    for dicom_header in dicoms:
        # Create affine matrix (http://nipy.sourceforge.net/nibabel/dicom/dicom_orientation.html#dicom-slice-affine)
        image_orient1 = numpy.array(dicom_header.ImageOrientationPatient)[0:3]
        image_orient2 = numpy.array(dicom_header.ImageOrientationPatient)[3:6]
        image_orient_combined = (image_orient1.tolist(), image_orient2.tolist())
        found_orientation = False
        for orientation in orientations:
            if numpy.allclose(image_orient_combined[0], numpy.array(orientation[0]), rtol=0.001, atol=0.001) \
                    and numpy.allclose(image_orient_combined[1], numpy.array(orientation[1]), rtol=0.001,
                                       atol=0.001):
                sorted_dicoms[str(orientation)].append(dicom_header)
                found_orientation = True
                break
        if not found_orientation:
            orientations.append(image_orient_combined)
            sorted_dicoms[str(image_orient_combined)] = [dicom_header]

    # if there are multiple possible orientations delete orientations where there are less than 4 files
    # we don't convert anything less that that anyway

    if len(sorted_dicoms) > 1:
        filtered_dicoms = []
        for orientation in sorted_dicoms.keys():
            if len(sorted_dicoms[orientation]) >= 4:
                filtered_dicoms.extend(sorted_dicoms[orientation])
        return filtered_dicoms
    else:
        return next(iter(sorted_dicoms.values()))


def _convert_slice_incement_inconsistencies(dicom_input):
    """
    If there is slice increment inconsistency detected, for the moment CT images, then split the volumes into subvolumes based on the slice increment and process each volume separately using a space constructed based on the highest resolution increment
    """

    #   Estimate the "first" slice increment based on the 2 first slices
    increment = numpy.array(dicom_input[0].ImagePositionPatient) - numpy.array(dicom_input[1].ImagePositionPatient)

    # Create as many volumes as many changes in slice increment. NB Increments might be repeated in different volumes
    max_slice_increment = 0
    slice_incement_groups = []
    current_group = [dicom_input[0], dicom_input[1]]
    previous_image_position = numpy.array(dicom_input[1].ImagePositionPatient)
    for dicom in dicom_input[2:]:
        current_image_position = numpy.array(dicom.ImagePositionPatient)
        current_increment = previous_image_position - current_image_position
        max_slice_increment = max(max_slice_increment, numpy.linalg.norm(current_increment))
        if numpy.allclose(increment, current_increment, rtol=0.05, atol=0.1):
            current_group.append(dicom)
        if not numpy.allclose(increment, current_increment, rtol=0.05, atol=0.1):
            slice_incement_groups.append(current_group)
            current_group = [current_group[-1], dicom]
            increment = current_increment
        previous_image_position = current_image_position
    slice_incement_groups.append(current_group)

    # Create nibabel objects for each volume based on the corresponding headers
    slice_incement_niftis = []
    slice_increments = []
    voxel_sizes = {}
    for dicom_slices in slice_incement_groups:
        data = common.get_volume_pixeldata(dicom_slices)
        affine, _ = common.create_affine(dicom_slices)
        if data.ndim > 3:  # do not squeeze single slice data
            data = data.squeeze()
        current_volume = nibabel.Nifti1Image(data, affine)
        slice_increment = numpy.linalg.norm(current_volume.header.get_zooms())
        voxel_sizes['%.5f' % slice_increment] = current_volume.header.get_zooms()
        slice_increments.extend([slice_increment] * (len(dicom_slices) - 1))
        slice_incement_niftis.append(current_volume)

    tenth_percentile_incement = numpy.percentile(slice_increments, 15)
    most_used_increment = min(slice_increments, key=lambda x: abs(x - tenth_percentile_incement))
    voxel_size = voxel_sizes['%.5f' % most_used_increment]

    nifti_volume = resample.resample_nifti_images(slice_incement_niftis, voxel_size=voxel_size)

    return nifti_volume, max_slice_increment
