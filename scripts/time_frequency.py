'''
Created on Feb 6, 2020

@author: davisr28
'''
import metadata as md
import pandas as pd
import numpy as np
import constants
from matplotlib import pyplot as plt

md_df=md.loadMetadata()

patient_list=list(md_df["PatientName"].drop_duplicates())

patient_time_df=pd.DataFrame([])
patient_num=-1
for patient_name in patient_list:
    patient_num=patient_num+1
    print("%2.1f%% completed." % (100*patient_num/len(patient_list)))
    patient_md_df=md_df[md_df["PatientName"]==patient_name].drop_duplicates(subset="StudyDate").sort_values(by="StudyDate")
    patient_md_df=patient_md_df[~patient_md_df["StudyDate"].isnull()]
    
    row_dict={}
    
    # scan timing
    row_dict["PatientName"]=patient_name
    row_dict["DaysBetweenFirstLastScan"]=int((patient_md_df.iloc[-1]["StudyDate"]-patient_md_df.iloc[0]["StudyDate"]).total_seconds()/(60*60*24))
        
    if len(patient_md_df)>1:
        row_dict["AverageDaysBetweenScans"]=int(np.array([int((patient_md_df.iloc[ii+1]["StudyDate"]-patient_md_df.iloc[ii]["StudyDate"]).total_seconds()/(60*60*24)) for ii in range(0,len(patient_md_df)-1)]).mean())
    else:
        row_dict["AverageDaysBetweenScans"]=0

    # contrast use consistency
    patient_contrast_md_df=md_df[(md_df["PatientName"]==patient_name) & (patient_md_df["SeriesNameWithContrast"]==True)].drop_duplicates(subset="StudyDate")
    row_dict["PercentStudyDatesWithContrast"] = 100 * len(patient_contrast_md_df)/len(patient_md_df)
    
    # add to dataframe
    patient_time_df=patient_time_df.append(row_dict, ignore_index=True)
        
# ax1 = plt.subplot(1,2,1)
# ax2 = plt.subplot(1,2,2)
# ax1.hist(patient_time_df["DaysBetweenFirstLastScan"])
# ax1.set(xlabel="Days",ylabel="Number of Patients",title="Number of days between first and last CT scan")
# ax2.hist(patient_time_df["AverageDaysBetweenScans"])
# ax2.set(xlabel="Days",ylabel="Number of Patients",title="Average number of days between patient scan dates")
# plt.show()

fig,ax3=plt.subplots()
ax3.hist(patient_time_df["PercentStudyDatesWithContrast"],color="k")
ax3.set(xlabel="Percent of patients's visits with axial contrast-enhanced scan",ylabel="Number of Patients",size=16)
plt.xlabel("Percent of patients's visits with axial contrast-enhanced scan",size=16)
plt.ylabel("Number of Patients",size=16)
plt.xticks(size=16)
plt.yticks(size=16)
plt.show()

patient_time_df.to_csv(constants.TEMP1_CSV)

print("Median of average days between scans: %d" % (int(patient_time_df["AverageDaysBetweenScans"].median())))
print("Median of days between first and last scan: %d" % (int(patient_time_df["DaysBetweenFirstLastScan"].median())))

print(constants.TEMP1_CSV)