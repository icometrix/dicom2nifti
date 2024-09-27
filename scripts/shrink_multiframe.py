# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import logging

import numpy
import pydicom
from pydicom import dcmread

import dicom2nifti.common as common
from dicom2nifti.convert_philips import _is_multiframe_diffusion_imaging, _is_multiframe_4d


def shrink_multiframe(input_file, output_file=None, slice_count=8, timepoint_count=4):
    if output_file is None:
        output_file = input_file

    # Load dicom_file_in
    dicom_in = dcmread(input_file)

    if _is_multiframe_diffusion_imaging([dicom_in]) or _is_multiframe_4d([dicom_in]):

        number_of_stack_slices = int(common.get_ss_value(dicom_in[(0x2001, 0x105f)][0][(0x2001, 0x102d)]))
        number_of_stacks = int(int(dicom_in.NumberOfFrames) / number_of_stack_slices)

        # We create a numpy array
        size_x = dicom_in.pixel_array.shape[2]
        size_y = dicom_in.pixel_array.shape[1]
        size_t = number_of_stacks
        frame_info = dicom_in.PerFrameFunctionalGroupsSequence
        data_4d = numpy.zeros((slice_count * timepoint_count, size_x, size_y), dtype=common.get_numpy_type(dicom_in))
        new_frame_info = [None] * slice_count * timepoint_count
        for index_z in range(0, slice_count):
            for index_t in range(0, timepoint_count):
                slice_index = int(size_t * index_z + index_t)
                new_slice_index = int(timepoint_count * index_z + index_t)

                z_location = frame_info[slice_index].FrameContentSequence[0].InStackPositionNumber - 1
                new_frame_info[new_slice_index] = frame_info[slice_index]

                logging.info('Importing slice on position %s %s %s' % (slice_index, z_location, index_t))
                data_4d[new_slice_index, :, :] = dicom_in.pixel_array[slice_index, :, :]

        dicom_in.PixelData = data_4d.tostring()
        common.set_ss_value(dicom_in[(0x2001, 0x105f)][0][(0x2001, 0x102d)], slice_count)
        setattr(dicom_in, 'NumberOfFrames', slice_count * timepoint_count)
        setattr(dicom_in, 'PerFrameFunctionalGroupsSequence', new_frame_info)

    else:
        # truncate the data
        dicom_in.PixelData = dicom_in.pixel_array[:slice_count, :, :].tostring()

        setattr(dicom_in, 'NumberOfFrames', slice_count)
        # truncate the pre frame groups sequence
        setattr(dicom_in, 'PerFrameFunctionalGroupsSequence', dicom_in.PerFrameFunctionalGroupsSequence[:slice_count])

    # Save the file
    dicom_in.save_as(output_file)


def main():
    shrink_multiframe('/Users/abrys/Downloads/cbct_01/001.dcm',timepoint_count=1)

    pass

if __name__ == "__main__":
    main()
