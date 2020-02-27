'''
Created on Feb 25, 2020

Questions: 
 1) What percent of visits with no contrast have MR images?
 2) What percent of visits have contrast or MR?

@author: davisr28
'''
import pandas as pd
import numpy as np
import constants

manual_df=pd.read_csv("C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\GO29436_TaskSeries_list_20190219.csv")
manual_df=manual_df.rename(mapper={"Code":"PatientName","Series Date":"StudyDate_str"},axis=1)
datetime_df=pd.to_datetime(manual_df["StudyDate_str"])
manual_df.insert(8,"StudyDate",datetime_df)

patient_list=list(manual_df["PatientName"].drop_duplicates())

patient_time_df=pd.DataFrame([])
patient_num=-1
for patient_name in patient_list:
    patient_num=patient_num+1
    print("%2.1f%% completed." % (100*patient_num/len(patient_list)))
    
    patient_manual_df=manual_df[manual_df["PatientName"]==patient_name].sort_values(by="StudyDate")
    
    # pivot with rows as visit and modality, columns as description. Which visits with no contrast have modality MR?
    patient_manual_df=patient_manual_df[~patient_manual_df["StudyDate"].isnull()]
    patient_manual_df.insert(len(patient_manual_df.keys()),"count",[1]*len(patient_manual_df))
    
    pt=pd.pivot_table(patient_manual_df,values="count",index=["Read Visit","Mod."],columns=["Description"],aggfunc=np.sum)
    pt.insert(0,"count",[1]*len(pt))

    # no visits have contrast or any visit doesn't have contrast:
    if ('w/IV contrast' not in pt.keys()) or (('w/IV contrast' in pt.keys()) and (any(pt["w/IV contrast"].isna()))):
        if "MR" not in pt.index.levels[1]:
            percent_non_contrast_with_MR=0
        else:
            mr_pt=pd.DataFrame(pt.loc[(slice(None),"MR"),:])
            mr_visits=set(mr_pt.index.codes[0])
            
            ct_df=pd.DataFrame(pt.loc[(slice(None),"CT"),:])
            ct_no_contrast_df=ct_df[ct_df["w/IV contrast"].isna()]
            ct_visits=set(ct_df.index.codes[0])
            ct_no_contrast_visits=set(ct_no_contrast_df.index.codes[0])
            
            # find the visits that have no contrast and no MR visit
            no_contrast_visits_without_mr=ct_no_contrast_visits - ct_no_contrast_visits.intersection(mr_visits)
            
            percent_non_contrast_with_MR=len(list(no_contrast_visits_without_mr))/len(list(ct_no_contrast_visits))
            
        pt.to_csv(constants.TEMP1_CSV)
        print("t")