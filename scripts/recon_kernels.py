'''
Created on Feb 6, 2020

@author: davisr28
'''
import metadata as md
import constants
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# md_df=md.loadMetadata()
# # md_df.drop_duplicates(subset=["Manufacturer","ConvKernel"])[["Manufacturer","ConvKernel"]].to_csv(constants.CONV_KERNAL_LIST_LOC)
# 
# patient_list=list(md_df["PatientName"].drop_duplicates())
# 
# patient_kernel_df=pd.DataFrame([])
# patient_num=-1
# for patient_name in patient_list:
#     patient_num=patient_num+1
#     print("%2.1f%% completed." % (100*patient_num/len(patient_list)))
#     patient_md_df=md_df[(md_df["PatientName"]==patient_name) & (md_df["IsAxial"]==True)].sort_values(by="StudyDate")
#     patient_md_df=patient_md_df[~patient_md_df["StudyDate"].isnull()]
#     
#     date_df=patient_md_df[["StudyDate"]].drop_duplicates().sort_values(by="StudyDate")
#     
#     num_kernels_all_visits=len(list(set(set(patient_md_df["ConvKernel"]))))
#     num_kernels_first_visit=len(list(set(set(patient_md_df[patient_md_df["StudyDate"]==date_df["StudyDate"].iloc[0]]["ConvKernel"]))))
#     
#     row={"PatientName":patient_name,"NumKernelsFirstVisit":num_kernels_first_visit,"NumKernelsAllVisits":num_kernels_all_visits}
#     patient_kernel_df=patient_kernel_df.append(pd.DataFrame(row,index=[len(patient_kernel_df)]))
# patient_kernel_df.to_csv(constants.TEMP1_CSV)

patient_kernel_df=pd.read_csv(constants.TEMP1_CSV)

# histogram of slice thicknesses among axial slices
ax1 = plt.subplot(1,3,1)
ax2 = plt.subplot(1,3,2)
ax3 = plt.subplot(1,3,3)
ax1.hist(np.array(patient_kernel_df["NumKernelsFirstVisit"]),bins=10,range=(0,10))
ax2.hist(np.array(patient_kernel_df["NumKernelsAllVisits"]),bins=10,range=(0,10))
ax3.hist(np.divide(np.array(patient_kernel_df["NumKernelsAllVisits"]),np.array(patient_kernel_df["NumKernelsFirstVisit"])),bins=10,range=(1,5))
ax1.set(xlabel="Number of Kernels Used in First Visit",ylabel="Number of Patients",title="First Visit")
ax2.set(xlabel="Number of Kernels Used in All Visits",ylabel="Number of Patients",title="All Visits")
ax3.set(xlabel="Ratio of # Kernels in First/All Visits",ylabel="Number of Patients",title="All:First Ratio")
ax1.set_ylim([0,700])
ax2.set_ylim([0,700])
ax3.set_ylim([0,700])

plt.show()
