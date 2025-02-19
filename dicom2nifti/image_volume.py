# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 07:40:20 2013

@author: abrys
"""
# To ignore numpy errors:
#     pylint: disable=E1101

import nibabel
import numpy

from dicom2nifti.common import get_nifti_data


class Slice(object):
    """
    Class containing all data for a single slice in an image volume
    """
    original_data = None
    slice_orientation = None


class SliceType(object):
    """
    ENUM like container for the slice types
    """
    AXIAL = 1
    SAGITTAL = 2
    CORONAL = 3


class SliceOrientation(object):
    """
    Class containing the orientation of a slice
    """
    x_component = None
    y_component = None
    normal_component = None
    x_inverted = False
    y_inverted = False


def load(nifti_file):
    nifti_image = nibabel.load(nifti_file)
    return ImageVolume(nifti_image)


class ImageVolume(object):
    """
    Class representing an imagevolume.
    You can provide it with a nifti and can be used to get slices in a certain direction
    It will take the affine matrix into account to find the correct orientation
    """

    def __init__(self, nifti_image):
        self.affine = nifti_image.affine
        # assert that it is a 3D image
        self.nifti_data = get_nifti_data(nifti_image).squeeze()
        if self.nifti_data.ndim == 2:
            self.nifti_data = numpy.expand_dims(self.nifti_data, 2)
        if self.nifti_data.ndim != 3:
            assert self.nifti_data.ndim >= 3

        # do some basic processing like setting dimensions and min/max values
        self.dimensions = self.nifti_data.shape
        self.axial_orientation = None
        self.coronal_orientation = None
        self.sagittal_orientation = None
        self.__calculate_slice_orientation__()

    def __calculate_slice_orientation__(self):
        # Not all image data has the same orientation
        # We use the affine matrix and multiplying it with one component
        # of the slice we can find the correct orientation
        affine_inverse = numpy.linalg.inv(self.affine)
        transformed_x = numpy.transpose(numpy.dot(affine_inverse, [[1], [0], [0], [0]]))[0]
        transformed_y = numpy.transpose(numpy.dot(affine_inverse, [[0], [1], [0], [0]]))[0]
        transformed_z = numpy.transpose(numpy.dot(affine_inverse, [[0], [0], [1], [0]]))[0]

        # calculate the most likely x,y,z direction
        x_component, y_component, z_component = __calc_most_likely_direction__(transformed_x,
                                                                               transformed_y,
                                                                               transformed_z)

        # Find slice orientiation for the axial size
        # Find the index of the max component to know which component is the direction in the size
        self.axial_orientation = SliceOrientation()
        self.axial_orientation.normal_component = z_component
        self.axial_orientation.x_component = x_component
        self.axial_orientation.x_inverted = numpy.sign(transformed_x[self.axial_orientation.x_component]) < 0
        self.axial_orientation.y_component = y_component
        self.axial_orientation.y_inverted = numpy.sign(transformed_y[self.axial_orientation.y_component]) < 0
        # Find slice orientiation for the coronal size
        # Find the index of the max component to know which component is the direction in the size
        self.coronal_orientation = SliceOrientation()
        self.coronal_orientation.normal_component = y_component
        self.coronal_orientation.x_component = x_component
        self.coronal_orientation.x_inverted = numpy.sign(transformed_x[self.coronal_orientation.x_component]) < 0
        self.coronal_orientation.y_component = z_component
        self.coronal_orientation.y_inverted = numpy.sign(transformed_z[self.coronal_orientation.y_component]) < 0
        # Find slice orientation for the sagittal size
        # Find the index of the max component to know which component is the direction in the size
        self.sagittal_orientation = SliceOrientation()
        self.sagittal_orientation.normal_component = x_component
        self.sagittal_orientation.x_component = y_component
        self.sagittal_orientation.x_inverted = numpy.sign(transformed_y[self.sagittal_orientation.x_component]) < 0
        self.sagittal_orientation.y_component = z_component
        self.sagittal_orientation.y_inverted = numpy.sign(transformed_z[self.sagittal_orientation.y_component]) < 0
        # Assert that the slice normals are not equal
        assert self.axial_orientation.normal_component != self.coronal_orientation.normal_component
        assert self.coronal_orientation.normal_component != self.sagittal_orientation.normal_component
        assert self.sagittal_orientation.normal_component != self.axial_orientation.normal_component

    def __get_raw_slice__(self, slice_number, slice_orientation, time_point=0):
        # Take the slice out of one of the timepoints of a 4 d nifti
        if len(self.nifti_data.shape) >= 4:
            if slice_orientation.normal_component == 0:
                slice_data = self.nifti_data[slice_number, :, :, time_point]
            elif slice_orientation.normal_component == 1:
                slice_data = self.nifti_data[:, slice_number, :, time_point]
            else:
                slice_data = self.nifti_data[:, :, slice_number, time_point]
        else:
            if slice_orientation.normal_component == 0:
                slice_data = self.nifti_data[slice_number, :, :]
            elif slice_orientation.normal_component == 1:
                slice_data = self.nifti_data[:, slice_number, :]
            else:
                slice_data = self.nifti_data[:, :, slice_number]
        # If the x_component is larger than the y_component we need to flip
        # As a consequence of the retrieval of the data the y component can be first
        # In this case we need to swap x and y
        if slice_orientation.x_component > slice_orientation.y_component:
            slice_data = numpy.swapaxes(slice_data, 0, 1)
        # Flip the numpy direction to display direction (only if needed)
        # Beware: the left right is actually up down in the image
        if not slice_orientation.y_inverted:
            slice_data = numpy.fliplr(slice_data)
        if not slice_orientation.x_inverted:
            slice_data = numpy.flipud(slice_data)
        return slice_data

    def get_slice(self, slice_type, slice_number, time_point=0):
        """
            Returns a slice of the dataset.
            slice.data contains the window/levelled values, in uint8
            slice.original_data contains the original data for this slice
            :param time_point: in case of 4d nifti the 4th dimension
            :param slice_number: the slice number
            :param slice_type: tye slice type (AXIAL, SAGITTAL, CORONAL)
        """
        slice_ = Slice()
        slice_.slice_number = slice_number
        # assert that slice_ number is withing the range
        assert slice_number >= 0
        assert slice_number < self._get_number_of_slices(slice_type)
        slice_data = None
        if slice_type == SliceType.AXIAL:
            slice_data = self.__get_raw_slice__(slice_number, self.axial_orientation, time_point)
            slice_.slice_orientation = self.axial_orientation
        elif slice_type == SliceType.SAGITTAL:
            slice_data = self.__get_raw_slice__(slice_number, self.sagittal_orientation, time_point)
            slice_.slice_orientation = self.sagittal_orientation
        elif slice_type == SliceType.CORONAL:
            slice_data = self.__get_raw_slice__(slice_number, self.coronal_orientation, time_point)
            slice_.slice_orientation = self.coronal_orientation
        # make a copy of the slice_ so we do not modify the orignal
        slice_.original_data = slice_data
        return slice_

    def _get_number_of_slices(self, slice_type):
        """
        Get the number of slices in a certain direction
        """
        if slice_type == SliceType.AXIAL:
            return self.dimensions[self.axial_orientation.normal_component]
        elif slice_type == SliceType.SAGITTAL:
            return self.dimensions[self.sagittal_orientation.normal_component]
        elif slice_type == SliceType.CORONAL:
            return self.dimensions[self.coronal_orientation.normal_component]


def __calc_most_likely_direction__(transformed_x, transformed_y, transformed_z):
    """
    Calculate which is the most likely component for a given direction
    """
    # calculate the x component
    tx_dot_x = numpy.abs(numpy.dot(transformed_x, [1, 0, 0, 0]))
    tx_dot_y = numpy.abs(numpy.dot(transformed_x, [0, 1, 0, 0]))
    tx_dot_z = numpy.abs(numpy.dot(transformed_x, [0, 0, 1, 0]))
    x_dots = [tx_dot_x, tx_dot_y, tx_dot_z]
    x_component = numpy.argmax(x_dots)
    x_max = numpy.max(x_dots)

    # calculate the y component
    ty_dot_x = numpy.abs(numpy.dot(transformed_y, [1, 0, 0, 0]))
    ty_dot_y = numpy.abs(numpy.dot(transformed_y, [0, 1, 0, 0]))
    ty_dot_z = numpy.abs(numpy.dot(transformed_y, [0, 0, 1, 0]))
    y_dots = [ty_dot_x, ty_dot_y, ty_dot_z]
    y_component = numpy.argmax(y_dots)
    y_max = numpy.max(y_dots)

    # calculate the z component
    tz_dot_x = numpy.abs(numpy.dot(transformed_z, [1, 0, 0, 0]))
    tz_dot_y = numpy.abs(numpy.dot(transformed_z, [0, 1, 0, 0]))
    tz_dot_z = numpy.abs(numpy.dot(transformed_z, [0, 0, 1, 0]))
    z_dots = [tz_dot_x, tz_dot_y, tz_dot_z]
    z_component = numpy.argmax(z_dots)
    z_max = numpy.max(z_dots)

    # as long as there are duplicate directions try to correct
    break_counter = 0
    while x_component == y_component or x_component == z_component or y_component == z_component:
        break_counter += 1
        if x_component == y_component:
            # keep the strongest one and change the other
            if x_max >= y_max:  # update the y component
                y_dots[y_component] = 0
                y_component = numpy.argmax(y_dots)
                y_max = numpy.max(y_dots)
            else:  # update the x component
                x_dots[x_component] = 0
                x_component = numpy.argmax(x_dots)
                x_max = numpy.max(x_dots)

        if x_component == z_component:
            # keep the strongest one and change the other
            if x_max >= z_max:  # update the z component
                z_dots[z_component] = 0
                z_component = numpy.argmax(z_dots)
                z_max = numpy.max(z_dots)
            else:  # update the x component
                x_dots[x_component] = 0
                x_component = numpy.argmax(x_dots)
                x_max = numpy.max(x_dots)

        if y_component == z_component:
            # keep the strongest one and change the other
            if y_max >= z_max:  # update the z component
                z_dots[z_component] = 0
                z_component = numpy.argmax(z_dots)
                z_max = numpy.max(z_dots)
            else:  # update the y component
                y_dots[y_component] = 0
                y_component = numpy.argmax(y_dots)
                y_max = numpy.max(y_dots)

        if break_counter >= 10:
            break  # this will only happen in very special scenarios like multiframe survey containing multiple stacks

    return x_component, y_component, z_component
