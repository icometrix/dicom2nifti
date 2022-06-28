=============
 dicom2nifti
=============

Python library for converting dicom files to nifti

:Author: Arne Brys
:Organization: `icometrix <https://www.icometrix.com>`_
:Repository: https://github.com/icometrix/dicom2nifti
:API documentation: https://icometrix.github.io/dicom2nifti/

=====================
 Using dicom2nifti
=====================
---------------
 Installation
---------------

conda:

.. code-block:: bash

   conda install -c conda-forge dicom2nifti

pip:

.. code-block:: bash

   pip install dicom2nifti

To support compressed dicom formats (JPEG, JPEG2000) we use GDCM in combination with pydicom.
Please install gdcm as required. https://pydicom.github.io/pydicom/stable/tutorials/installation.html

---------------
 Updating
---------------

conda:

.. code-block:: bash

   conda update dicom2nifti

pip:

.. code-block:: bash

   pip install dicom2nifti --upgrade

---------------
 Usage
---------------
Command line
^^^^^^^^^^^^^
.. code-block:: bash

   dicom2nifti [-h] [-G] [-r] [-o RESAMPLE_ORDER] [-p RESAMPLE_PADDING] [-M] [-C] [-R] input_directory output_directory


for more information

.. code-block:: bash

   dicom2nifti -h

From python
^^^^^^^^^^^^

Converting a directory with dicom files to nifti files

.. code-block:: python

   import dicom2nifti

   dicom2nifti.convert_directory(dicom_directory, output_folder, compression=True, reorient=True)

Converting a directory with only 1 series to 1 nifti file

.. code-block:: python

   import dicom2nifti

   dicom2nifti.dicom_series_to_nifti(original_dicom_directory, output_file, reorient_nifti=True)

----------------
 Supported data
----------------
Most anatomical data for CT and MR should be supported as long as they are in classical dicom files.

Try avoiding "Implicit VR Endian" if possible as this makes converting non anatomical (i.e. DTI, fMRI, ...) much more difficult.

There is some vendor specific support, more specifically for 4D imaging like fMRI and DTI/DKI

Gantry tilted CT
^^^^^^^^^^^^^^^^^
By default support for gantry tilted ct is disabled as we validate image orthogonality.
You can explicitly allow gantry tilted data by disabling this validation.

Standard this will result in a nifti file where the gantry tilt is captured by the affine matrix.
We also provide the option to resample the data to an orthogonal nifti.
For this resampling we use scipy.ndimage.interpolation.affine_transform.
You should configure the padding value and spline interpolation order.
IMPORTANT NOTE: When using the orthogonal resampling the output nifti will always be reoriented

Command line:

.. code-block:: bash

   dicom2nifti -G -r -o 1 -p -1000 input_directory output_directory


Python code:

.. code-block:: python

   import dicom2nifti
   import dicom2nifti.settings as settings

   settings.disable_validate_orthogonal()
   settings.enable_resampling()
   settings.set_resample_spline_interpolation_order(1)
   settings.set_resample_padding(-1000)

   dicom2nifti.convert_directory(dicom_directory, output_folder)



Inconsistent slice incremement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default support for inconsistent slice increments is disabled.
You can explicitly allow the images but should also use resampling (similar to the gantry tilted support)
to avoid geometric distortions due to the inconsistent slice increments.
You should configure the padding value and spline interpolation order

Command line:

.. code-block:: bash

   dicom2nifti -I -r -o 1 -p -1000 input_directory output_directory


Python code:

.. code-block:: python

   import dicom2nifti
   import dicom2nifti.settings as settings

   settings.disable_validate_slice_increment()
   settings.enable_resampling()
   settings.set_resample_spline_interpolation_order(1)
   settings.set_resample_padding(-1000)

   dicom2nifti.convert_directory(dicom_directory, output_folder)


Single slice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default we do not convert single slice images.
You can explicitly allow the conversion of single slices.

Command line:

.. code-block:: bash

   dicom2nifti -S input_directory output_directory


Python code:

.. code-block:: python

   import dicom2nifti
   import dicom2nifti.settings as settings

   settings.disable_validate_slicecount()

   dicom2nifti.convert_directory(dicom_directory, output_folder)


GE MR
^^^^^^
Anatomical data should all be support.
4D images like fMRI and DTI/DKI are supported.

Siemens MR
^^^^^^^^^^^
Anatomical data should all be support.
4D images like fMRI and DTI/DKI are supported.

Philips MR
^^^^^^^^^^^
For classic dicom files dicom2nifti support anatomical.
For classic dicom files 4D images like fMRI and DTI/DKI are supported.

For "Philips Enhanced Dicom" there is no support for "Implicit VR Endian" transfer syntax.
For the others we support anatomical and 4D images like fMRI and DTI/DKI.

Hitachi MR
^^^^^^^^^^^
Anatomical data should all be support.
4D images like fMRI and DTI/DKI are NOT supported.
Anyone willing to share DTI and/or fMRI dicom form Hitachi scanners please contact us.

------------------
 Unsupported data
------------------
If you encounter unsupported data you can help the development of dicom2nifti by providing a dataset. This dataset should be anonymised (but leave as much of the private fields as possible).


