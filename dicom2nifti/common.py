# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import logging
import os
import struct

import numpy
import pydicom
from pydicom.tag import Tag

import dicom2nifti.settings
from dicom2nifti.exceptions import ConversionValidationError, ConversionError

logger = logging.getLogger(__name__)


# Disable false positive numpy errors
# pylint: disable=E1101
def read_dicom_directory(dicom_directory, stop_before_pixels=False):
    """
    Read all dicom files in a given directory (stop before pixels)

    :type stop_before_pixels: bool
    :type dicom_directory: str
    :param stop_before_pixels: Should we stop reading before the pixeldata (handy if we only want header info)
    :param dicom_directory: Directory with dicom data
    :return: List of dicom objects
    """
    dicom_input = []
    for root, _, files in os.walk(dicom_directory):
        for dicom_file in files:
            file_path = os.path.join(root, dicom_file)
            if is_dicom_file(file_path):
                dicom_headers = pydicom.read_file(file_path,
                                                  defer_size="1 KB",
                                                  stop_before_pixels=stop_before_pixels,
                                                  force=dicom2nifti.settings.pydicom_read_force)
                if is_valid_imaging_dicom(dicom_headers):
                    dicom_input.append(dicom_headers)
    return dicom_input


def is_hitachi(dicom_input):
    """
    Use this function to detect if a dicom series is a hitachi dataset

    :param dicom_input: directory with dicom files for 1 scan of a dicom_header
    """
    # read dicom header
    header = dicom_input[0]

    if 'Manufacturer' not in header or 'Modality' not in header:
        return False  # we try generic conversion in these cases

    # check if Modality is mr
    if header.Modality.upper() != 'MR':
        return False

    # check if manufacturer is hitachi
    if 'HITACHI' not in header.Manufacturer.upper():
        return False

    return True


def is_ge(dicom_input):
    """
    Use this function to detect if a dicom series is a GE dataset

    :param dicom_input: list with dicom objects
    """
    # read dicom header
    header = dicom_input[0]

    if 'Manufacturer' not in header or 'Modality' not in header:
        return False  # we try generic conversion in these cases

    # check if Modality is mr
    if header.Modality.upper() != 'MR':
        return False

    # check if manufacturer is GE
    if 'GE MEDICAL SYSTEMS' not in header.Manufacturer.upper():
        return False

    return True


def is_philips(dicom_input):
    """
    Use this function to detect if a dicom series is a philips dataset

    :param dicom_input: directory with dicom files for 1 scan of a dicom_header
    """
    # read dicom header
    header = dicom_input[0]

    if 'Manufacturer' not in header or 'Modality' not in header:
        return False  # we try generic conversion in these cases

    # check if Modality is mr
    if header.Modality.upper() != 'MR':
        return False

    # check if manufacturer is Philips
    if 'PHILIPS' not in header.Manufacturer.upper():
        return False

    return True


def is_siemens(dicom_input):
    """
    Use this function to detect if a dicom series is a siemens dataset

    :param dicom_input: directory with dicom files for 1 scan
    """
    # read dicom header
    header = dicom_input[0]

    # check if manufacturer is Siemens
    if 'Manufacturer' not in header or 'Modality' not in header:
        return False  # we try generic conversion in these cases

    # check if Modality is mr
    if header.Modality.upper() != 'MR':
        return False

    if 'SIEMENS' not in header.Manufacturer.upper():
        return False

    return True


def is_multiframe_dicom(dicom_input):
    """
    Use this function to detect if a dicom series is a siemens 4D dataset
    NOTE: Only the first slice will be checked so you can only provide an already sorted dicom directory
    (containing one series)

    :param dicom_input: directory with dicom files for 1 scan
    """
    # read dicom header
    header = dicom_input[0]

    if Tag(0x0002, 0x0002) not in header.file_meta:
        return False
    # enhanced CT image storage
    if header.file_meta.MediaStorageSOPClassUID == '1.2.840.10008.5.1.4.1.1.2.1':
        return True
    # enhanced MRI image storage
    if header.file_meta.MediaStorageSOPClassUID == '1.2.840.10008.5.1.4.1.1.4.1':
        return True

    # fallback for certain vendors not setting the correct SOPClassUID
    if "SharedFunctionalGroupsSequence" in header:
        return True

    if "PerFrameFunctionalGroupsSequence" in header:
        return True

    return False


def is_valid_imaging_dicom(dicom_header):
    """
    Function will do some basic checks to see if this is a valid imaging dicom
    """
    # if it is philips and multiframe dicom then we assume it is ok
    try:
        if is_multiframe_dicom([dicom_header]):
            return True

        if "SeriesInstanceUID" not in dicom_header:
            return False

        if "InstanceNumber" not in dicom_header:
            return False

        if "ImageOrientationPatient" not in dicom_header or len(dicom_header.ImageOrientationPatient) < 6:
            return False

        if "ImagePositionPatient" not in dicom_header or len(dicom_header.ImagePositionPatient) < 3:
            return False

        # for all others if there is image position patient we assume it is ok
        if Tag(0x0020, 0x0037) not in dicom_header:
            return False

        return True
    except (KeyError, AttributeError):
        return False


def _get_t_position_index(multiframe_dicom):
    # First try temporal position index itself
    if 'DimensionIndexSequence' not in multiframe_dicom:
        return None

    for current_index in range(len(multiframe_dicom.DimensionIndexSequence)):
        item = multiframe_dicom.DimensionIndexSequence[current_index]
        if 'DimensionDescriptionLabel' in item and \
                'Temporal Position Index' in item.DimensionDescriptionLabel:
            return current_index

    # This seems to work for most dti
    for current_index in range(len(multiframe_dicom.DimensionIndexSequence)):
        item = multiframe_dicom.DimensionIndexSequence[current_index]
        if 'DimensionDescriptionLabel' in item and \
                'Diffusion Gradient Orientation' in item.DimensionDescriptionLabel:
            return current_index

    # This seems to work for 3D grace sequences
    for current_index in range(len(multiframe_dicom.DimensionIndexSequence)):
        item = multiframe_dicom.DimensionIndexSequence[current_index]
        if 'DimensionDescriptionLabel' in item and \
                'Effective Echo Time' in item.DimensionDescriptionLabel:
            return current_index

    # First try trigger delay time (inspired by http://www.dclunie.com/papers/SCAR_20040522_CTMRMF.pdf)
    for current_index in range(len(multiframe_dicom.DimensionIndexSequence)):
        item = multiframe_dicom.DimensionIndexSequence[current_index]
        if 'DimensionDescriptionLabel' in item and \
                'Trigger Delay Time' in item.DimensionDescriptionLabel:
            return current_index

    return None


def multiframe_to_block(multiframe_dicom):
    """
    Generate a full datablock containing all stacks
    """
    # Calculate the amount of stacks and slices in the stack
    number_of_stacks, number_of_stack_slices = multiframe_get_stack_count([multiframe_dicom])

    # We create a numpy array
    size_x = multiframe_dicom.pixel_array.shape[2]
    size_y = multiframe_dicom.pixel_array.shape[1]
    size_z = number_of_stack_slices
    size_t = number_of_stacks
    # get the format
    format_string = get_numpy_type(multiframe_dicom)

    # get header info needed for ordering
    frame_info = multiframe_dicom.PerFrameFunctionalGroupsSequence

    data_4d = numpy.zeros((size_z, size_y, size_x, size_t), dtype=format_string)

    # loop over each slice and insert in datablock
    t_location_index = _get_t_position_index(multiframe_dicom)
    for slice_index in range(0, size_t * size_z):

        if "FrameContentSequence" in frame_info[slice_index]:
            z_location = frame_info[slice_index].FrameContentSequence[0].InStackPositionNumber - 1
        else:
            z_location = slice_index

        if t_location_index is not None:
            t_location = frame_info[slice_index].FrameContentSequence[0].DimensionIndexValues[t_location_index] - 1
        elif "FrameContentSequence" in frame_info[slice_index] and \
                "TemporalPositionIndex" in frame_info[slice_index].FrameContentSequence[0]:
            t_location = frame_info[slice_index].FrameContentSequence[0].TemporalPositionIndex - 1
        else:
            t_location = 0

        block_data = multiframe_dicom.pixel_array[slice_index, :, :]
        # apply scaling
        if "PixelValueTransformationSequence" in frame_info[slice_index]:
            rescale_intercept = frame_info[slice_index].PixelValueTransformationSequence[0].RescaleIntercept
            rescale_slope = frame_info[slice_index].PixelValueTransformationSequence[0].RescaleSlope
            block_data = do_scaling(block_data, rescale_slope, rescale_intercept)
        # switch to float if needed
        if block_data.dtype != data_4d.dtype:
            new_dtype = numpy.promote_types(block_data.dtype, data_4d.dtype)
            data_4d = data_4d.astype(new_dtype)
            block_data = block_data.astype(new_dtype)
        data_4d[z_location, :, :, t_location] = block_data

    full_block = numpy.zeros((size_x, size_y, size_z, size_t), dtype=data_4d.dtype)

    # loop over each stack and reorganize the data
    for t_index in range(0, size_t):
        # transpose the block so the directions are correct
        data_3d = numpy.transpose(data_4d[:, :, :, t_index], (2, 1, 0))
        # add the block the full data
        full_block[:, :, :, t_index] = data_3d

    return numpy.squeeze(full_block)


def get_volume_pixeldata(sorted_slices):
    """
    the slice and intercept calculation can cause the slices to have different dtypes
    we should get the correct dtype that can cover all of them

    :type sorted_slices: list of slices
    :param sorted_slices: sliced sored in the correct order to create volume
    """
    slices = []
    combined_dtype = None
    for slice_ in sorted_slices:
        slice_data = _get_slice_pixeldata(slice_)
        slice_data = slice_data[numpy.newaxis, :, :]
        slices.append(slice_data)
        if combined_dtype is None:
            combined_dtype = slice_data.dtype
        else:
            combined_dtype = numpy.promote_types(combined_dtype, slice_data.dtype)

    # create the new volume with with the correct data
    vol = numpy.concatenate(slices, axis=0)

    # Done
    # if rgb data do separate transpose
    if len(vol.shape) == 4 and vol.shape[3] == 3:
        vol = numpy.transpose(vol, (2, 1, 0, 3))
    else:
        vol = numpy.transpose(vol, (2, 1, 0))
    return vol


def _get_slice_pixeldata(dicom_slice):
    """
    the slice and intercept calculation can cause the slices to have different dtypes
    we should get the correct dtype that can cover all of them

    :type dicom_slice: pydicom object
    :param dicom_slice: slice to get the pixeldata for
    """
    data = dicom_slice.pixel_array
    # fix overflow issues for signed data where BitsStored is lower than BitsAllocated and PixelReprentation = 1 (signed)
    # for example a hitachi mri scan can have BitsAllocated 16 but BitsStored is 12 and HighBit 11
    if dicom_slice.BitsAllocated != dicom_slice.BitsStored and \
            dicom_slice.HighBit == dicom_slice.BitsStored - 1 and \
            dicom_slice.PixelRepresentation == 1:
        if dicom_slice.BitsAllocated == 16:
            data = data.astype(numpy.int16)  # assert that it is a signed type
        max_value = pow(2, dicom_slice.HighBit) - 1
        invert_value = -1 ^ max_value
        data[data > max_value] = numpy.bitwise_or(data[data > max_value], invert_value)
        pass
    return apply_scaling(data, dicom_slice)


def _is_float(float_value):
    """
    Check if a number is actually a float

    :type float_value: int or float
    :param float_value: number to check
    :return True if it is not an integer number
    """
    if int(float_value) != float_value:
        return True


def get_numpy_type(dicom_header):
    """
    Make NumPy format code, e.g. "uint16", "int32" etc
    from two pieces of info:
    mosaic.PixelRepresentation -- 0 for unsigned, 1 for signed;
    mosaic.BitsAllocated -- 8, 16, or 32

    :param dicom_header: the read dicom file/headers
    :returns: numpy format string
    """

    format_string = '%sint%d' % (('u', '')[dicom_header.PixelRepresentation], dicom_header.BitsAllocated)
    try:
        numpy.dtype(format_string)
    except TypeError:
        raise TypeError("Data type not understood by NumPy: format='%s', PixelRepresentation=%d, BitsAllocated=%d" %
                        (format_string, dicom_header.PixelRepresentation, dicom_header.BitsAllocated))
    return format_string


def get_fd_array_value(tag, count):
    """
    Getters for data that also work with implicit transfersyntax

    :param count: number of items in the array
    :param tag: the tag to read
    """
    if tag.VR == 'OB' or tag.VR == 'UN':
        values = []
        for i in range(count):
            start = i * 8
            stop = (i + 1) * 8
            values.append(struct.unpack('d', tag.value[start:stop])[0])
        return numpy.array(values)
    return tag.value


def get_fd_value(tag):
    """
    Getters for data that also work with implicit transfersyntax

    :param tag: the tag to read
    """
    if tag.VR == 'OB' or tag.VR == 'UN':
        value = struct.unpack('d', tag.value)[0]
        return value
    return tag.value


def set_fd_value(tag, value):
    """
    Setters for data that also work with implicit transfersyntax

    :param value: the value to set on the tag
    :param tag: the tag to read
    """
    if tag.VR == 'OB' or tag.VR == 'UN':
        value = struct.pack('d', value)
    tag.value = value


def get_fl_value(tag):
    """
    Getters for data that also work with implicit transfersyntax

    :param tag: the tag to read
    """
    if tag.VR == 'OB' or tag.VR == 'UN':
        value = struct.unpack('f', tag.value)[0]
        return value
    return tag.value


def get_is_value(tag):
    """
    Getters for data that also work with implicit transfersyntax

    :param tag: the tag to read
    """
    # data is int formatted as string so convert te string first and cast to int
    if tag.VR == 'OB' or tag.VR == 'UN':
        value = int(tag.value.decode("ascii").replace(" ", ""))
        return value
    return int(tag.value)


def get_ss_value(tag):
    """
    Getters for data that also work with implicit transfersyntax

    :param tag: the tag to read
    """
    # data is int formatted as string so convert te string first and cast to int
    if tag.VR == 'OB' or tag.VR == 'UN':
        value = struct.unpack('h', tag.value)[0]
        return value
    return tag.value


def set_ss_value(tag, value):
    """
    Setter for data that also work with implicit transfersyntax

    :param value: the value to set on the tag
    :param tag: the tag to read
    """
    if tag.VR == 'OB' or tag.VR == 'UN':
        value = struct.pack('h', value)
    tag.value = value


def apply_scaling(data, dicom_headers):
    """
    Rescale the data based on the RescaleSlope and RescaleOffset
    Based on the scaling from pydicomseries

    :param dicom_headers: dicom headers to use to retreive the scaling factors
    :param data: the input data
    """

    # Apply the rescaling if needed
    private_scale_slope_tag = Tag(0x2005, 0x100E)
    private_scale_intercept_tag = Tag(0x2005, 0x100D)
    if 'RescaleSlope' in dicom_headers or 'RescaleIntercept' in dicom_headers \
            or private_scale_slope_tag in dicom_headers or private_scale_intercept_tag in dicom_headers:
        rescale_slope = 1
        rescale_intercept = 0
        if 'RescaleSlope' in dicom_headers:
            rescale_slope = dicom_headers.RescaleSlope
        if 'RescaleIntercept' in dicom_headers:
            rescale_intercept = dicom_headers.RescaleIntercept
        # try:
        #     # this section can sometimes fail due to unknown private fields
        #     if private_scale_slope_tag in dicom_headers:
        #         private_scale_slope = float(dicom_headers[private_scale_slope_tag].value)
        #     if private_scale_slope_tag in dicom_headers:
        #         private_scale_slope = float(dicom_headers[private_scale_slope_tag].value)
        # except:
        #     pass
        return do_scaling(data, rescale_slope, rescale_intercept)
    else:
        return data


def do_scaling(data, rescale_slope, rescale_intercept, private_scale_slope=1.0, private_scale_intercept=0.0):
    # Obtain slope and offset
    need_floats = False

    if int(rescale_slope) != rescale_slope or \
            int(rescale_intercept) != rescale_intercept or \
            private_scale_slope != 1.0 or \
            private_scale_intercept != 0.0:
        need_floats = True

    if not need_floats:
        rescale_slope = int(rescale_slope)
        rescale_intercept = int(rescale_intercept)
    else:
        rescale_slope = float(rescale_slope)
        rescale_intercept = float(rescale_intercept)
        private_scale_slope = float(private_scale_slope)
        private_scale_intercept = float(private_scale_intercept)
    # Maybe we need to change the datatype?
    if data.dtype in [numpy.float32, numpy.float64]:
        pass
    elif need_floats:
        data = data.astype(numpy.float32)
    else:
        # Determine required range
        minimum_required, maximum_required = data.min(), data.max()
        minimum_required = min([minimum_required, minimum_required * rescale_slope + rescale_intercept,
                                maximum_required * rescale_slope + rescale_intercept])
        maximum_required = max([maximum_required, minimum_required * rescale_slope + rescale_intercept,
                                maximum_required * rescale_slope + rescale_intercept])

        # Determine required datatype from that
        if minimum_required < 0:
            # Signed integer type
            maximum_required = max([-minimum_required, maximum_required])
            if maximum_required < 2 ** 7:
                dtype = numpy.int8
            elif maximum_required < 2 ** 15:
                dtype = numpy.int16
            elif maximum_required < 2 ** 31:
                dtype = numpy.int32
            else:
                dtype = numpy.float32
        else:
            # Unsigned integer type
            if maximum_required < 2 ** 8:
                dtype = numpy.uint8
            elif maximum_required < 2 ** 16:
                dtype = numpy.uint16
            elif maximum_required < 2 ** 32:
                dtype = numpy.uint32
            else:
                dtype = numpy.float32

        # Change datatype
        if dtype != data.dtype:
            data = data.astype(dtype)

    # Apply rescale_slope and rescale_intercept
    # Scaling according to ISMRM2013_PPM_scaling_reminder
    # The actual scaling is not does the scaling the same way as the next code example
    # and https://github.com/fedorov/DICOMPhilipsRescalePlugin/blob/master/DICOMPhilipsRescalePlugin.py
    # FOR DEFAULT DATA
    # RESULT_DATA = (STORED_VALUE * RESCALE_SLOPE) + RESCALE_INTERCEPT
    # FOR PHILIPS DATA
    # RESULT_DATA = (STORED_VALUE * PRIVATE_SCALE_SLOPE) + PRIVATE_SCALE_INTERCEPT
    if private_scale_slope == 1.0 and private_scale_intercept == 0.0:
        data = (data * rescale_slope) + rescale_intercept
    else:
        data = (data * private_scale_slope) + private_scale_intercept

    return data


def write_bvec_file(bvecs, bvec_file):
    """
    Write an array of bvecs to a bvec file

    :param bvecs: array with the vectors
    :param bvec_file: filepath to write to
    """
    if bvec_file is None:
        return
    logger.info('Saving BVEC file: %s' % bvec_file)
    with open(bvec_file, 'w') as text_file:
        # Map a dicection to string join them using a space and write to the file
        text_file.write('%s\n' % ' '.join(map(str, bvecs[:, 0])))
        text_file.write('%s\n' % ' '.join(map(str, bvecs[:, 1])))
        text_file.write('%s\n' % ' '.join(map(str, bvecs[:, 2])))


def write_bval_file(bvals, bval_file):
    """
    Write an array of bvals to a bval file

    :param bvals: array with the values
    :param bval_file: filepath to write to
    """
    if bval_file is None:
        return
    logger.info('Saving BVAL file: %s' % bval_file)
    with open(bval_file, 'w') as text_file:
        # join the bvals using a space and write to the file
        text_file.write('%s\n' % ' '.join(map(str, bvals)))


def multiframe_create_affine(dicoms, data_block):
    """
    Function to generate the affine matrix for a dicom series
    This method was based on (http://nipy.org/nibabel/dicom/dicom_orientation.html)

    :param sorted_dicoms: list with sorted dicom files
    """

    # Create affine matrix (http://nipy.sourceforge.net/nibabel/dicom/dicom_orientation.html#dicom-slice-affine)
    frame_info = dicoms[0].PerFrameFunctionalGroupsSequence
    image_orient1, image_orient2 = _multiframe_get_image_orientations(dicoms[0], 0)

    if 'PixelMeasuresSequence' in frame_info[0]:
        delta_r = float(frame_info[0].PixelMeasuresSequence[0].PixelSpacing[0])
        delta_c = float(frame_info[0].PixelMeasuresSequence[0].PixelSpacing[1])
    elif "SharedFunctionalGroupsSequence" in dicoms[0] and \
            "PixelMeasuresSequence" in dicoms[0].SharedFunctionalGroupsSequence[0]:
        shared_frame_info = dicoms[0].SharedFunctionalGroupsSequence
        delta_r = numpy.array(shared_frame_info[0].PixelMeasuresSequence[0].PixelSpacing[0])
        delta_c = numpy.array(shared_frame_info[0].PixelMeasuresSequence[0].PixelSpacing[1])
    elif "PixelSpacing" in dicoms[0]:
        delta_r = numpy.array(dicoms[0].PixelSpacing[0])
        delta_c = numpy.array(dicoms[0].PixelSpacing[1])
    else:
        logger.warning('Unsupported or missing PixelMeasuresSequence')
        raise ConversionError('Unsupported or missing PixelMeasuresSequence')

    image_pos = _multiframe_get_image_position(dicoms[0], 0)
    last_image_pos = _multiframe_get_image_position(dicoms[0], -1)

    if len(frame_info) == 1:
        # Single slice
        slice_thickness = 1
        if "SliceThickness" in frame_info[0].PixelMeasuresSequence[0]:
            slice_thickness = frame_info[0].PixelMeasuresSequence[0].SliceThickness
        step = - numpy.cross(image_orient1, image_orient2) * slice_thickness
    else:
        slices_per_block = data_block.shape[2]
        step = (image_pos - last_image_pos) / (1 - slices_per_block)

    # check if this is actually a volume and not all slices on the same location
    if numpy.linalg.norm(step) == 0.0:
        raise ConversionError("NOT_A_VOLUME")

    affine = numpy.array(
        [[-image_orient1[0] * delta_c, -image_orient2[0] * delta_r, -step[0], -image_pos[0]],
         [-image_orient1[1] * delta_c, -image_orient2[1] * delta_r, -step[1], -image_pos[1]],
         [image_orient1[2] * delta_c, image_orient2[2] * delta_r, step[2], image_pos[2]],
         [0, 0, 0, 1]]
    )
    return affine, numpy.linalg.norm(step)


def create_affine(sorted_dicoms):
    """
    Function to generate the affine matrix for a dicom series
    This method was based on (http://nipy.org/nibabel/dicom/dicom_orientation.html)

    :param sorted_dicoms: list with sorted dicom files
    """

    # Create affine matrix (http://nipy.sourceforge.net/nibabel/dicom/dicom_orientation.html#dicom-slice-affine)
    image_orient1 = numpy.array(sorted_dicoms[0].ImageOrientationPatient)[0:3]
    image_orient2 = numpy.array(sorted_dicoms[0].ImageOrientationPatient)[3:6]

    delta_r = float(sorted_dicoms[0].PixelSpacing[0])
    delta_c = float(sorted_dicoms[0].PixelSpacing[1])

    image_pos = numpy.array(sorted_dicoms[0].ImagePositionPatient)

    last_image_pos = numpy.array(sorted_dicoms[-1].ImagePositionPatient)

    if len(sorted_dicoms) == 1:
        # Single slice
        slice_thickness = 1
        if "SliceThickness" in sorted_dicoms[0]:
            slice_thickness = sorted_dicoms[0].SliceThickness
        step = - numpy.cross(image_orient1, image_orient2) * slice_thickness
    else:
        step = (image_pos - last_image_pos) / (1 - len(sorted_dicoms))

    # check if this is actually a volume and not all slices on the same location
    if numpy.linalg.norm(step) == 0.0:
        raise ConversionError("NOT_A_VOLUME")

    affine = numpy.array(
        [[-image_orient1[0] * delta_c, -image_orient2[0] * delta_r, -step[0], -image_pos[0]],
         [-image_orient1[1] * delta_c, -image_orient2[1] * delta_r, -step[1], -image_pos[1]],
         [image_orient1[2] * delta_c, image_orient2[2] * delta_r, step[2], image_pos[2]],
         [0, 0, 0, 1]]
    )
    return affine, numpy.linalg.norm(step)


def multiframe_validate_orthogonal(dicoms):
    """
    Validate that volume is orthonormal

    :param dicoms: check that we have a volume without skewing
    """
    # if only one slice we do not need this check
    if not multiframe_is_orthogonal(dicoms, log_details=True):
        raise ConversionValidationError('NON_CUBICAL_IMAGE/GANTRY_TILT')


def validate_orthogonal(dicoms):
    """
    Validate that volume is orthonormal

    :param dicoms: check that we have a volume without skewing
    """
    # if only one slice we do not need this check
    if len(dicoms) == 1:
        return
    if not is_orthogonal(dicoms, log_details=True):
        raise ConversionValidationError('NON_CUBICAL_IMAGE/GANTRY_TILT')


def multiframe_is_orthogonal(dicoms, log_details=False):
    """
    Validate that volume is orthonormal

    :param dicoms: check that we have a volume without skewing
    """
    first_image_orient1, first_image_orient2 = _multiframe_get_image_orientations(dicoms[0], 0)
    first_image_pos = _multiframe_get_image_position(dicoms[0], 0)
    last_image_pos = _multiframe_get_image_position(dicoms[0], -1)

    first_image_dir = numpy.cross(first_image_orient1, first_image_orient2)
    first_image_dir /= numpy.linalg.norm(first_image_dir)

    combined_dir = last_image_pos - first_image_pos
    combined_dir /= numpy.linalg.norm(combined_dir)

    if not numpy.allclose(first_image_dir, combined_dir, rtol=0.05, atol=0.05) \
            and not numpy.allclose(first_image_dir, -combined_dir, rtol=0.05, atol=0.05):
        if log_details:
            logger.warning('Orthogonality check failed: non cubical image')
            logger.warning('---------------------------------------------------------')
            logger.warning(first_image_dir)
            logger.warning(combined_dir)
            logger.warning('---------------------------------------------------------')
        return False
    return True


def is_orthogonal(dicoms, log_details=False):
    """
    Validate that volume is orthonormal

    :param dicoms: check that we have a volume without skewing
    """
    first_image_orient1 = numpy.array(dicoms[0].ImageOrientationPatient)[0:3]
    first_image_orient2 = numpy.array(dicoms[0].ImageOrientationPatient)[3:6]
    first_image_pos = numpy.array(dicoms[0].ImagePositionPatient)

    last_image_pos = numpy.array(dicoms[-1].ImagePositionPatient)

    first_image_dir = numpy.cross(first_image_orient1, first_image_orient2)
    first_image_dir /= numpy.linalg.norm(first_image_dir)

    combined_dir = last_image_pos - first_image_pos
    combined_dir /= numpy.linalg.norm(combined_dir)

    if not numpy.allclose(first_image_dir, combined_dir, rtol=0.05, atol=0.05) \
            and not numpy.allclose(first_image_dir, -combined_dir, rtol=0.05, atol=0.05):
        if log_details:
            logger.warning('Orthogonality check failed: non cubical image')
            logger.warning('---------------------------------------------------------')
            logger.warning(first_image_dir)
            logger.warning(combined_dir)
            logger.warning('---------------------------------------------------------')
        return False
    return True


def is_orthogonal_nifti(nifti_image):
    """
    Validate that volume is orthonormal

    :param dicoms: check that we have a volume without skewing
    """
    affine = nifti_image.affine

    transformed_x = numpy.transpose(numpy.dot(affine, [[1], [0], [0], [0]]))[0][:3]
    transformed_y = numpy.transpose(numpy.dot(affine, [[0], [1], [0], [0]]))[0][:3]
    transformed_z = numpy.transpose(numpy.dot(affine, [[0], [0], [1], [0]]))[0][:3]

    transformed_x /= numpy.linalg.norm(transformed_x)
    transformed_y /= numpy.linalg.norm(transformed_y)
    transformed_z /= numpy.linalg.norm(transformed_z)

    perpendicular = numpy.cross(transformed_x, transformed_y)
    perpendicular /= numpy.linalg.norm(perpendicular)

    if not numpy.allclose(transformed_z, perpendicular, rtol=0.05, atol=0.05) \
            and not numpy.allclose(transformed_z, -perpendicular, rtol=0.05, atol=0.05):
        return False
    return True


def sort_dicoms(dicoms):
    """
    Sort the dicoms based om the image possition patient

    :param dicoms: list of dicoms
    """
    # find most significant axis to use during sorting
    # the original way of sorting (first x than y than z) does not work in certain border situations
    # where for exampe the X will only slightly change causing the values to remain equal on multiple slices
    # messing up the sorting completely)
    dicom_input_sorted_x = sorted(dicoms, key=lambda x: (x.ImagePositionPatient[0]))
    dicom_input_sorted_y = sorted(dicoms, key=lambda x: (x.ImagePositionPatient[1]))
    dicom_input_sorted_z = sorted(dicoms, key=lambda x: (x.ImagePositionPatient[2]))
    diff_x = abs(dicom_input_sorted_x[-1].ImagePositionPatient[0] - dicom_input_sorted_x[0].ImagePositionPatient[0])
    diff_y = abs(dicom_input_sorted_y[-1].ImagePositionPatient[1] - dicom_input_sorted_y[0].ImagePositionPatient[1])
    diff_z = abs(dicom_input_sorted_z[-1].ImagePositionPatient[2] - dicom_input_sorted_z[0].ImagePositionPatient[2])
    if diff_x >= diff_y and diff_x >= diff_z:
        return dicom_input_sorted_x
    if diff_y >= diff_x and diff_y >= diff_z:
        return dicom_input_sorted_y
    if diff_z >= diff_x and diff_z >= diff_y:
        return dicom_input_sorted_z


def multiframe_validate_slice_increment(dicoms):
    """
    Validate that the distance between all slices is equal (or very close to)

    :param dicoms: list of dicoms
    """

    frame_info = dicoms[0].PerFrameFunctionalGroupsSequence
    first_image_position = _multiframe_get_image_position(dicoms[0], 0)
    previous_image_position = _multiframe_get_image_position(dicoms[0], 1)

    increment = first_image_position - previous_image_position
    for frame_number in range(2, len(frame_info)):
        current_image_position = _multiframe_get_image_position(dicoms[0], frame_number)
        current_increment = previous_image_position - current_image_position
        if not numpy.allclose(increment, current_increment, rtol=0.05, atol=0.1):
            logger.warning('Slice increment not consistent through all slices')
            logger.warning('---------------------------------------------------------')
            logger.warning('%s %s' % (previous_image_position, increment))
            logger.warning('%s %s' % (current_image_position, current_increment))
            logger.warning('---------------------------------------------------------')
            raise ConversionValidationError('SLICE_INCREMENT_INCONSISTENT')
        previous_image_position = current_image_position


def validate_slice_increment(dicoms):
    """
    Validate that the distance between all slices is equal (or very close to)

    :param dicoms: list of dicoms
    """

    # if only one slice we do not need to run the checks
    if len(dicoms) == 1:
        return

    first_image_position = numpy.array(dicoms[0].ImagePositionPatient)
    previous_image_position = numpy.array(dicoms[1].ImagePositionPatient)

    increment = first_image_position - previous_image_position
    for dicom_ in dicoms[2:]:
        current_image_position = numpy.array(dicom_.ImagePositionPatient)
        current_increment = previous_image_position - current_image_position
        if not numpy.allclose(increment, current_increment, rtol=0.05, atol=0.1):
            logger.warning('Slice increment not consistent through all slices')
            logger.warning('---------------------------------------------------------')
            logger.warning('%s %s' % (previous_image_position, increment))
            logger.warning('%s %s' % (current_image_position, current_increment))
            if 'InstanceNumber' in dicom_:
                logger.warning('Instance Number: %s' % dicom_.InstanceNumber)
            logger.warning('---------------------------------------------------------')
            raise ConversionValidationError('SLICE_INCREMENT_INCONSISTENT')
        previous_image_position = current_image_position


def validate_instance_number(dicoms):
    """
    Validate that the instance number is consistent through all slices

    :param dicoms: list of dicoms
    """
    if "InstanceNumber" not in dicoms[0]:
        return
    first_instance_number = numpy.array(dicoms[0].InstanceNumber)
    previous_instance_number = numpy.array(dicoms[1].InstanceNumber)

    instance_number_increment = first_instance_number - previous_instance_number
    for dicom_ in dicoms[2:]:
        current_instance_number = numpy.array(dicom_.InstanceNumber)
        current_instance_number_increment = previous_instance_number - current_instance_number
        if not instance_number_increment == current_instance_number_increment:
            logger.warning('Instance Number not consistent through all slices')
            logger.warning('---------------------------------------------------------')
            logger.warning('%s %s' % (previous_instance_number, current_instance_number))
            logger.warning('---------------------------------------------------------')
            raise ConversionValidationError('INSTANCE_NUMBER_INCONSISTENT')
        previous_instance_number = current_instance_number


def multiframe_is_slice_increment_inconsistent(dicoms):
    """
    Validate that the distance between all slices is equal (or very close to)

    :param dicoms: list of dicoms
    """
    sliceincrement_inconsistent = False
    frame_info = dicoms[0].PerFrameFunctionalGroupsSequence
    first_image_position = _multiframe_get_image_position(dicoms[0], 0)
    previous_image_position = _multiframe_get_image_position(dicoms[0], 1)

    increment = first_image_position - previous_image_position
    for frame_number in range(2, len(frame_info)):
        current_image_position = _multiframe_get_image_position(dicoms[0], frame_number)
        current_increment = previous_image_position - current_image_position
        if not numpy.allclose(increment, current_increment, rtol=0.05, atol=0.1):
            sliceincrement_inconsistent = True
            break
        previous_image_position = current_image_position
    return sliceincrement_inconsistent


def is_slice_increment_inconsistent(dicoms):
    """
    Validate that the distance between all slices is equal (or very close to)

    :param dicoms: list of dicoms
    """
    if len(dicoms) == 1:
        return True
    sliceincrement_inconsistent = False
    first_image_position = numpy.array(dicoms[0].ImagePositionPatient)
    previous_image_position = numpy.array(dicoms[1].ImagePositionPatient)

    increment = first_image_position - previous_image_position
    for dicom_ in dicoms[2:]:
        current_image_position = numpy.array(dicom_.ImagePositionPatient)
        current_increment = previous_image_position - current_image_position
        if not numpy.allclose(increment, current_increment, rtol=0.05, atol=0.1):
            sliceincrement_inconsistent = True
            break
        previous_image_position = current_image_position
    return sliceincrement_inconsistent


def multiframe_validate_slicecount(dicoms):
    """
    Validate that volume is big enough to create a meaningfull volume
    This will also skip localizers and alike

    :param dicoms: list of dicoms
    """
    frame_info = dicoms[0].PerFrameFunctionalGroupsSequence
    if len(frame_info) <= 3:
        logger.warning('At least 3 slices are needed for correct conversion')
        logger.warning('---------------------------------------------------------')
        raise ConversionValidationError('TOO_FEW_SLICES/LOCALIZER')


def multiframe_get_stack_count(dicoms):
    """
    Count the number of 3D stacks in a 4D multiframe dicom, for example fmri or DTI
    Not to be confused with multiframe dicoms containing multiple unrelated stacks
    """
    temporal_position_indices = []
    in_stack_position_numbers = []
    for functional_group_sequence in dicoms[0].PerFrameFunctionalGroupsSequence:
        if "FrameContentSequence" not in functional_group_sequence:
            continue
        if "TemporalPositionIndex" in functional_group_sequence.FrameContentSequence[0]:
            temporal_position_indices.append(functional_group_sequence.FrameContentSequence[0].TemporalPositionIndex)
        if "InStackPositionNumber" in functional_group_sequence.FrameContentSequence[0]:
            in_stack_position_numbers.append(functional_group_sequence.FrameContentSequence[0].InStackPositionNumber)
    temporal_position_indices = list(set(temporal_position_indices))

    # try based on temporal position index first but is not always correctly used
    if len(temporal_position_indices) > 1:
        return len(temporal_position_indices), int(
            len(dicoms[0].PerFrameFunctionalGroupsSequence) / len(temporal_position_indices))

    # try based on the in stack position index
    if len(in_stack_position_numbers) > 1:
        values, count = numpy.unique(numpy.array(in_stack_position_numbers), return_counts=True)
        return count[0], len(values)

    # assume 3D block so 1 stack
    else:
        return 1, len(dicoms[0].PerFrameFunctionalGroupsSequence)


def validate_slicecount(dicoms):
    """
    Validate that volume is big enough to create a meaningfull volume
    This will also skip localizers and alike

    :param dicoms: list of dicoms
    """
    if len(dicoms) <= 3:
        logger.warning('At least 3 slices are needed for correct conversion')
        logger.warning('---------------------------------------------------------')
        raise ConversionValidationError('TOO_FEW_SLICES/LOCALIZER')


def _multiframe_get_image_orientations(dicom_headers, frame_number=0):
    frame_info = dicom_headers.PerFrameFunctionalGroupsSequence
    shared_info = dicom_headers.get("SharedFunctionalGroupsSequence")
    if "PlaneOrientationSequence" in frame_info[frame_number]:
        image_orient1 = numpy.array(frame_info[frame_number].PlaneOrientationSequence[0].ImageOrientationPatient)[0:3]
        image_orient2 = numpy.array(frame_info[frame_number].PlaneOrientationSequence[0].ImageOrientationPatient)[3:6]
    elif shared_info is not None and "PlaneOrientationSequence" in shared_info[0]:
        image_orient1 = numpy.array(shared_info[0].PlaneOrientationSequence[0].ImageOrientationPatient)[0:3]
        image_orient2 = numpy.array(shared_info[0].PlaneOrientationSequence[0].ImageOrientationPatient)[3:6]
    elif "ImageOrientationPatient" in frame_info[frame_number]:
        image_orient1 = numpy.array(frame_info[frame_number].ImageOrientationPatient)[0:3]
        image_orient2 = numpy.array(frame_info[frame_number].ImageOrientationPatient)[3:6]
    elif shared_info is not None and "ImageOrientationPatient" in shared_info[0]:
        image_orient1 = numpy.array(shared_info[0].ImageOrientationPatient)[0:3]
        image_orient2 = numpy.array(shared_info[0].ImageOrientationPatient)[3:6]
    else:
        logger.warning('Unsupported or missing PlaneOrientationSequence/ImageOrientationPatient')
        raise ConversionError('Unsupported or missing PlaneOrientationSequence/ImageOrientationPatient')

    return image_orient1, image_orient2


def _multiframe_get_image_position(dicom_headers, frame_number=0):
    frame_info = dicom_headers.PerFrameFunctionalGroupsSequence

    if "PlanePositionSequence" in frame_info[frame_number]:
        return numpy.array(frame_info[frame_number].PlanePositionSequence[0].ImagePositionPatient)
    elif "ImagePositionPatient" in frame_info[frame_number]:
        return numpy.array(frame_info[frame_number].ImagePositionPatient)
    else:
        logger.warning('Unsupported or missing PlanePositionSequence/ImagePositionPatient')
        raise ConversionError('Unsupported or missing PlanePositionSequence/ImagePositionPatient')


def multiframe_validate_orientation(dicoms):
    """
    Validate that all dicoms have the same orientation

    :param dicoms: list of dicoms
    """

    frame_info = dicoms[0].PerFrameFunctionalGroupsSequence
    first_image_orient1, first_image_orient2 = _multiframe_get_image_orientations(dicoms[0], 0)

    for frame_index, frame_ in enumerate(frame_info):
        # Create affine matrix (http://nipy.sourceforge.net/nibabel/dicom/dicom_orientation.html#dicom-slice-affine)
        image_orient1, image_orient2 = _multiframe_get_image_orientations(dicoms[0], frame_index)
        if not numpy.allclose(image_orient1, first_image_orient1, rtol=0.001, atol=0.001) \
                or not numpy.allclose(image_orient2, first_image_orient2, rtol=0.001, atol=0.001):
            logger.warning('Image orientations not consistent through all slices')
            logger.warning('---------------------------------------------------------')
            logger.warning('%s %s' % (image_orient1, first_image_orient1))
            logger.warning('%s %s' % (image_orient2, first_image_orient2))
            logger.warning('---------------------------------------------------------')
            raise ConversionValidationError('IMAGE_ORIENTATION_INCONSISTENT')


def validate_orientation(dicoms):
    """
    Validate that all dicoms have the same orientation

    :param dicoms: list of dicoms
    """
    first_image_orient1 = numpy.array(dicoms[0].ImageOrientationPatient)[0:3]
    first_image_orient2 = numpy.array(dicoms[0].ImageOrientationPatient)[3:6]
    for dicom_ in dicoms:
        # Create affine matrix (http://nipy.sourceforge.net/nibabel/dicom/dicom_orientation.html#dicom-slice-affine)
        image_orient1 = numpy.array(dicom_.ImageOrientationPatient)[0:3]
        image_orient2 = numpy.array(dicom_.ImageOrientationPatient)[3:6]
        if not numpy.allclose(image_orient1, first_image_orient1, rtol=0.001, atol=0.001) \
                or not numpy.allclose(image_orient2, first_image_orient2, rtol=0.001, atol=0.001):
            logger.warning('Image orientations not consistent through all slices')
            logger.warning('---------------------------------------------------------')
            logger.warning('%s %s' % (image_orient1, first_image_orient1))
            logger.warning('%s %s' % (image_orient2, first_image_orient2))
            logger.warning('---------------------------------------------------------')
            raise ConversionValidationError('IMAGE_ORIENTATION_INCONSISTENT')


def set_tr_te(nifti_image, repetition_time, echo_time):
    """
    Set the tr and te in the nifti headers

    :param echo_time: echo time
    :param repetition_time: repetition time
    :param nifti_image: nifti image to set the info to
    """
    # set the repetition time in pixdim
    nifti_image.header.structarr['pixdim'][4] = repetition_time / 1000.0

    # set tr and te in db_name field
    nifti_image.header.structarr['db_name'] = '?TR:%.3f TE:%d' % (repetition_time, echo_time)

    return nifti_image


def get_nifti_data(nifti_image):
    """
    Function that replicates the deprecated nifti.get_data behavior
    """
    return numpy.asanyarray(nifti_image.dataobj)


def is_dicom_file(filename):
    """
    Util function to check if file is a dicom file
    the first 128 bytes are preamble
    the next 4 bytes should contain DICM otherwise it is not a dicom

    :param filename: file to check for the DICM header block
    :type filename: str
    :returns: True if it is a dicom file
    """
    file_stream = open(filename, 'rb')
    file_stream.seek(128)
    data = file_stream.read(4)
    file_stream.close()
    if data == b'DICM':
        return True
    if dicom2nifti.settings.pydicom_read_force:
        try:
            dicom_headers = pydicom.read_file(filename, defer_size="1 KB", stop_before_pixels=True, force=True)
            if dicom_headers is not None:
                return True
        except:
            pass
    return False
