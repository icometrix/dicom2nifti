# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import nibabel
import nibabel.affines
import numpy
import scipy.ndimage

from dicom2nifti.common import get_nifti_data
from dicom2nifti import settings


def resample_single_nifti(input_image, output_nifti):
    """
    Resample a gantry tilted image in place
    """
    # read the input image
    output_image = resample_nifti_images([input_image])
    output_image.header.set_slope_inter(1, 0)
    output_image.header.set_xyzt_units(2)  # set units for xyz (leave t as unknown)
    output_image.to_filename(output_nifti)
    return output_image


def resample_nifti_images(nifti_images, voxel_size=None):
    """
    In this function we will create an orthogonal image and resample the original images to this space

    In this calculation we work in 3 spaces / coordinate systems

    - original image coordinates
    - world coordinates
    - "projected" coordinates

    This last one is a new rotated "orthogonal" coordinates system in mm where
    x and y are perpendicular with the x and y or the image

    We do the following steps
    - calculate a new "projection" coordinate system
    - calculate the world coordinates of all corners of the image in world coordinates
    - project the world coordinates of the corners on the projection coordinate system
    - calculate the min and max corners to get the orthogonal bounding box of the image in projected space
    - translate the origin back to world coordinages

    We now have the new xyz axis, origin and size and can create the new affine used for resampling
    """

    # get the smallest voxelsize and use that
    if voxel_size is None:
        voxel_size = nifti_images[0].header.get_zooms()
        for nifti_image in nifti_images[1:]:
            voxel_size = numpy.minimum(voxel_size, nifti_image.header.get_zooms())

    x_axis_world = numpy.transpose(numpy.dot(nifti_images[0].affine, [[1], [0], [0], [0]]))[0, :3]
    y_axis_world = numpy.transpose(numpy.dot(nifti_images[0].affine, [[0], [1], [0], [0]]))[0, :3]
    x_axis_world /= numpy.linalg.norm(x_axis_world)  # normalization
    y_axis_world /= numpy.linalg.norm(y_axis_world)  # normalization
    z_axis_world = numpy.cross(y_axis_world, x_axis_world)
    z_axis_world /= numpy.linalg.norm(z_axis_world)  # calculate new z
    y_axis_world = numpy.cross(x_axis_world, z_axis_world)  # recalculate y in case x and y where not perpendicular
    y_axis_world /= numpy.linalg.norm(y_axis_world)

    points_world = []

    for nifti_image in nifti_images:
        original_size = nifti_image.shape

        points_image = [[0, 0, 0],
                        [original_size[0] - 1, 0, 0],
                        [0, original_size[1] - 1, 0],
                        [original_size[0] - 1, original_size[1] - 1, 0],
                        [0, 0, original_size[2] - 1],
                        [original_size[0] - 1, 0, original_size[2] - 1],
                        [0, original_size[1] - 1, original_size[2] - 1],
                        [original_size[0] - 1, original_size[1] - 1, original_size[2] - 1]]

        for point in points_image:
            points_world.append(numpy.transpose(numpy.dot(nifti_image.affine,
                                                          [[point[0]], [point[1]], [point[2]], [1]]))[0, :3])

    projections = []
    for point in points_world:
        projection = [numpy.dot(point, x_axis_world),
                      numpy.dot(point, y_axis_world),
                      numpy.dot(point, z_axis_world)]
        projections.append(projection)

    projections = numpy.array(projections)

    min_projected = numpy.amin(projections, axis=0)
    max_projected = numpy.amax(projections, axis=0)
    new_size_mm = max_projected - min_projected

    origin = min_projected[0] * x_axis_world + \
             min_projected[1] * y_axis_world + \
             min_projected[2] * z_axis_world

    new_voxelsize = voxel_size
    new_shape_float = new_size_mm / new_voxelsize + 1
    new_shape = numpy.ceil(
        numpy.round(new_shape_float, decimals=2)  # Floor values below 0.005
    ).astype(numpy.int16)

    new_affine = _create_affine(x_axis_world, y_axis_world, z_axis_world, origin, voxel_size)

    # Resample each image
    combined_image_data = numpy.full(new_shape, settings.resample_padding,
                                     dtype=get_nifti_data(nifti_images[0]).dtype)
    for nifti_image in nifti_images:
        image_affine = nifti_image.affine
        combined_affine = numpy.linalg.inv(new_affine).dot(image_affine)
        matrix, offset = nibabel.affines.to_matvec(numpy.linalg.inv(combined_affine))
        resampled_image = scipy.ndimage.affine_transform(get_nifti_data(nifti_image),
                                                         matrix=matrix,
                                                         offset=offset,
                                                         output_shape=new_shape,
                                                         output=get_nifti_data(nifti_image).dtype,
                                                         order=settings.resample_spline_interpolation_order,
                                                         mode='constant',
                                                         cval=settings.resample_padding,
                                                         prefilter=False)
        combined_image_data[combined_image_data == settings.resample_padding] = \
            resampled_image[combined_image_data == settings.resample_padding]

    if combined_image_data.ndim > 3:  # do not squeeze single slice data
        combined_image_data = combined_image_data.squeeze()
    return nibabel.Nifti1Image(combined_image_data, new_affine)


def _create_affine(x_axis, y_axis, z_axis, image_pos, voxel_sizes):
    """
    Function to generate the affine matrix for a dicom series
    This method was based on (http://nipy.org/nibabel/dicom/dicom_orientation.html)

    :param sorted_dicoms: list with sorted dicom files
    """

    # Create affine matrix (http://nipy.sourceforge.net/nibabel/dicom/dicom_orientation.html#dicom-slice-affine)

    affine = numpy.array(
        [[x_axis[0] * voxel_sizes[0], y_axis[0] * voxel_sizes[1], z_axis[0] * voxel_sizes[2], image_pos[0]],
         [x_axis[1] * voxel_sizes[0], y_axis[1] * voxel_sizes[1], z_axis[1] * voxel_sizes[2], image_pos[1]],
         [x_axis[2] * voxel_sizes[0], y_axis[2] * voxel_sizes[1], z_axis[2] * voxel_sizes[2], image_pos[2]],
         [0, 0, 0, 1]])
    return affine
