'''
Created on Feb 25, 2020

Questions: 
 1) What percent of visits with no contrast have MR images?
 2) What percent of visits have contrast or MR?
 
 https://stackoverflow.com/questions/3899980/how-to-change-the-font-size-on-a-matplotlib-plot
 
Find a patient with no contrast on first method and yes contraston second, and see which is correct

@author: davisr28
'''
import pandas as pd
import numpy as np
import constants
import re
from matplotlib import pyplot as plt
import matplotlib

#set font sizes
matplotlib.rc('xtick', labelsize=20) 
matplotlib.rc('ytick', labelsize=20)
matplotlib.rcParams.update({'font.size': 20}) 

compute = True

if compute:
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
    
        visits_with_contrast_CT=len(set(pt[~pt["w/IV contrast"].isna()].loc[(slice(None),"CT"),:].index.codes[0])) if (("w/IV contrast" in pt.keys()) and ("CT" in pt.index.levels[1])) else 0
    
        fraction_visits_with_contrast=visits_with_contrast_CT/total_visits
        
        # if any visits doesn't have contrast CT:
        if visits_with_contrast_CT < total_visits:
            if "MR" not in pt.index.levels[1]:
                fraction_non_contrast_with_mr=0
                fraction_with_ct_contrast_or_mr=fraction_visits_with_contrast
                num_visits_w_no_contrast_and_no_mr = total_visits - visits_with_contrast_CT
            elif "CT" not in pt.index.levels[1]:
                mr_pt=pd.DataFrame(pt.loc[(slice(None),"MR"),:])
                mr_visits=set(mr_pt.index.codes[0])
                
                fraction_non_contrast_with_mr=1
                fraction_with_ct_contrast_or_mr=1
                
                num_visits_w_no_contrast_and_no_mr = total_visits-len(mr_visits)
            else:
                mr_pt=pd.DataFrame(pt.loc[(slice(None),"MR"),:])
                mr_visits=set(mr_pt.index.codes[0])
                
                ct_df=pd.DataFrame(pt.loc[(slice(None),"CT"),:])
    
                # no contrast visits
                ct_no_contrast_df=ct_df[ct_df["w/IV contrast"].isna()] if "w/IV contrast" in ct_df.keys() else ct_df
                ct_with_contrast_df=ct_df[~ct_df["w/IV contrast"].isna()] if "w/IV contrast" in ct_df.keys() else ct_df[ct_df[ct_df.keys()[0]]=="1"]
    
                   
                ct_visits=set(ct_df.index.codes[0])
                ct_no_contrast_visits=set(ct_no_contrast_df.index.codes[0])
                
                # find the visits that have no contrast and no MR visit
                no_contrast_visits_without_mr=ct_no_contrast_visits - ct_no_contrast_visits.intersection(mr_visits)
                num_visits_w_no_contrast_and_no_mr = len(no_contrast_visits_without_mr)
    
                # this else kicks in if all CT visits have contrast, but there is one visit with only MR. Then the denominator will be zero here.
                fraction_non_contrast_with_mr=1-len(list(no_contrast_visits_without_mr))/len(list(ct_no_contrast_visits)) if len(list(ct_no_contrast_visits)) > 0 else 1
        
                # with contrast visits
                ct_with_contrast_visits=set(ct_with_contrast_df.index.codes[0])
                
                # fraction with contrast or MR
                visits_with_ct_contrast_or_mr=ct_with_contrast_visits.union(mr_visits)
                fraction_with_ct_contrast_or_mr=len(visits_with_ct_contrast_or_mr)/total_visits
                
                # fraction with contrast
#                 fraction_with_ct_contrast_or
    
        else:
            fraction_non_contrast_with_mr=1
            fraction_with_ct_contrast_or_mr=1
            num_visits_w_no_contrast_and_no_mr=0
        row={"PatientName":patient_name,"TotalVisits":total_visits,"FractionVisitsWithContrast":fraction_visits_with_contrast,"FractionNoContrastWithMR":fraction_non_contrast_with_mr,"FractionWithCTContrastOrMR":fraction_with_ct_contrast_or_mr,"NumVisitsWithNoContrastAndNoBodyMR":num_visits_w_no_contrast_and_no_mr}
        patient_contrast_df=patient_contrast_df.append(pd.DataFrame(row,index=[len(patient_contrast_df)]))
    
    patient_contrast_df.to_csv(constants.TEMP_CONTRAST2_CSV)
    
else:
    
    patient_contrast_df = pd.read_csv(constants.TEMP_CONTRAST2_CSV)

ax1 = plt.subplot(1,2,1)
ax2 = plt.subplot(1,2,2)
ax1.hist(np.array(patient_contrast_df["NumVisitsWithNoContrastAndNoBodyMR"]),color="k",bins=[-0.5 + ii for ii in range(12)])
ax1.set(xlabel="# Visits w/o Contrast CT or Body MR",ylabel="Number of Patients")
ax1.set_xticks([0,3,6,9,12])
ax2.hist(100*np.array(patient_contrast_df["FractionWithCTContrastOrMR"]),color="k",bins=[10*(-0.5 + ii) for ii in range(12)])
ax2.set(xlabel="Percent visits w/ contrast-CT")
# plt.xlabel("Percent of patients's visits with axial contrast-enhanced scan",size=16)
# plt.ylabel("Number of Patients",size=16)
# plt.xticks(size=16)
# plt.yticks(size=16)
plt.show()

percent_patients_contrast_all_visits=len(patient_contrast_df[patient_contrast_df["NumVisitsWithNoContrastAndNoBodyMR"]==0])/len(patient_contrast_df)
percent_patients_contrast_all_or_all_but_one_visits=len(patient_contrast_df[patient_contrast_df["NumVisitsWithNoContrastAndNoBodyMR"]<=1])/len(patient_contrast_df)

print("%d% of patients have contrast on all visits" % (100*percent_patients_contrast_all_visits))
print("%d% patients have contrast on all but one visitt" % (100*percent_patients_contrast_all_or_all_but_one_visits))
