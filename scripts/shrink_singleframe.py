# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
import logging
import os

import pydicom
import pydicom.dataset
from pydicom import dcmread


def _shrink_file(dicom_file_in, subsample_factor):
    """
    Anonimize a single dicomfile
    :param dicom_file_in: filepath for input file
    :param dicom_file_out: filepath for output file
    :param fields_to_keep: dicom tags to keep
    """
    # Default meta_fields
    # Required fields according to reference

    dicom_file_out = dicom_file_in

    # Load dicom_file_in
    dicom_in = dcmread(dicom_file_in)

    # Create new dicom file
    # Set new file meta information
    file_meta = pydicom.dataset.Dataset()
    for key, value in dicom_in.file_meta.items():
        file_meta.add(value)

        # Create the FileDataset instance (initially no data elements, but file_meta supplied)
    dicom_out = pydicom.dataset.FileDataset(dicom_file_out, {}, file_meta=file_meta, preamble=b'\0' * 128)

    # Copy transfer syntax
    dicom_out.is_little_endian = dicom_in.is_little_endian
    dicom_out.is_implicit_VR = dicom_in.is_implicit_VR

    rows = 0
    columns = 0

    # Add the data elements
    for field_key, field_value in dicom_in.items():
        logging.info(field_key)
        if field_key == (0x7fe0, 0x0010):
            pixel_array = dicom_in.pixel_array[::subsample_factor, ::subsample_factor]

            dicom_out.PixelData = pixel_array.tostring()  # = byte array (see pydicom docs)
            rows = pixel_array.shape[1]
            columns = pixel_array.shape[0]
            # noinspection PyPep8Naming
            dicom_out[0x7fe0, 0x0010].VR = 'OB'
        else:
            dicom_out.add(field_value)

    dicom_out.PixelSpacing[0] *= subsample_factor
    dicom_out.PixelSpacing[1] *= subsample_factor
    dicom_out.Rows = rows
    dicom_out.Columns = columns

    # Save dicom_file_out
    # Make sure we have a directory
    if not os.path.exists(os.path.dirname(dicom_file_out)):
        logging.info('Decompressing files')

    # Save the file
    dicom_out.save_as(dicom_file_out, write_like_original=False)


def main():
    _shrink_file('/***/***.dcm',
                 subsample_factor=8)


if __name__ == "__main__":
    main()
