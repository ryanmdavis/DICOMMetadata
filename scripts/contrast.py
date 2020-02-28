'''
Created on Feb 25, 2020

Questions: 
 1) What percent of visits with no contrast have MR images?
 2) What percent of visits have contrast or MR?
 
Find a patient with no contrast on first method and yes contraston second, and see which is correct

@author: davisr28
'''
import pandas as pd
import numpy as np
import constants
import re

manual_df=pd.read_csv("C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\GO29436_TaskSeries_list_20190219.csv")
manual_df=manual_df.rename(mapper={"Code":"PatientName","Series Date":"StudyDate_str"},axis=1)
datetime_df=pd.to_datetime(manual_df["StudyDate_str"])
manual_df.insert(8,"StudyDate",datetime_df)

patient_list=list(manual_df["PatientName"].drop_duplicates())

patient_contrast_df=pd.DataFrame([])
patient_num=-1
for patient_name in patient_list:
    patient_num=patient_num+1
    print("%2.1f%% completed." % (100*patient_num/len(patient_list)))
    
    patient_manual_df=manual_df[manual_df["PatientName"]==patient_name].sort_values(by="StudyDate")
    
    
    # remove Head MR for MR analysis, scouts, and data not acquired
#     anat_df=anat_df[(anat_df["Description"].str.contains("contrast|lung window|bone window",flags=re.IGNORECASE,regex=True)) & (~anat_df["Description"].str.contains("coronal|saggital",flags=re.IGNORECASE,regex=True).astype(bool))]
    patient_manual_df=patient_manual_df[~((patient_manual_df["Anatomy"].str.contains("head|brain",flags=re.IGNORECASE,regex=True)) & (patient_manual_df["Mod."] == "MR"))]
    patient_manual_df=patient_manual_df[~patient_manual_df["Description"].isna()]
    patient_manual_df=patient_manual_df[~patient_manual_df["Description"].str.contains("scout|data not acquired",flags=re.IGNORECASE,regex=True)]


    # pivot with rows as visit and modality, columns as description. Which visits with no contrast have modality MR?
    patient_manual_df=patient_manual_df[~patient_manual_df["StudyDate"].isnull()]
    patient_manual_df.insert(len(patient_manual_df.keys()),"count",[1]*len(patient_manual_df))
    
    pt=pd.pivot_table(patient_manual_df,values="count",index=["Read Visit","Mod."],columns=["Description"],aggfunc=np.sum)
    pt.insert(0,"count",[1]*len(pt))

    total_visits=len(set(pt.index.codes[0]))

    visits_with_contrast=len(set(pt[~pt["w/IV contrast"].isna()].index.codes[0])) if "w/IV contrast" in pt.keys() else 0
    fraction_visits_with_contrast=visits_with_contrast/total_visits
    
    # no visits have contrast or any visit doesn't have contrast:
#     if ('w/IV contrast' not in pt.keys()) or (('w/IV contrast' in pt.keys()) and (any(pt["w/IV contrast"].isna()))):
    if visits_with_contrast < total_visits:
        if "MR" not in pt.index.levels[1]:
            fraction_non_contrast_with_mr=0
        elif "CT" not in pt.index.levels[1]:
            fraction_non_contrast_with_mr=1
        else:
            mr_pt=pd.DataFrame(pt.loc[(slice(None),"MR"),:])
            mr_visits=set(mr_pt.index.codes[0])
            
            ct_df=pd.DataFrame(pt.loc[(slice(None),"CT"),:])

            try:
                ct_no_contrast_df=ct_df[ct_df["w/IV contrast"].isna()]
            except:
                print("t")
               
            ct_visits=set(ct_df.index.codes[0])
            ct_no_contrast_visits=set(ct_no_contrast_df.index.codes[0])
            
            # find the visits that have no contrast and no MR visit
            no_contrast_visits_without_mr=ct_no_contrast_visits - ct_no_contrast_visits.intersection(mr_visits)

            # this else kicks in if all CT visits have contrast, but there is one visit with only MR. Then the denominator will be zero here.
            fraction_non_contrast_with_mr=1-len(list(no_contrast_visits_without_mr))/len(list(ct_no_contrast_visits)) if len(list(ct_no_contrast_visits)) > 0 else 1

    else:
        fraction_non_contrast_with_mr=1
    row={"PatientName":patient_name,"TotalVisits":total_visits,"FractionVisitsWithContrast":fraction_visits_with_contrast,"FractionNoContrastWithMR":fraction_non_contrast_with_mr}
#     print(row)
    patient_contrast_df=patient_contrast_df.append(pd.DataFrame(row,index=[len(patient_contrast_df)]))
patient_contrast_df.to_csv(constants.TEMP_CONTRAST_CSV)