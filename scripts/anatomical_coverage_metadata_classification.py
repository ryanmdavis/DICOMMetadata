'''
Created on Feb 26, 2020

@author: davisr28
'''

import pandas as pd
import constants

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
    this_pt_df=class_df[(class_df["Subject Label"]==subject_label) & (class_df["StudyDate"]==study_date)]
    this_pt_contains_chest=any(this_pt_df["Classification List"].str.contains("Chest"))
    this_pt_contains_abdomen=any(this_pt_df["Classification List"].str.contains("Abdomen"))
    this_pt_contains_pelvis=any(this_pt_df["Classification List"].str.contains("Pelvis"))
    this_pt_contains_whole_body=any(this_pt_df["Classification List"].str.contains("Whole Body"))
    
    row={"Subject Label":subject_label,"StudyDate":study_date,"HasC":this_pt_contains_chest,"HasA":this_pt_contains_abdomen,"HasP":this_pt_contains_pelvis,"HasCAP":(this_pt_contains_chest and this_pt_contains_abdomen and this_pt_contains_pelvis) or this_pt_contains_whole_body,"HasAnatomyClassified":this_pt_contains_chest or this_pt_contains_abdomen or this_pt_contains_pelvis or this_pt_contains_whole_body}
    coverage_df=coverage_df.append(pd.DataFrame(row,index=[len(coverage_df)]))

coverage_df.to_csv(constants.TEMP1_CSV)
print("t")


# find percent with abdomen
class_df=pd.read_csv("G:\\Shared drives\\PHC DS Imaging\\Projects\\DICOM Metadata Characterization\\IMpower150_complete_report.csv")

total_number_patients=len(class_df.drop_duplicates(subset="Subject Label"))
ab_df=class_df[class_df["Classification List"].str.contains("Abdomen")]
total_number_patients_with_abdomen=len(ab_df.drop_duplicates(subset="Subject Label"))