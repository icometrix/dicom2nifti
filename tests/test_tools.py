import os
import logging
import tempfile

import nibabel
import numpy
import shutil

import dicom2nifti.image_reorientation as image_reorientation
from dicom2nifti.common import get_nifti_data


def ground_thruth_filenames(input_dir):
    nifti_file = input_dir + '_ground_truth.nii.gz'
    reoriented_nifti_file = input_dir + '_ground_truth_reoriented.nii.gz'
    bval_file = input_dir + '_ground_truth.bval'
    bvec_file = input_dir + '_ground_truth.bvec'
    return nifti_file, reoriented_nifti_file, bval_file, bvec_file


def assert_compare_nifti(nifti_file_1, nifti_file_2):
    logging.info("%s %s" % (nifti_file_1, nifti_file_2))
    work_dir = tempfile.mkdtemp()
    try:
        tmp_nifti_file_1 = os.path.join(work_dir, os.path.basename(nifti_file_1))
        tmp_nifti_file_2 = os.path.join(work_dir, os.path.basename(nifti_file_2))
        image_reorientation.reorient_image(nifti_file_1, tmp_nifti_file_1)
        image_reorientation.reorient_image(nifti_file_2, tmp_nifti_file_2)
        nifti_1 = nibabel.load(tmp_nifti_file_1)
        nifti_2 = nibabel.load(tmp_nifti_file_2)

        # check the affine
        if not numpy.allclose(nifti_1.affine, nifti_2.affine):
            raise Exception('affine mismatch')

        # check the data
        nifti_1_data = get_nifti_data(nifti_1)
        nifti_2_data = get_nifti_data(nifti_2)

        # in case of rgba data we should stack the data again
        if nifti_1.get_data_dtype() == [('R', 'u1'), ('G', 'u1'), ('B', 'u1'), ('A', 'u1')]:
            nifti_1_data = numpy.stack([nifti_1_data['R'], nifti_1_data['G'], nifti_1_data['B'], nifti_1_data['A']])
        if nifti_2.get_data_dtype() == [('R', 'u1'), ('G', 'u1'), ('B', 'u1'), ('A', 'u1')]:
            nifti_2_data = numpy.stack([nifti_2_data['R'], nifti_2_data['G'], nifti_2_data['B'], nifti_2_data['A']])
            
        if nifti_1.get_data_dtype() != nifti_2.get_data_dtype():
            raise Exception(f'dtype mismatch {nifti_1.get_data_dtype()} <> {nifti_2.get_data_dtype()}')
        if not numpy.allclose(nifti_1_data, nifti_2_data, rtol=0.01, atol=1):
            difference = get_nifti_data(nifti_1) - get_nifti_data(nifti_2)
            raise Exception('data mismatch %s ' % numpy.max(numpy.abs(difference)))

    except:
        shutil.rmtree(work_dir)
        raise


def assert_compare_bval(bval_file_1, bval_file_2):
    bval_1 = numpy.loadtxt(bval_file_1)
    bval_2 = numpy.loadtxt(bval_file_2)
    equal = numpy.allclose(bval_1, bval_2)
    if not equal:
        raise Exception('bvals not equal\n%s\n%s' %(numpy.array2string(bval_1), numpy.array2string(bval_2)))


def assert_compare_bvec(bvec_file_1, bvec_file_2):
    bvec_1 = numpy.loadtxt(bvec_file_1)
    bvec_2 = numpy.loadtxt(bvec_file_2)
    equal = numpy.allclose(bvec_1, bvec_2)
    if not equal:
        raise Exception('bvecs not equal\n%s\n%s' %(numpy.array2string(bvec_1), numpy.array2string(bvec_2)))
