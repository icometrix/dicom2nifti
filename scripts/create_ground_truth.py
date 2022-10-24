import os
import traceback

import dicom2nifti
import dicom2nifti.image_reorientation as image_reorientation
import dicom2nifti.settings as settings


def subdir_count(path):
    count = 0
    for f in os.listdir(path):
        child = os.path.join(path, f)
        if os.path.isdir(child):
            count += 1
    return count


def main():
    test_data_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                       'tests',
                                       'data')
    print(test_data_directory)
    for root, dir_names, _ in os.walk(test_data_directory):
        settings.disable_validate_multiframe_implicit()
        settings.disable_validate_slicecount()
        # New directory
        for dir_name in dir_names:
            dir_path = os.path.join(root, dir_name)
            if subdir_count(dir_path) > 0:
                continue  # not processing because not lowest level of directory
            print(dir_path)
            output_file = dir_path + '_ground_truth.nii.gz'
            reoriented_file = dir_path + '_ground_truth_reoriented.nii.gz'
            # noinspection PyBroadException
            try:
                generate_ground_truth(dir_path, output_file, reoriented_file)
            except: # explicitly capturing everything here
                traceback.print_exc()
                pass


def generate_ground_truth(dicom_directory, output_file, reoriented_file):
    if not os.path.isfile(output_file):
        dicom2nifti.dicom_series_to_nifti(dicom_directory, output_file, False)
        image_reorientation.reorient_image(output_file, reoriented_file)


def generate_inconsistent_slice_incement():
    settings.disable_validate_orthogonal()
    settings.disable_validate_slice_increment()
    settings.enable_resampling()
    settings.set_resample_padding(0)
    settings.set_resample_spline_interpolation_order(1)

    dicom_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'tests',
                                   'data',
                                   'failing',
                                   'sliceincrement',
                                   '002')

    output_file = dicom_directory + '_ground_truth.nii.gz'
    reoriented_file = dicom_directory + '_ground_truth_reoriented.nii.gz'
    generate_ground_truth(dicom_directory, output_file, reoriented_file)

    settings.disable_resampling()
    settings.enable_validate_slice_increment()
    settings.enable_validate_orientation()


if __name__ == "__main__":

    main()
    #generate_inconsistent_slice_incement()
