'''
Created on Feb 5, 2020

@author: davisr28
'''

import pandas as pd
import constants
import matplotlib.pyplot as plt
import numpy as np
import query as q

dtype={"ContrastBolusStartTime":str,"ConvKernel":str,"FolderIndex":int,"ImageZCoverage":float,"IsAxial":bool,"Manufacturer":str,"ManufacturerModelName":str,"PatientName":str,"SeriesName":str,"SeriesNameWithContrast":bool,"SeriesZCoverage":float,"SliceThicknessImageFirst":float,"SliceThicknessImageLast":float,"SliceThicknessSeries":float,"StudyDate":str}
md_df=pd.read_csv(constants.METADATA_DATABASE_LOC, encoding = "ISO-8859-1",dtype=dtype)

# histogram of slice thicknesses among axial slices
ax1 = plt.subplot(1,2,1)
ax2 = plt.subplot(1,2,2)
ax1.hist(np.array(md_df[(md_df["IsAxial"]==True) & (md_df["SeriesNameWithContrast"]==True)]["SliceThicknessSeries"]),bins=100,range=(0,6))
ax2.hist(np.array(md_df[(md_df["IsAxial"]==True) & (md_df["SeriesNameWithContrast"]==True)]["SliceThicknessImageFirst"]),bins=100,range=(0,6))
ax1.set(xlabel="Slice Thickness (mm)",ylabel="Number of Axial Series",title="Series-level SliceThickness Attribute (0x0018,0x0050)")
ax2.set(xlabel="Slice Thickness (mm)",ylabel="Number of Axial Series",title="Image-level Slice Separation (0x0020,0x0032)")
ax1.set_ylim([0,14000])
ax2.set_ylim([0,14000])
# plt.show()

# percent of patients with 3 mm or 5 mm SliceThickness
sts=[5.0,3.0,2.5,1.0]
# num_PT_3_5_slice = len(md_df[(md_df["IsAxial"]==True) & (md_df["SliceThicknessSeries"].isin(sts))].drop_duplicates(subset=["PatientName","StudyDate"]))
num_PT_3_5_slice = len(q.queryFloatRange(md_df[(md_df["IsAxial"]==True) & (md_df["SeriesNameWithContrast"]==True)], "SliceThicknessSeries", sts, constants.MM_RANGE).drop_duplicates(subset=["PatientName","StudyDate"]))

# num_PT_3_5_image = len(md_df[(md_df["IsAxial"]==True) & (md_df["SliceThicknessImageFirst"].isin(sts))].drop_duplicates(subset=["PatientName","StudyDate"]))
num_PT_3_5_image = len(q.queryFloatRange(md_df[(md_df["IsAxial"]==True) & (md_df["SeriesNameWithContrast"]==True)], "SliceThicknessImageFirst", sts, constants.MM_RANGE).drop_duplicates(subset=["PatientName","StudyDate"]))
num_PT = len(md_df.drop_duplicates(subset=["PatientName","StudyDate"]))

percent_w_3_5_slice = 100 * num_PT_3_5_slice/num_PT
percent_w_3_5_image = 100 * num_PT_3_5_image/num_PT

print("Percent patient_timepoints with a %s mm slice thickness contrast-enhanced axial scan (Slice Thickness attribute): %2.2f%%" % (",".join([str(s) for s in sts]),percent_w_3_5_slice))
print("Percent patient_timepoints with a %s mm slice thickness contrast-enhanced axial scan (Image Spacing attribute): %2.2f%%" % (",".join([str(s) for s in sts]),percent_w_3_5_image))

# md_df[md_df["IsAxial"]==True]["SliceThicknessSeries"]
print("t")

# percent of time first slice and last slice are more than 5% different thickness

# percent of time that series and image-level slice thicknesses are different