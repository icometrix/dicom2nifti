# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""
from .settings import Dicom2NiftiSettings as settings
from .convert_dicom import dicom_series_to_nifti
from .convert_dir import convert_directory

from .patch_pydicom_encodings import apply as apply_pydicom_encodings_patch
apply_pydicom_encodings_patch()
