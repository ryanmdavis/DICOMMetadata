'''
Created on Feb 11, 2020

@author: davisr28

# calculate percent of timepoints in entire study that have CAP coverage
'''

import pandas as pd
import re
import numpy as np
import constants

anat_df=pd.read_csv("C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\GO29436_TaskSeries_list_20190219.csv")
# anat_df=anat_df[(anat_df["Mod."] == "CT") & (anat_df["Description"] != "Data Not Acquired")]
anat_df=anat_df.rename(mapper={"Code":"PatientName","Series Date":"StudyDate"},axis=1)

# calculate pivot table of description (
# anat_df.insert(len(anat_df.keys()),"Count",[1]*len(anat_df))
# table= pd.pivot_table(anat_df,values="Count",index="Description",aggfunc=np.sum).sort_values(by="Count")
# table.to_csv(constants.TEMP1_CSV)

anat_df=anat_df[(anat_df["Description"].str.contains("contrast|lung window|bone window",flags=re.IGNORECASE,regex=True)) & (~anat_df["Description"].str.contains("coronal|saggital",flags=re.IGNORECASE,regex=True).astype(bool))]

# calculate pivot table of anatomical coverage
anat_df.insert(len(anat_df.keys()),"Count",[1]*len(anat_df))
table= pd.pivot_table(anat_df,values="Count",index="Anatomy",aggfunc=np.sum).sort_values(by="Count")
table.to_csv(constants.ANAT_COV_PIVOT_LOC)

pt_df=anat_df[["PatientName","Visit"]].drop_duplicates()

coverage_df=pd.DataFrame([])
patient_num=-1
for (patient_name,visit) in pt_df.itertuples(index=False):
    patient_num=patient_num+1
    print("%2.1f%% completed." % (100*patient_num/len(pt_df)))
    this_pat_df=anat_df[(anat_df["PatientName"]==patient_name) & (anat_df["Visit"]==visit)]
    this_pat_contains_chest=any(this_pat_df["Anatomy"].str.contains("Chest|thorax",flags=re.IGNORECASE,regex=True))
    this_pat_contains_abdomen=any(this_pat_df["Anatomy"].str.contains("Abdomen",flags=re.IGNORECASE,regex=True))
    this_pat_contains_pelvis=any(this_pat_df["Anatomy"].str.contains("Pelvis",flags=re.IGNORECASE,regex=True))
    
    row={"PatientName":patient_name,"Visit":visit,"HasCAP":this_pat_contains_chest and this_pat_contains_abdomen and this_pat_contains_pelvis,"HasChest":this_pat_contains_chest,"HasAbdomen":this_pat_contains_abdomen,"HasPelvis":this_pat_contains_pelvis}
    coverage_df=coverage_df.append(pd.DataFrame(row,index=[len(coverage_df)]))

coverage_df.to_csv(constants.TEMP1_CSV)

patient_all_pt_cov_df=pd.DataFrame([])
for patient_name in list(pt_df["PatientName"].drop_duplicates()):
    all_timepoints_cap_bool=len(coverage_df[coverage_df["PatientName"]==patient_name]) == len(coverage_df[(coverage_df["PatientName"]==patient_name) & (coverage_df["HasCAP"]==True)])
    
    fraction_has_cap=len(coverage_df[(coverage_df["PatientName"]==patient_name) & (coverage_df["HasCAP"]==True)])/len(coverage_df[coverage_df["PatientName"]==patient_name])
    
    row={"PatientName":patient_name,"AllTPHasCAP":all_timepoints_cap_bool,"FractionHasCAP":fraction_has_cap}
    patient_all_pt_cov_df=patient_all_pt_cov_df.append(pd.DataFrame(row,index=[len(patient_all_pt_cov_df)]))

# patient_all_pt_cov_df.to_csv(constants.TEMP1_CSV)
print(constants.TEMP1_CSV)
print("%2.1f%% of timepoints contain full CAP coverage." % (100*len(coverage_df[coverage_df["HasCAP"]==True])/len(coverage_df)))
print("%2.1f%% of patients contain full CAP coverage for all of their exams." % (100*len(patient_all_pt_cov_df[patient_all_pt_cov_df["AllTPHasCAP"]==True])/len(patient_all_pt_cov_df)))