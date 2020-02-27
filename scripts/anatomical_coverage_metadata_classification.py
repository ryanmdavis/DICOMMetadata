'''
Created on Feb 26, 2020

@author: davisr28
'''

import pandas as pd

class_df=pd.read_csv("G:\\Shared drives\\PHC DS Imaging\\Projects\\DICOM Metadata Characterization\\IMpower150_complete_report.csv")

# deduce modality, contrast, anatomical coverage
class_df.insert(len(class_df.keys()),"Modality",class_df.apply(lambda row:row["Visit Label"].split("_")[1],axis=1))

# deduce contrast
class_df.insert(len(class_df.keys()),"ContrastEnhanced",class_df.apply(lambda row:"With Contrast" in row["Classification List"],axis=1))

# deduce study date
class_df.insert(len(class_df.keys()),"StudyDate",class_df.apply(lambda row:row["Visit Label"].split("_")[0],axis=1))
   
# deduce anatomical coverage
pt_df=class_df[["Subject Label","StudyDate"]].drop_duplicates()

coverage_df=pd.DataFrame([])
patient_num=-1
for (subject_label,study_date) in pt_df.itertuples(index=False):
    patient_num=patient_num+1
    print("%2.1f%% completed." % (100*patient_num/len(pt_df)))
    this_pat_df=class_df[(class_df["Subject_label"]==subject_label) & (class_df["StudyDate"]==study_date)]
    this_pat_contains_chest=any(this_pat_df["Anatomy"].str.contains("Chest"))
    this_pat_contains_abdomen=any(this_pat_df["Anatomy"].str.contains("Abdomen"))
    this_pat_contains_pelvis=any(this_pat_df["Anatomy"].str.contains("Pelvis"))
    
    row={"Subject Label":subject_label,"StudyDate":study_date,"HasCAP":this_pat_contains_chest and this_pat_contains_abdomen and this_pat_contains_pelvis}
    coverage_df=coverage_df.append(pd.DataFrame(row,index=[len(coverage_df)]))
print("t")