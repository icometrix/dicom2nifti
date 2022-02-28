import argparse
import difflib
import logging
import os
import sys

from .convert_dir import convert_directory
from .settings import Dicom2NiftiSettings as settings
from dicom2nifti.compressed_dicom import read_file


def dicom2nifti(args=None):
    args = sys.argv[1:] if args is None else args

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description='dicom2nifti, convert dicom files into nifti format.')
    parser.add_argument('input_directory', type=str,
                        help='directory containing dicom files, can be nested')
    parser.add_argument('output_directory', type=str,
                        help='directory to store the nifti files')

    parser.add_argument('-G', '--allow-gantry-tilting', action='store_true',
                        help='allow the conversion of gantry tilted data (this will be reflected in the affine '
                             'matrix only unless resampling is enabled)')

    parser.add_argument('-I', '--allow-inconsistent-slice-increment', action='store_true',
                        help='allow the conversion of inconsistent slice increment data (this will result '
                             'in distorted images unless resampling is enabled)')

    parser.add_argument('-S', '--allow-single-slice', action='store_true',
                        help='allow the conversion of a single slice (2D image)')

    parser.add_argument('-r', '--resample', action='store_true',
                        help='resample gantry tilted data to an orthogonal image or inconsistent slice '
                             'increment data to a uniform image')

    parser.add_argument('-o', '--resample-order', type=int,
                        help='order of the spline interpolation used during the resampling (0 -> 5) '
                             '[0 = NN, 1 = LIN, ....]')

    parser.add_argument('-p', '--resample-padding', type=int,
                        help='padding value to used during resampling to use as fill value')

    parser.add_argument('-M', '--allow-multiframe-implicit', action='store_true',
                        help='allow the conversion of multiframe data with implicit vr transfer syntax '
                             '(this is not guaranteed to work)')

    parser.add_argument('-C', '--no-compression', action='store_true',
                        help='disable gzip compression and write .nii files instead of .nii.gz')

    parser.add_argument('-R', '--no-reorientation', action='store_true',
                        help='disable image reorientation (default: images are reoriented to LAS orientation)')

    args = parser.parse_args(args)

    if not os.path.isdir(args.input_directory):
        logging.info('ERROR: \'input_directory\' should be a valid path')
        logging.info('----------------------------------------------------\n')
        parser.print_help()
        return 2
    elif not os.path.isdir(args.output_directory):
        logging.info('ERROR: \'output_directory\' should be a valid path')
        logging.info('----------------------------------------------------\n')
        parser.print_help()
        return 2
    else:
        if args.allow_gantry_tilting:
            settings.disable_validate_orthogonal()
        if args.allow_multiframe_implicit:
            settings.disable_validate_multiframe_implicit()
        if args.allow_single_slice:
            settings.disable_validate_slicecount()
        if args.resample:
            settings.enable_resampling()
        if args.resample_order:
            settings.set_resample_spline_interpolation_order(args.resample_order)
        if args.resample_padding:
            settings.set_resample_padding(args.resample_padding)
        convert_directory(args.input_directory, args.output_directory,
                          not args.no_compression, not args.no_reorientation)


def dicomdiff(args):
    """ Shows the fields that differ between two DICOM images.

    Inspired by https://code.google.com/p/pydicom/source/browse/source/dicom/examples/DicomDiff.py
    """
    args = sys.argv[1:] if args is None else args
    parser = argparse.ArgumentParser(description='dicomdiff, show fields that differ between two DICOM images.')
    parser.add_argument('file1', type=str, metavar='FILE1', help='first file to compare')
    parser.add_argument('file2', type=str, metavar='FILE2', help='second file to compare')
    parsed_args = parser.parse_args(args)

    datasets = read_file(parsed_args.file1), read_file(parsed_args.file2)

    rep = []
    for dataset in datasets:
        lines = (str(dataset.file_meta)+"\n"+str(dataset)).split('\n')
        lines = [line + '\n' for line in lines]  # add the newline to the end
        rep.append(lines)

    diff = difflib.Differ()
    for line in diff.compare(rep[0], rep[1]):
        if (line[0] == '+') or (line[0] == '-'):
            sys.stdout.write(line)
