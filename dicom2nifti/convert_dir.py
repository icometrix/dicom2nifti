# -*- coding: utf-8 -*-
"""
this module houses all the code to just convert a directory of random dicom files

@author: abrys
"""
import dicom2nifti.compressed_dicom as compressed_dicom

import gc
import os
import re
import traceback
import unicodedata

from pydicom.tag import Tag

import logging

import dicom2nifti.common as common
import dicom2nifti.convert_dicom as convert_dicom
import dicom2nifti.settings
from experimental import utils

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("dicom2nifti.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def convert_directory(
        dicom_directory,
        output_folder,
        compression=True,
        reorient=True):
    """
    This function will order all dicom files by series and order them one by one

    :param compression: enable or disable gzip compression
    :param reorient: reorient the dicoms according to LAS orientation
    :param output_folder: folder to write the nifti files to
    :param dicom_directory: directory with dicom files
    """
    # sort dicom files by series uid
    dicom_series = {}
    for root, _, files in os.walk(dicom_directory):
        for dicom_file in files:
            file_path = os.path.join(root, dicom_file)
            # noinspection PyBroadException
            try:
                if compressed_dicom.is_dicom_file(file_path):
                    # read the dicom as fast as possible
                    # (max length for SeriesInstanceUID is 64 so defer_size 100 should be ok)

                    dicom_headers = compressed_dicom.read_file(
                        file_path,
                        defer_size="1 KB",
                        stop_before_pixels=False,
                        force=dicom2nifti.settings.pydicom_read_force)
                    if not _is_valid_imaging_dicom(dicom_headers):
                        logger.info("Skipping: %s" % file_path)
                        continue
                    logger.info("Organizing: %s" % file_path)
                    if dicom_headers.SeriesInstanceUID not in dicom_series:
                        dicom_series[dicom_headers.SeriesInstanceUID] = []
                    dicom_series[dicom_headers.SeriesInstanceUID].append(
                        {'dicom': dicom_headers, 'dicom_file_path': file_path})
            except BaseException:  # Explicitly capturing all errors here to be able to continue processing all the rest
                logger.warning("Unable to read: %s" % file_path)
                traceback.print_exc()

    # further divide one series into multiple sub-series by sequence_name
    series_new = {}
    for series_id, entries in dicom_series.items():
        dicoms = [entry['dicom'] for entry in entries]
        if 'SequenceName' in dicoms[0]:
            sequence_names = list(
                set([dicom.SequenceName for dicom in dicoms]))
            if len(sequence_names) == 1:
                series_new[series_id] = entries
            else:
                for ii, sequence_name in enumerate(sequence_names):
                    series_new['%s.%d' % (series_id, ii)] = [entries[ii] for ii, dicom in enumerate(
                        dicoms) if dicom.SequenceName == sequence_name]
        else:
            series_new[series_id] = entries
    dicom_series = series_new
    # start converting one by one
    for _, entries in dicom_series.items():
        dicom_input = [entry['dicom'] for entry in entries]
        dicom_file_paths = [entry['dicom_file_path'] for entry in entries]
        base_filename = ""
        # noinspection PyBroadException
        try:
            # construct the filename for the nifti
            base_filename = ""
            if 'SeriesNumber' in dicom_input[0]:
                base_filename = _remove_accents_(
                    'series_number@%s' %
                    dicom_input[0].SeriesNumber)
                if 'SeriesDescription' in dicom_input[0]:
                    base_filename = _remove_accents_(
                        '%s@series_description@%s' %
                        (base_filename, dicom_input[0].SeriesDescription))
                if 'SequenceName' in dicom_input[0]:
                    base_filename = _remove_accents_(
                        '%s@sequence_name@%s' %
                        (base_filename, dicom_input[0].SequenceName))
                if 'ProtocolName' in dicom_input[0]:
                    base_filename = _remove_accents_(
                        '%s@protocol_name@%s' %
                        (base_filename, dicom_input[0].ProtocolName))
            else:
                base_filename = _remove_accents_(
                    dicom_input[0].SeriesInstanceUID)
            logger.info('--------------------------------------------')
            logger.info('Start converting %s' % base_filename)

            if compression:
                nifti_file = os.path.join(
                    output_folder, base_filename + '.nii.gz')
            else:
                nifti_file = os.path.join(
                    output_folder, base_filename + '.nii')
            convert_dicom.dicom_array_to_nifti(
                dicom_input, nifti_file, reorient)

            # record dicom tags in json
            json_out = {'dicoms': [], 'nifti': nifti_file}
            for dicom, dicom_file_path in zip(dicom_input, dicom_file_paths):
                dicom = utils.convert_dicom_value(dicom)
                dicom.pop('PixelData')
                dicom.update({'dicom_file_path': dicom_file_path})
                json_out['dicoms'].append(dicom)
            utils.dump_json(
                json_out,
                os.path.join(
                    output_folder,
                    base_filename +
                    '.json'))

            gc.collect()
        except Exception as exception:  # Explicitly capturing app exceptions here to be able to continue processing
            logger.info("Unable to convert: %s" % base_filename)
            if str(exception) not in [
                'TOO_FEW_SLICES/LOCALIZER',
                "MISSING_DICOM_FILES",
                    "SLICE_INCREMENT_INCONSISTENT"]:
                traceback.print_exc()


def _is_valid_imaging_dicom(dicom_header):
    """
    Function will do some basic checks to see if this is a valid imaging dicom
    """
    # if it is philips and multiframe dicom then we assume it is ok
    try:
        if common.is_hyperfine([dicom_header]):
            return True

        if common.is_philips([dicom_header]):
            if common.is_multiframe_dicom([dicom_header]):
                return True

        if "SeriesInstanceUID" not in dicom_header:
            return False

        if "InstanceNumber" not in dicom_header:
            return False

        if "ImageOrientationPatient" not in dicom_header or len(
                dicom_header.ImageOrientationPatient) < 6:
            return False

        if "ImagePositionPatient" not in dicom_header or len(
                dicom_header.ImagePositionPatient) < 3:
            return False

        # for all others if there is image position patient we assume it is ok
        if Tag(0x0020, 0x0037) not in dicom_header:
            return False

        return True
    except (KeyError, AttributeError):
        return False


def _remove_accents(unicode_filename):
    """
    Function that will try to remove accents from a unicode string to be used in a filename.
    input filename should be either an ascii or unicode string
    """
    # noinspection PyBroadException
    try:
        unicode_filename = unicode_filename.replace(" ", "_")
        cleaned_filename = unicodedata.normalize(
            'NFKD', unicode_filename).encode(
            'ASCII', 'ignore').decode('ASCII')

        cleaned_filename = re.sub(
            r'[^\w\s-]', '', cleaned_filename.strip().lower())
        cleaned_filename = re.sub(r'[-\s]+', '-', cleaned_filename)

        return cleaned_filename
    except BaseException:
        traceback.print_exc()
        return unicode_filename


def _remove_accents_(unicode_filename):
    """
    Function that will try to remove accents from a unicode string to be used in a filename.
    input filename should be either an ascii or unicode string
    """
    unicode_filename = unicode_filename.replace(" ", "_")
    unicode_filename = unicode_filename.strip().lower()
    valid_characters = bytes(b'@-_.()1234567890abcdefghijklmnopqrstuvwxyz')
    cleaned_filename = unicodedata.normalize(
        'NFKD', unicode_filename).encode(
        'ASCII', 'ignore')

    new_filename = ""

    for char_int in bytes(cleaned_filename):
        char_byte = bytes([char_int])
        if char_byte in valid_characters:
            new_filename += char_byte.decode()

    return new_filename
