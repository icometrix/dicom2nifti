# To ignore numpy errors:
#     pylint: disable=E1101
# icoMetrix DICOM-related utilities


import difflib
import sys

import pydicom
from pydicom import dcmread


def dicom_diff(file1, file2):
    """ Shows the fields that differ between two DICOM images.

    Inspired by https://code.google.com/p/pydicom/source/browse/source/dicom/examples/DicomDiff.py
    """

    datasets = dcmread(file1), dcmread(file2)

    rep = []

    for dataset in datasets:
        lines = (str(dataset.file_meta)+"\n"+str(dataset)).split('\n')
        lines = [line + '\n' for line in lines]  # add the newline to the end
        rep.append(lines)

    diff = difflib.Differ()
    for line in diff.compare(rep[0], rep[1]):
        if (line[0] == '+') or (line[0] == '-'):
            sys.stdout.write(line)
