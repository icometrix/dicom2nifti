import numpy
from nibabel import Nifti1Image

from dicom2nifti.resample import resample_nifti_images


def test_resample():
    z_spacing = 0.45  # In float64: 0.45000000000000001
    nifti = Nifti1Image(
        dataobj=numpy.ones((3, 3, 3)),
        affine=numpy.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, z_spacing, 0],
                [0, 0, 0, 1],
            ]
        ),
    )
    voxel_size = nifti.header.get_zooms()  # Rounds to float32: 0.44999998807907104492
    nifti_out = resample_nifti_images([nifti], voxel_size)
    # shape was (3, 3, 4) before rounding fix in resample_nifti_images()
    assert nifti_out.shape == (3, 3, 3)
