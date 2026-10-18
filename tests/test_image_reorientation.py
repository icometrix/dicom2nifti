"""Regression tests for reoriented image geometry and temporal metadata."""

import os
import tempfile
import unittest

import nibabel
import numpy

from dicom2nifti.image_reorientation import reorient_image


class TestImageReorientation(unittest.TestCase):
    def setUp(self):
        self.work_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.work_dir.cleanup)
        self.affine = numpy.array([[0, 0, 4, 10],
                                   [-2, 0, 0, 20],
                                   [0, 3, 0, 30],
                                   [0, 0, 0, 1]])

    def _make_image(self, shape, temporal_zoom=3.71, temporal_unit='sec'):
        data = numpy.arange(numpy.prod(shape), dtype=numpy.float32).reshape(shape)
        image = nibabel.Nifti1Image(data, self.affine)
        image.header.set_xyzt_units('mm', temporal_unit)
        if len(shape) == 4:
            image.header.set_zooms((2, 3, 4, temporal_zoom))
        return image, data

    def _assert_geometry(self, image, original_data):
        # Input axes point posterior, superior and right; output axes are LAS.
        axes = (2, 0, 1) if original_data.ndim == 3 else (2, 0, 1, 3)
        expected_data = original_data.transpose(axes)[::-1, ::-1]
        expected_affine = numpy.array([[-4, 0, 0, 22],
                                       [0, 2, 0, 18],
                                       [0, 0, 3, 30],
                                       [0, 0, 0, 1]])
        numpy.testing.assert_array_equal(numpy.asanyarray(image.dataobj), expected_data)
        numpy.testing.assert_allclose(image.affine, expected_affine)
        numpy.testing.assert_allclose(image.header.get_zooms()[:3], (4, 2, 3))
        self.assertEqual(nibabel.aff2axcodes(image.affine), ('L', 'A', 'S'))

    def test_4d_temporal_metadata(self):
        for use_filename in (False, True):
            for temporal_zoom, temporal_unit in ((3.71, 'sec'), (3710, 'msec'), (3.71, 'unknown')):
                with self.subTest(filename=use_filename, unit=temporal_unit):
                    image, data = self._make_image((2, 3, 4, 5), temporal_zoom, temporal_unit)
                    input_image = image
                    if use_filename:
                        input_image = os.path.join(self.work_dir.name, 'input.nii.gz')
                        image.to_filename(input_image)
                    output_path = os.path.join(self.work_dir.name, 'output.nii.gz')

                    output = reorient_image(input_image, output_path)
                    reloaded = nibabel.load(output_path)

                    for result in (output, reloaded):
                        self._assert_geometry(result, data)
                        numpy.testing.assert_allclose(result.header.get_zooms(), (4, 2, 3, temporal_zoom))
                        self.assertEqual(result.header.get_xyzt_units(), ('mm', temporal_unit))

    def test_3d_geometry_and_units(self):
        for use_filename in (False, True):
            with self.subTest(filename=use_filename):
                image, data = self._make_image((2, 3, 4), temporal_unit='msec')
                input_image = image
                if use_filename:
                    input_image = os.path.join(self.work_dir.name, 'input.nii.gz')
                    image.to_filename(input_image)
                output_path = os.path.join(self.work_dir.name, 'output.nii.gz')

                output = reorient_image(input_image, output_path)

                for result in (output, nibabel.load(output_path)):
                    self._assert_geometry(result, data)
                    self.assertEqual(result.header.get_xyzt_units(), ('mm', 'unknown'))

    def test_nifti2_filename_temporal_metadata(self):
        image, data = self._make_image((2, 3, 4, 5))
        image = nibabel.Nifti2Image(data, image.affine)
        image.header.set_zooms((2, 3, 4, 3.71))
        image.header.set_xyzt_units('mm', 'sec')
        input_path = os.path.join(self.work_dir.name, 'nifti2_input.nii')
        output_path = os.path.join(self.work_dir.name, 'nifti2_output.nii.gz')
        image.to_filename(input_path)

        output = reorient_image(input_path, output_path)

        for result in (output, nibabel.load(output_path)):
            self._assert_geometry(result, data)
            numpy.testing.assert_allclose(result.header.get_zooms(), (4, 2, 3, 3.71))
            self.assertEqual(result.header.get_xyzt_units(), ('mm', 'sec'))

    def test_other_image_formats_remain_supported(self):
        data = numpy.arange(120, dtype=numpy.float32).reshape((2, 3, 4, 5))
        affine = numpy.diag([-2, 3, 4, 1])
        for image_class, extension in ((nibabel.AnalyzeImage, '.img'),
                                       (nibabel.MGHImage, '.mgz')):
            with self.subTest(format=image_class.__name__):
                input_path = os.path.join(self.work_dir.name, 'input' + extension)
                output_path = os.path.join(self.work_dir.name, 'converted.nii.gz')
                image_class(data, affine).to_filename(input_path)
                source = nibabel.load(input_path)
                self.assertEqual(nibabel.aff2axcodes(source.affine), ('L', 'A', 'S'))

                output = reorient_image(input_path, output_path)

                for result in (output, nibabel.load(output_path)):
                    numpy.testing.assert_array_equal(numpy.asanyarray(result.dataobj), data)
                    numpy.testing.assert_allclose(result.affine, source.affine)
                    numpy.testing.assert_allclose(result.header.get_zooms(), (2, 3, 4, 1))
                    self.assertEqual(result.header.get_xyzt_units(), ('mm', 'unknown'))

    def test_scaled_file_applies_scaling_once(self):
        image, data = self._make_image((2, 3, 4, 5))
        image.header.set_slope_inter(2, 10)
        input_path = os.path.join(self.work_dir.name, 'scaled_input.nii.gz')
        output_path = os.path.join(self.work_dir.name, 'scaled_output.nii.gz')
        image.to_filename(input_path)

        output = reorient_image(input_path, output_path)
        reloaded = nibabel.load(output_path)

        for result in (output, reloaded):
            self._assert_geometry(result, data * 2 + 10)
            numpy.testing.assert_allclose(result.header.get_zooms(), (4, 2, 3, 3.71))
            self.assertEqual(result.header.get_xyzt_units(), ('mm', 'sec'))
        self.assertEqual(reloaded.dataobj.slope, 1)
        self.assertEqual(reloaded.dataobj.inter, 0)


if __name__ == '__main__':
    unittest.main()
