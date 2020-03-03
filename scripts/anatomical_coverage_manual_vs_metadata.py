'''
Created on Feb 11, 2020

@author: davisr28

# calculate percent of timepoints in entire study that have CAP coverage
'''

import pandas as pd
import re
import numpy as np
import constants
from sklearn.metrics import confusion_matrix
from datetime import datetime

###################################### METADATA ###############################################
# figure out which patient/studies have CAP coverage from metadata (z-position coverage)
# Considers z coverage of entire study (not just single series) excluding head/brain series

HEAD_UPPER_THRESHOLD_MM = 225
CAP_LOWER_THRESHOLD_MM = 550

compute = False

if compute:
    # read and format dataframes
    meta_df=pd.read_csv(constants.METADATA_DATABASE_LOC)
    meta_df=meta_df[meta_df["IsAxial"]==True]
    pt_df=meta_df[["PatientCode","StudyDate"]].drop_duplicates()
    
    # figure out which patient/studies have CAP coverage from the metadata
    coverage_meta_df=pd.DataFrame([])
    patient_num=-1
    for (patient_code,study_date) in pt_df.itertuples(index=False):
        patient_num=patient_num+1
        print("%2.1f%% completed metadata." % (100*patient_num/len(pt_df)))
        
        pt_meta_nohead_df=meta_df[(meta_df["PatientCode"] == patient_code) & (meta_df["StudyDate"] == study_date) & ~(meta_df["SeriesZCoverageImg"] < HEAD_UPPER_THRESHOLD_MM)]
        
        if len(pt_meta_nohead_df) > 0:
            # find the most superior and inferior slice for non-head series
            edge_pos=np.concatenate((np.array(pt_meta_nohead_df["FirstSlice"]),np.array(pt_meta_nohead_df["LastSlice"])),axis=0)
            superior_pos=edge_pos.max()
            inferior_pos=edge_pos.min()
            non_head_spatial_coverage=superior_pos-inferior_pos
            
            pt_has_cap_meta=non_head_spatial_coverage > CAP_LOWER_THRESHOLD_MM
            
            row={"PatientCode":str(patient_code),"StudyDate":str(study_date),"NonHeadSpatialCoverage":non_head_spatial_coverage}
            coverage_meta_df=coverage_meta_df.append(pd.DataFrame(row,index=[len(coverage_meta_df)]))
    coverage_meta_df.to_csv(constants.ANAT_COV_META_STORE_LOC)
    
    ################### MANUALLY CURATED ANATOMICAL COVERAGE INFORMATION ##########################
    # read and format dataframe of manually curated anatomical coverage
    anat_df=pd.read_csv("C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\GO29436_TaskSeries_list_20190219.csv")
    anat_df=anat_df[(anat_df["Mod."] == "CT")] # & (anat_df["Description"] != "Data Not Acquired")]
    anat_df=anat_df.rename(mapper={"Code":"PatientName","Series Date":"StudyDate"},axis=1)
        # get axial series, which have one of the following descriptions (w/ contrast and w/o contrast are both axial)
    anat_df=anat_df[(anat_df["Description"].str.contains("contrast|lung window|bone window",flags=re.IGNORECASE,regex=True)) & (~anat_df["Description"].str.contains("coronal|saggital",flags=re.IGNORECASE,regex=True).astype(bool))]
    pt_df=anat_df[["PatientName","StudyDate"]].drop_duplicates()
    
    # figure out which patient/studies have CAP coverage from the manually curated data
    coverage_man_df=pd.DataFrame([])
    patient_num=-1
    for (patient_name,study_date) in pt_df.itertuples(index=False):
        patient_num=patient_num+1
        print("%2.1f%% completed manual annotations." % (100*patient_num/len(pt_df)))
        this_pat_df=anat_df[(anat_df["PatientName"]==patient_name) & (anat_df["StudyDate"]==study_date)]
        this_pat_contains_chest=any(this_pat_df["Anatomy"].str.contains("Chest|thorax",flags=re.IGNORECASE,regex=True))
        this_pat_contains_abdomen=any(this_pat_df["Anatomy"].str.contains("Abdomen",flags=re.IGNORECASE,regex=True))
        this_pat_contains_pelvis=any(this_pat_df["Anatomy"].str.contains("Pelvis",flags=re.IGNORECASE,regex=True))
        
        row={"PatientCode":str(patient_name),"StudyDate":datetime.strptime(study_date,"%m/%d/%Y").strftime("%Y%m%d"),"HasCAPManual":this_pat_contains_chest and this_pat_contains_abdomen and this_pat_contains_pelvis}
        coverage_man_df=coverage_man_df.append(pd.DataFrame(row,index=[len(coverage_man_df)]))
    
    coverage_man_df.to_csv(constants.ANAT_COV_MAN_STORE_LOC)
else:
    coverage_meta_df=pd.read_csv(constants.ANAT_COV_META_STORE_LOC,dtype={"PatientCode":str,"StudyDate":str,"NonHeadSpatialCoverage":float},index_col=0)
    coverage_man_df=pd.read_csv(constants.ANAT_COV_MAN_STORE_LOC,dtype={"PatientCode":str,"StudyDate":str,"HasCAPManual":bool},index_col=0)
######################### MERGE METADATA AND MANUAL AND CALC CONFUSION MATRIX ############################
man_meta_df=coverage_meta_df.merge(coverage_man_df,on=["PatientCode","StudyDate"],how="inner")
man_meta_df.to_csv(constants.ANAT_COV_MAN_VS_META_LOC)
cm=confusion_matrix(man_meta_df["HasCAPManual"],man_meta_df["NonHeadSpatialCoverage"] > CAP_LOWER_THRESHOLD_MM)
print(cm)