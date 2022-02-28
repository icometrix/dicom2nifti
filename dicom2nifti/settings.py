class Dicom2NiftiSettings:
    validate_slicecount = True
    validate_orientation = True
    validate_orthogonal = True
    validate_slice_increment = True
    validate_instance_number = False
    validate_multiframe_implicit = True
    pydicom_read_force = False
    gdcmconv_path = None
    resample = False
    resample_padding = 0
    resample_spline_interpolation_order = 0  # spline interpolation order (0 nn , 1 bilinear, 3 cubic)

    @classmethod
    def disable_validate_slice_increment(cls):
        """
        Disable the validation of the slice increment.
        This allows for converting data where the slice increment is not consistent.
        USE WITH CAUTION!
        """
        cls.validate_slice_increment = False

    @classmethod
    def disable_validate_instance_number(cls):
        """
        Disable the validation of the slice increment.
        This allows for converting data where the slice increment is not consistent.
        USE WITH CAUTION!
        """
        cls.validate_instance_number = False

    @classmethod
    def disable_validate_orientation(cls):
        """
        Disable the validation of the slice orientation.
        This validation checks that all slices have the same orientation (are parallel).
        USE WITH CAUTION!
        """
        cls.validate_orientation = False

    @classmethod
    def disable_validate_orthogonal(cls):
        """
        Disable the validation whether the volume is orthogonal (so without gantry tilting or alike).
        This allows for converting gantry tilted data.
        The gantry tilting will be reflected in the affine matrix and not in the data
        USE WITH CAUTION!
        """
        cls.validate_orthogonal = False

    @classmethod
    def disable_validate_slicecount(cls):
        """
        Disable the validation of the minimal slice count of 4 slices.
        This allows for converting data with less slices.
        Usually less than 4 could be considered localizer or similar thus ignoring these scans by default
        USE WITH CAUTION!
        """
        cls.validate_slicecount = False

    @classmethod
    def disable_validate_multiframe_implicit(cls):
        """
        Disable the validation that checks that data is not multiframe implicit
        This allows to sometimes convert Philips Multiframe with implicit transfer syntax
        """
        cls.validate_multiframe_implicit = False

    @classmethod
    def enable_validate_slice_increment(cls):
        """
        Enable the slice increment validation again (DEFAULT ENABLED)
        """
        cls.validate_slice_increment = True

    @classmethod
    def enable_validate_instance_number(cls):
        """
        Enable the slice increment validation again (DEFAULT ENABLED)
        """
        cls.validate_instance_number = True

    @classmethod
    def enable_validate_orientation(cls):
        """
        Enable the slice orientation validation again (DEFAULT ENABLED)
        """
        cls.validate_orientation = True

    @classmethod
    def enable_validate_orthogonal(cls):
        """
        Enable the validation whether the volume is orthogonal again (DEFAULT ENABLED)
        """
        cls.validate_orthogonal = True

    @classmethod
    def enable_validate_slicecount(cls):
        """
        Enable the validation of the minimal slice count of 4 slices again (DEFAULT ENABLED)
        """
        cls.validate_slicecount = True

    @classmethod
    def enable_validate_multiframe_implicit(cls):
        """
        Enable the validation that checks that data is not multiframe implicit again (DEFAULT ENABLED)
        """
        cls.validate_multiframe_implicit = True

    @classmethod
    def enable_pydicom_read_force(cls):
        """
        Enable the pydicom read force to try to read non conform dicom data
        """
        cls.pydicom_read_force = True

    @classmethod
    def disable_pydicom_read_force(cls):
        """
        Enable the pydicom read force to try to read non conform dicom data
        """
        cls.pydicom_read_force = False

    @classmethod
    def enable_resampling(cls):
        """
        Enable resampling in case of gantry tilted data (disabled by default)
        """
        cls.resample = True

    @classmethod
    def disable_resampling(cls):
        """
        Disable resampling in case of gantry tilted data (disabled by default)
        """
        cls.resample = False

    @classmethod
    def set_resample_padding(cls, padding):
        """
        Set the spline interpolation padding

        :param padding: spline interpolation padding value
        """
        cls.resample_padding = padding

    @classmethod
    def set_resample_spline_interpolation_order(cls, order):
        """
        Set the spline interpolation order used during resampling of gantry tilted data

        :param order: spline interpolation order (0 nn , 1 bilinear, 3 cubic)
        """
        cls.resample_spline_interpolation_order = order

    @classmethod
    def set_gdcmconv_path(cls, path):
        """
        Set where the filepath to the gdcmconv executable (needed is it is not found in your PATH)

        :param path: the file path to the gdcmconv executable
        """
        cls.gdcmconv_path = path
