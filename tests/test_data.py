# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

import os

# GENERIC DATASETS
GENERIC_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'generic', 'anatomical', '001')
GENERIC_ANATOMICAL_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'data', 'generic', 'anatomical', '001_implicit')
GENERIC_COMPRESSED = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'generic', 'compressed', '001')
GENERIC_COMPRESSED_JPEG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       'data', 'generic', 'compressed_jpeg', '001')
GENERIC_COMPRESSED_J2K = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'data', 'generic', 'compressed_j2k', '001')
GENERIC_COMPRESSED_JPEGLS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         'data', 'generic', 'compressed_jpegls', '001')
GENERIC_COMPRESSED_RLE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'data', 'generic', 'compressed_rle', '001')
GENERIC_RGB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'data', 'generic', 'rgb', '001')
GENERIC_COMPRESSED_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'data', 'generic', 'compressed', '001_implicit')
GENERIC_NON_ISOTROPIC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'data', 'generic', 'anatomical', '002_non_isotropic')

# GE DATASETS
GE_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'data', 'ge', 'anatomical', '001')

GE_ANATOMICAL_SINGLE_SLICE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          'data', 'ge', 'anatomical', '001_single_slice')

GE_ANATOMICAL_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'data', 'ge', 'anatomical', '001_implicit')

GE_DTI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'data', 'ge', 'dti', '001')

GE_DTI_OLD = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'data', 'ge', 'dti', '002')

GE_DTI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'data', 'ge', 'dti', '001_implicit')

GE_FMRI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'data', 'ge', 'fmri', '001')

GE_FMRI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'data', 'ge', 'fmri', '001_implicit')

# PHILIPS DATASETS
PHILIPS_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'philips', 'anatomical', '001')

PHILIPS_ANATOMICAL_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'data', 'philips', 'anatomical', '001_implicit')
# icometrix/dicom2nifti#136 dataset containing both magnitude and phase encoded images
PHILIPS_ANATOMICAL_SWI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'data', 'philips', 'anatomical', '002')

PHILIPS_DTI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'data', 'philips', 'dti', '001')

PHILIPS_DTI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'data', 'philips', 'dti', '001_implicit')

PHILIPS_DTI_002 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'data', 'philips', 'dti', '002')

PHILIPS_DTI_IMPLICIT_002 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        'data', 'philips', 'dti', '002_implicit')

PHILIPS_FMRI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'data', 'philips', 'fmri', '001')

PHILIPS_FMRI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'data', 'philips', 'fmri', '001_implicit')

# PHILIPS DATASETS
PHILIPS_ENHANCED_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'data', 'philips_enhanced', 'anatomical', '001')

PHILIPS_ENHANCED_ANATOMICAL_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    'data', 'philips_enhanced', 'anatomical', '001_implicit')

PHILIPS_ENHANCED_DTI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'data', 'philips_enhanced', 'dti', '001')

PHILIPS_ENHANCED_DTI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             'data', 'philips_enhanced', 'dti', '001_implicit')

PHILIPS_ENHANCED_FMRI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'data', 'philips_enhanced', 'fmri', '001')

PHILIPS_ENHANCED_FMRI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'data', 'philips_enhanced', 'fmri', '001_implicit')

# SIEMENS DATASETS
SIEMENS_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'siemens', 'anatomical', '001')

SIEMENS_ANATOMICAL_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'data', 'siemens', 'anatomical', '001_implicit')

SIEMENS_DTI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'data', 'siemens', 'dti', '001')

SIEMENS_DTI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'data', 'siemens', 'dti', '001_implicit')

SIEMENS_FMRI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'data', 'siemens', 'fmri', '001')

SIEMENS_FMRI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'data', 'siemens', 'fmri', '001_implicit')

SIEMENS_CLASSIC_DTI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'data', 'siemens', 'dti_classic', '001')

SIEMENS_CLASSIC_DTI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            'data', 'siemens', 'dti_classic', '001_implicit')

SIEMENS_CLASSIC_FMRI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'data', 'siemens', 'fmri_classic', '001')

SIEMENS_CLASSIC_FMRI_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             'data', 'siemens', 'fmri_classic', '001_implicit')

SIEMENS_MULTIFRAME_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             'data', 'siemens_multiframe', 'anatomical', '001')

# HITACHI DATASETS
HITACHI_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'hitachi', 'anatomical', '001')

HITACHI_ANATOMICAL_IMPLICIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'data', 'hitachi', 'anatomical', '001_implicit')

# HYPERFINE DATASETS
HYPERFINE_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'data', 'hyperfine', 'anatomical', '001')

# HYPERFINE DATASETS
SIRONA_MULTIFRAME_ANATOMICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            'data', 'sirona_multiframe', 'anatomical', '001')

# FAILING
FAILING_SLICEINCREMENT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'data', 'failing', 'sliceincrement', '001')

FAILING_SLICEINCREMENT_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        'data', 'failing', 'sliceincrement', '002')

FAILING_SLICECOUNT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'failing', 'slicecount', '001')

FAILING_ORHTOGONAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'failing', 'gantrytilting', '001')

FAILING_ORIENTATION = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'data', 'failing', 'sliceorientation', '001')

FAILING_NOTAVOLUME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'data', 'failing', 'notavolume', '001')
