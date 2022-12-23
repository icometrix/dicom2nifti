from distutils.core import setup
from setuptools import find_packages


version = "2.4.7"
print('Starting pypi release version %s' % version)
long_description = """
With this package you can convert dicom images to nifti files.
There is support for most anatomical CT and MR data.
For MR specifically there is support for most 4D data (like DTI and fMRI)
"""

setup(
    name='dicom2nifti',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    version=version,
    description='package for converting dicom files to nifti',
    long_description=long_description,
    license='MIT',
    author='icometrix NV',
    author_email='dicom2nifti@icometrix.com',
    maintainer="icometrix NV",
    maintainer_email="dicom2nifti@icometrix.com",
    url='https://github.com/icometrix/dicom2nifti',
    download_url='https://github.com/icometrix/dicom2nifti/tarball/%s' % version,
    keywords=['dicom', 'nifti', 'medical imaging'],
    scripts=['scripts/dicom2nifti'],
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux'],
    install_requires=['nibabel', 'numpy', 'scipy', 'pydicom>=2.2.0', 'python-gdcm'],
    setup_requires=['nose', 'coverage']
)
