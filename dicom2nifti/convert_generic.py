# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import logging
import nibabel
import numpy

from pydicom.tag import Tag

from .common import is_slice_increment_inconsistent, get_volume_pixeldata, \
    create_affine, set_tr_te, is_multiframe_dicom, validate_slice_increment, \
    validate_instance_number, initial_dicom_checks, sort_dicoms
from .settings import Dicom2NiftiSettings as settings
from .resample import resample_nifti_images

logger = logging.getLogger(__name__)


def generic_dicom_to_nifti(dicom_input, output_file, run_checks=True):
    """
    This function will convert single frame dicom series to a nifti

    Examples: See unit test

    :param output_file: filepath to the output nifti
    :param dicom_input: directory with the dicom files for a single scan, or list of read in dicoms
    :param run_checks:
    """
    if run_checks:
        dicom_input = initial_dicom_checks(dicom_input)

    if not is_multiframe_dicom(dicom_input):
        # sort the dicoms
        dicom_input = sort_dicoms(dicom_input)

    # validate slice increment inconsistent
    if settings.validate_slice_increment:
        # validate that all slices have a consistent slice increment
        validate_slice_increment(dicom_input)

    if settings.validate_instance_number:
        # validate that all slices have a consistent instance_number
        validate_instance_number(dicom_input)

    # if inconsistent increment and we allow resampling then do the resampling based conversion
    # to maintain the correct geometric shape
    if is_slice_increment_inconsistent(dicom_input) and settings.resample:
        if is_multiframe_dicom(dicom_input):
            raise Exception('Conversion of inconsistent slice increment with resampling not supported for multiframe')
            # TODO add support for this if it actually exists
        nii_image, max_slice_increment = _convert_slice_increment_inconsistencies(dicom_input)
    # do the normal conversion
    else:
        # Get data; originally z,y,x, transposed to x,y,z
        data = get_volume_pixeldata(dicom_input)

        affine, max_slice_increment = create_affine(dicom_input)

        # Convert to nifti
        if data.ndim > 3:  # do not squeeze single slice data
            data = data.squeeze()
        if dicom_input[0].PhotometricInterpretation == 'RGB':
            nii_image = create_rgba_nifti(data, affine)
        else:
            nii_image = nibabel.Nifti1Image(data, affine)

    # Set TR and TE if available
    if Tag(0x0018, 0x0080) in dicom_input[0] and Tag(0x0018, 0x0081) in dicom_input[0]:
        set_tr_te(nii_image, float(dicom_input[0].RepetitionTime), float(dicom_input[0].EchoTime))

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


def _convert_slice_increment_inconsistencies(dicom_input):
    """
    If there is slice increment inconsistency detected, for the moment CT images, then split the volumes
    into subvolumes based on the slice increment and process each volume separately using a space
    constructed based on the highest resolution increment
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
        data = get_volume_pixeldata(dicom_slices)
        affine, _ = create_affine(dicom_slices)
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

    nifti_volume = resample_nifti_images(slice_incement_niftis, voxel_size=voxel_size)

    return nifti_volume, max_slice_increment
