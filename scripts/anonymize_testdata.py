# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import datetime
import logging
import os

import numpy
import pydicom
import pydicom.dataset
import pydicom.uid
from pydicom import dcmread

import common
from dicom2nifti.common import read_dicom_directory, is_philips, is_siemens, is_ge


def anonymize_directory(input_directory, output_directory=None):
    if output_directory is None:
        output_directory = input_directory

    study_uid = pydicom.uid.generate_uid()
    series_uid = pydicom.uid.generate_uid()
    date = datetime.datetime.now().strftime("%Y%m%d")
    time = datetime.datetime.now().strftime("%H%M%S.000000")

    fields_to_keep = {'SpecificCharacterSet': None,
                      'ImageType': None,
                      'AcquisitionMatrix': None,
                      'SOPClassUID': None,
                      'SOPInstanceUID': None,  # Will be replaced by file-unique UID
                      'StudyDate': date,
                      'SeriesDate': date,
                      'AcquisitionDate': date,
                      'ContentDate': date,
                      'StudyTime': time,
                      'AcquisitionTime': time,
                      'AcquisitionNumber': None,
                      'Modality': None,
                      'Manufacturer': None,
                      'ManufacturersModelName': None,
                      'PatientName': 'dicom2nifti',
                      'PatientID': 'dicom2nifti',
                      'PatientsBirthDate': date,
                      'PatientsSex': None,
                      'PatientsAge': '0Y',
                      'PatientPosition': None,
                      'ScanningSequence': None,
                      'SequenceVariant': None,
                      'MRAcquisitionType': None,
                      'SequenceName': 'dicom2nifti',
                      'RepetitionTime': None,
                      'EchoTime': None,
                      'InversionTime': None,
                      'DeviceSerialNumber': '1234',
                      'StudyInstanceUID': study_uid,
                      'SeriesInstanceUID': series_uid,
                      'StudyID': 'dicom2nifti',
                      'SeriesNumber': None,
                      'InstanceNumber': None,
                      'ImagePositionPatient': None,
                      'ImageOrientationPatient': None,
                      'SliceLocation': None,
                      'PhotometricInterpretation': None,
                      'PlanarConfiguration': None,
                      'Rows': None,
                      'Columns': None,
                      'PixelSpacing': None,
                      'BitsAllocated': None,
                      'BitsStored': None,
                      'HighBit': None,
                      'RescaleSlope': None,
                      'RescaleIntercept': None,
                      'PixelRepresentation': None,
                      'NumberOfFrames': None,
                      'SamplesPerPixel': None,
                      'SpacingBetweenSlices': None,
                      'PerFrameFunctionalGroupsSequence': None,
                      'SharedFunctionalGroupsSequence': None,
                      # Pixel Data must be specified with hex code as it will not work for compressed dicoms
                      (0x7fe0, 0x0010): None}

    if is_philips(read_dicom_directory(input_directory)):
        philips_fields = {
            (0x2001, 0x100a): None,
            (0x2001, 0x1003): None,
            (0x2001, 0x105f): None,
            (0x2005, 0x100d): None,
            (0x2005, 0x100e): None,
            (0x2005, 0x10b0): None,
            (0x2005, 0x10b1): None,
            (0x2005, 0x10b2): None,
            (0x0018, 0x9087): None,
            (0x0018, 0x9089): None,
            (0x5200, 0x9230): None,
            'SharedFunctionalGroupsSequence': None}
        fields_to_keep.update(philips_fields)

    if is_siemens(read_dicom_directory(input_directory)):
        siemens_fields = {(0x0019, 0x100c): None,
                          (0x0029, 0x1020): None,
                          (0x0051, 0x100b): None,
                          (0x0019, 0x100e): None}
        fields_to_keep.update(siemens_fields)

    if is_ge(read_dicom_directory(input_directory)):
        ge_fields = {(0x0020, 0x9056): None,
                     (0x0020, 0x9057): None,
                     (0x0043, 0x1039): None,
                     (0x0019, 0x10bb): None,
                     (0x0019, 0x10bc): None,
                     (0x0019, 0x10bd): None}
        fields_to_keep.update(ge_fields)

    _anonymize_files(input_directory, output_directory, fields_to_keep)


def _anonymize_file(dicom_file_in, dicom_file_out, fields_to_keep):
    """
    Anonimize a single dicomfile
    :param dicom_file_in: filepath for input file
    :param dicom_file_out: filepath for output file
    :param fields_to_keep: dicom tags to keep
    """
    # Default meta_fields
    # Required fields according to reference

    meta_fields = ['MediaStorageSOPClassUID',
                   'MediaStorageSOPInstanceUID',
                   'ImplementationClassUID']

    # Load dicom_file_in
    dicom_in = dcmread(dicom_file_in)

    # Create new dicom file
    # Set new file meta information
    file_meta = pydicom.dataset.Dataset()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    for field_key in meta_fields:
        file_meta.add(dicom_in.file_meta.data_element(field_key))

        # Create the FileDataset instance (initially no data elements, but file_meta supplied)
    dicom_out = pydicom.dataset.FileDataset(dicom_file_out, {}, file_meta=file_meta, preamble=b'\0' * 128)

    # Copy transfer syntax
    dicom_out.is_little_endian = dicom_in.is_little_endian
    dicom_out.is_implicit_VR = dicom_in.is_implicit_VR

    # Add the data elements
    for field_key, field_value in fields_to_keep.items():
        logging.info(field_key)
        if field_key == (0x7fe0, 0x0010):

            # anonimize the dicom pixeldata
            random_data = numpy.random.randint(0, 255, dicom_in.pixel_array.shape).astype(dicom_in.pixel_array.dtype)
            dicom_out.PixelData = random_data.tobytes()  # = byte array (see pydicom docs)

            # dicom_out.PixelData = dicom_in.pixel_array.tostring()  # = byte array (see pydicom docs)

            # noinspection PyPep8Naming
            dicom_out[0x7fe0, 0x0010].VR = 'OB'
        elif field_value is None:
            try:
                if isinstance(field_key, str):
                    if field_key in dicom_in:
                        dicom_out.add(dicom_in.data_element(field_key))
                else:
                    if dicom_in.get(field_key) is not None:
                        dicom_out.add(dicom_in[field_key])
            except KeyError:
                logging.info('Warning: %s not found' % field_key)
        else:
            setattr(dicom_out, field_key, field_value)

    # Save dicom_file_out
    # Make sure we have a directory
    if not os.path.exists(os.path.dirname(dicom_file_out)):
        logging.info('Decompressing files')

        # Save the file
        dicom_out.is_little_endian = True
    dicom_out.is_implicit_VR = False

    dicom_out.save_as(dicom_file_out, write_like_original=False)


def _anonymize_files(dicom_directory_in, dicom_directory_out, fields_to_keep):
    """
    See anonymize_file for more information.

    series_UID and instance_UID will create a new UID respectively for the series for each directory or for the
    instance for each file. Note that for a multi-series dataset it is thus required that each series is in its own
    directory.

    """

    # Make sure we have absolute paths
    dicom_directory_in = os.path.abspath(dicom_directory_in)
    dicom_directory_out = os.path.abspath(dicom_directory_out)

    # looping over all files
    for root, _, file_names in os.walk(dicom_directory_in):
        # New directory

        for file_name in file_names:
            # Create instance_UID
            fields_to_keep['SOPInstanceUID'] = pydicom.uid.generate_uid()

            dicom_file_in = os.path.join(root, file_name)
            current_dir = root[len(dicom_directory_in) + 1:]
            dicom_file_out = os.path.join(dicom_directory_out, current_dir, file_name)
            if common.is_dicom_file(dicom_file_in):
                logging.info("Processing " + dicom_file_in)
                _anonymize_file(dicom_file_in, dicom_file_out, fields_to_keep)
            else:
                logging.info("Skipping " + dicom_file_in + ", no dicom file")

if __name__ == '__main__':
    anonymize_directory('/Users/abrys/Downloads/dicom_download',
                        '/Users/abrys/Downloads/dicom_download_2')
