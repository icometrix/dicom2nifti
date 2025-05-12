#%%
import numpy as np
import pydicom

# %%
# Read in a template Philips Multiframe DTI
ds = pydicom.dcmread("/Users/matthew/Downloads/Apollo/MR000000.dcm")
# %%
# Copy the template
adc_ds = ds.copy()
#%%
# New UID
O8T_UID = pydicom.uid.UID("1.3.6.1.4.1.55381")
# %%
# Patient Data
adc_ds.PatientName = "Philips_ADC_Multiframe"
adc_ds.PatientID = "Philips_ADC_Multiframe"
#%%
# Current date and time
date = pydicom.valuerep.DT("20240625")
time = pydicom.valuerep.TM("204732.16")
#%%
# Instance/Series/Study
adc_ds.InstanceCreationDate = date
adc_ds.InstanceCreationTime = time
adc_ds.InstanceCreatorUID = O8T_UID
adc_ds.SOPInstanceUID = pydicom.uid.generate_uid()
adc_ds.StudyDate = date
adc_ds.SeriesDate = date
adc_ds.ContentDate = date
adc_ds.AcquisitionDateTime = date
adc_ds.StudyTime = time
adc_ds.SeriesTime = time
adc_ds.ContentTime = time
adc_ds.StationName = "ADC_Multiframe"
adc_ds.ReferencedPerformedProcedureStepSequence[0].InstanceCreationDate = date
adc_ds.ReferencedPerformedProcedureStepSequence[0].InstanceCreationTime = time
adc_ds.ReferencedPerformedProcedureStepSequence[0].InstanceCreatorUID = O8T_UID

adc_ds.DeviceSerialNumber = "adcMultiframe"

adc_ds.StudyInstanceUID = pydicom.uid.generate_uid()
adc_ds.SeriesInstanceUID = pydicom.uid.generate_uid()
adc_ds.StudyID = "0000"
adc_ds.SeriesNumber = "1111"

# The existing scan is 34 directions of 80 slices per frame -> Image Dimension is 2720
num_slices_per_frame = 8
num_frames = 4
adc_ds.NumberOfFrames = str(num_slices_per_frame*num_frames)
adc_ds.RequestAttributesSequence[0].AccessionNumber = "0"
# %%
pffgs = ds.PerFrameFunctionalGroupsSequence
# %%
adc_pffgs = pydicom.sequence.Sequence()
# %%
# Slices go:
# - b0 at Z height A
# - b1000 (Dir 1) at Z height A
# - b1000 (Dir 2) at Z height A
# ...
# ADC at Z height A
# - b0 at Z height B
# ...
# 0, 1, 2, 33, 34, 35, 36, 67

for z_count, z_height in enumerate(range(num_slices_per_frame)):
    for new_frame, direction in enumerate([0, 1, 2, 33]):
        frame_to_grab = (z_height * 34) + direction
        print(f'frame_to_grab: {frame_to_grab}')
        one_frame = pffgs[frame_to_grab]
        div = one_frame.FrameContentSequence[0].DimensionIndexValues
        new_div = div[0:3]
        if direction == 0:  # The B=0, was seen in the Apollo to have [x,y,z,33]
            new_div.append(3)
            one_frame.FrameContentSequence[0].DimensionIndexValues = new_div
        elif direction > 30: # The ADC, was seen to be the last, but we're removing 30 frames so do the minus 30
            new_div.append(direction-30)
            one_frame.FrameContentSequence[0].DimensionIndexValues = new_div
        else:
            new_div.append(direction) # Regular B=1000, keep as is
            one_frame.FrameContentSequence[0].DimensionIndexValues = new_div
        frame_number_to_insert = (z_count * 4) + new_frame
        print(f"frame_number_to_insert: {frame_number_to_insert}")
        adc_pffgs.insert(frame_number_to_insert,one_frame)

# %%
adc_ds.PerFrameFunctionalGroupsSequence = adc_pffgs
#%%
volume = np.random.randint(
    2**16, size=(adc_ds.NumberOfFrames, adc_ds.Rows, adc_ds.Columns), dtype=np.uint16
)
adc_ds.PixelData = volume.tobytes()
# %%
adc_ds.save_as("tests/data/philips_enhanced/dti/adc/adc_multiframe.dcm")
# %%
