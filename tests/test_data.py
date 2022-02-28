# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import os

__all__ = ['GENERIC_ANATOMICAL', 'GENERIC_ANATOMICAL_IMPLICIT', 'GENERIC_COMPRESSED', 'GENERIC_RGB',
           'GENERIC_COMPRESSED_IMPLICIT', 'GENERIC_NON_ISOTROPIC', 'GE_ANATOMICAL', 'GE_ANATOMICAL_SINGLE_SLICE',
           'GE_ANATOMICAL_IMPLICIT', 'GE_DTI', 'GE_DTI_OLD', 'GE_DTI_IMPLICIT', 'GE_FMRI', 'GE_FMRI_IMPLICIT',
           'PHILIPS_ANATOMICAL', 'PHILIPS_ANATOMICAL_IMPLICIT', 'PHILIPS_DTI', 'PHILIPS_DTI_IMPLICIT',
           'PHILIPS_DTI_002', 'PHILIPS_DTI_IMPLICIT_002', 'PHILIPS_FMRI', 'PHILIPS_FMRI_IMPLICIT',
           'PHILIPS_ENHANCED_ANATOMICAL', 'PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT', 'PHILIPS_ENHANCED_DTI',
           'PHILIPS_ENHANCED_DTI_IMPLICIT', 'PHILIPS_ENHANCED_FMRI', 'PHILIPS_ENHANCED_FMRI_IMPLICIT',
           'SIEMENS_ANATOMICAL', 'SIEMENS_ANATOMICAL_IMPLICIT', 'SIEMENS_DTI', 'SIEMENS_DTI_IMPLICIT',
           'SIEMENS_FMRI', 'SIEMENS_FMRI_IMPLICIT', 'SIEMENS_CLASSIC_DTI', 'SIEMENS_CLASSIC_DTI_IMPLICIT',
           'SIEMENS_CLASSIC_FMRI', 'SIEMENS_CLASSIC_FMRI_IMPLICIT', 'SIEMENS_MULTIFRAME_ANATOMICAL',
           'HITACHI_ANATOMICAL', 'HITACHI_ANATOMICAL_IMPLICIT', 'FAILING_SLICEINCREMENT',
           'FAILING_SLICEINCREMENT_2', 'FAILING_SLICECOUNT', 'FAILING_ORHTOGONAL', 'FAILING_ORIENTATION',
           'FAILING_NOTAVOLUME']

data_root = os.path.dirname(os.path.abspath(__file__))

# GENERIC DATASETS
GENERIC_ANATOMICAL = os.path.join(data_root, 'data', 'generic', 'anatomical', '001')
GENERIC_ANATOMICAL_IMPLICIT = os.path.join(data_root, 'data', 'generic', 'anatomical', '001_implicit')
GENERIC_COMPRESSED = os.path.join(data_root, 'data', 'generic', 'compressed', '001')
GENERIC_RGB = os.path.join(data_root, 'data', 'generic', 'rgb', '001')
GENERIC_COMPRESSED_IMPLICIT = os.path.join(data_root, 'data', 'generic', 'compressed', '001_implicit')
GENERIC_NON_ISOTROPIC = os.path.join(data_root, 'data', 'generic', 'anatomical', '002_non_isotropic')

# GE DATASETS
GE_ANATOMICAL = os.path.join(data_root, 'data', 'ge', 'anatomical', '001')
GE_ANATOMICAL_SINGLE_SLICE = os.path.join(data_root, 'data', 'ge', 'anatomical', '001_single_slice')
GE_ANATOMICAL_IMPLICIT = os.path.join(data_root, 'data', 'ge', 'anatomical', '001_implicit')
GE_DTI = os.path.join(data_root, 'data', 'ge', 'dti', '001')
GE_DTI_OLD = os.path.join(data_root, 'data', 'ge', 'dti', '002')
GE_DTI_IMPLICIT = os.path.join(data_root, 'data', 'ge', 'dti', '001_implicit')
GE_FMRI = os.path.join(data_root, 'data', 'ge', 'fmri', '001')
GE_FMRI_IMPLICIT = os.path.join(data_root, 'data', 'ge', 'fmri', '001_implicit')

# PHILIPS DATASETS
PHILIPS_ANATOMICAL = os.path.join(data_root, 'data', 'philips', 'anatomical', '001')
PHILIPS_ANATOMICAL_IMPLICIT = os.path.join(data_root, 'data', 'philips', 'anatomical', '001_implicit')
PHILIPS_DTI = os.path.join(data_root, 'data', 'philips', 'dti', '001')
PHILIPS_DTI_IMPLICIT = os.path.join(data_root, 'data', 'philips', 'dti', '001_implicit')
PHILIPS_DTI_002 = os.path.join(data_root, 'data', 'philips', 'dti', '002')
PHILIPS_DTI_IMPLICIT_002 = os.path.join(data_root, 'data', 'philips', 'dti', '002_implicit')
PHILIPS_FMRI = os.path.join(data_root, 'data', 'philips', 'fmri', '001')
PHILIPS_FMRI_IMPLICIT = os.path.join(data_root, 'data', 'philips', 'fmri', '001_implicit')

# PHILIPS DATASETS
PHILIPS_ENHANCED_ANATOMICAL = os.path.join(data_root, 'data', 'philips_enhanced', 'anatomical', '001')
PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT = os.path.join(data_root, 'data', 'philips_enhanced', 'anatomical', '001_implicit')
PHILIPS_ENHANCED_DTI = os.path.join(data_root, 'data', 'philips_enhanced', 'dti', '001')
PHILIPS_ENHANCED_DTI_IMPLICIT = os.path.join(data_root, 'data', 'philips_enhanced', 'dti', '001_implicit')
PHILIPS_ENHANCED_FMRI = os.path.join(data_root, 'data', 'philips_enhanced', 'fmri', '001')
PHILIPS_ENHANCED_FMRI_IMPLICIT = os.path.join(data_root, 'data', 'philips_enhanced', 'fmri', '001_implicit')

# SIEMENS DATASETS
SIEMENS_ANATOMICAL = os.path.join(data_root, 'data', 'siemens', 'anatomical', '001')
SIEMENS_ANATOMICAL_IMPLICIT = os.path.join(data_root, 'data', 'siemens', 'anatomical', '001_implicit')
SIEMENS_DTI = os.path.join(data_root, 'data', 'siemens', 'dti', '001')
SIEMENS_DTI_IMPLICIT = os.path.join(data_root, 'data', 'siemens', 'dti', '001_implicit')
SIEMENS_FMRI = os.path.join(data_root, 'data', 'siemens', 'fmri', '001')
SIEMENS_FMRI_IMPLICIT = os.path.join(data_root, 'data', 'siemens', 'fmri', '001_implicit')
SIEMENS_CLASSIC_DTI = os.path.join(data_root, 'data', 'siemens', 'dti_classic', '001')
SIEMENS_CLASSIC_DTI_IMPLICIT = os.path.join(data_root, 'data', 'siemens', 'dti_classic', '001_implicit')
SIEMENS_CLASSIC_FMRI = os.path.join(data_root, 'data', 'siemens', 'fmri_classic', '001')
SIEMENS_CLASSIC_FMRI_IMPLICIT = os.path.join(data_root, 'data', 'siemens', 'fmri_classic', '001_implicit')
SIEMENS_MULTIFRAME_ANATOMICAL = os.path.join(data_root, 'data', 'siemens_multiframe', 'anatomical', '001')

# HITACHI DATASETS
HITACHI_ANATOMICAL = os.path.join(data_root, 'data', 'hitachi', 'anatomical', '001')
HITACHI_ANATOMICAL_IMPLICIT = os.path.join(data_root, 'data', 'hitachi', 'anatomical', '001_implicit')

# FAILING
FAILING_SLICEINCREMENT = os.path.join(data_root, 'data', 'failing', 'sliceincrement', '001')
FAILING_SLICEINCREMENT_2 = os.path.join(data_root, 'data', 'failing', 'sliceincrement', '002')
FAILING_SLICECOUNT = os.path.join(data_root, 'data', 'failing', 'slicecount', '001')
FAILING_ORHTOGONAL = os.path.join(data_root, 'data', 'failing', 'gantrytilting', '001')
FAILING_ORIENTATION = os.path.join(data_root, 'data', 'failing', 'sliceorientation', '001')
FAILING_NOTAVOLUME = os.path.join(data_root, 'data', 'failing', 'notavolume', '001')