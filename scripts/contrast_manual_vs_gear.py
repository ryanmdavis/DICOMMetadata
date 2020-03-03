'''
Created on Mar 2, 2020

@author: davisr28
'''
import constants
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib

#set font sizes
matplotlib.rc('xtick', labelsize=16) 
matplotlib.rc('ytick', labelsize=16)
matplotlib.rcParams.update({'font.size': 16}) 

########################### GEAR ##################################
# see contrast_From_flywheel_gear.py
contrast_gear_df = pd.read_csv(constants.CONTRAST_GEAR_RESULT_LOC)
contrast_gear_df.insert(len(contrast_gear_df.keys()),"ContrastCount",(contrast_gear_df["HasContrastGear"] | contrast_gear_df["HasMR"]).astype(int))
contrast_gear_df.insert(len(contrast_gear_df.keys()),"VisitCount",[1]*len(contrast_gear_df))
pt_gear=pd.pivot_table(contrast_gear_df,index=["Subject Label"],values=["ContrastCount","VisitCount"],aggfunc=np.sum)

visits_without_contrast_gear=np.array(pt_gear["VisitCount"])-np.array(pt_gear["ContrastCount"])

######################### MANUAL ##################################
# see contrast.py
patient_contrast_manual_df = pd.read_csv(constants.TEMP_CONTRAST2_CSV)


########################## PLOT ###################################
ax1 = plt.subplot(1,2,1)
ax2 = plt.subplot(1,2,2)
ax1.hist(np.array(patient_contrast_manual_df["NumVisitsWithNoContrastAndNoBodyMR"]),color="k",bins=[-0.5 + ii for ii in range(12)])
ax1.set(xlabel="# Visits w/o Contrast CT or Body MR",ylabel="Number of Patients",title="From Manual Curation")
ax1.set_xticks([0,3,6,9,12])
ax1.set_ylim([0, 1200])
ax2.hist(visits_without_contrast_gear,color="k",bins=[-0.5 + ii for ii in range(12)])
ax2.set(xlabel="# Visits w/o Contrast CT or Body MR",title="From Metadata")
ax1.set_xticks([0,3,6,9,12])
ax2.set_ylim([0, 1200])
# plt.xlabel("Percent of patients's visits with axial contrast-enhanced scan",size=16)
# plt.ylabel("Number of Patients",size=16)
# plt.xticks(size=16)
# plt.yticks(size=16)
plt.show()