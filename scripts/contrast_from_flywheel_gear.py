'''
Created on Mar 2, 2020

@author: davisr28
'''

import pandas as pd
import constants
import numpy as np
from matplotlib import pyplot as plt

compute=True
if compute:
    class_df=pd.read_csv("G:\\Shared drives\\PHC DS Imaging\\Projects\\DICOM Metadata Characterization\\IMpower150_complete_report.csv")
    
    # deduce modality, contrast, anatomical coverage
    class_df.insert(len(class_df.keys()),"Modality",class_df.apply(lambda row:row["Visit Label"].split("_")[1],axis=1))
    
    # deduce contrast
    class_df.insert(len(class_df.keys()),"ContrastEnhanced",class_df.apply(lambda row:"With Contrast" in row["Classification List"],axis=1))
    
    # deduce study date
    class_df.insert(len(class_df.keys()),"StudyDate",class_df.apply(lambda row:row["Visit Label"].split("_")[0],axis=1))

    pt_df=class_df[["Subject Label","StudyDate"]].drop_duplicates()
    
    contrast_gear_df=pd.DataFrame([])
    patient_num=-1
    for (subject_label,study_date) in pt_df.itertuples(index=False):
        patient_num=patient_num+1
        print("%2.1f%% completed." % (100*patient_num/len(pt_df)))
        
        visit_has_mr=len(class_df[(class_df["Subject Label"]==subject_label) & (class_df["StudyDate"] == study_date) & (class_df["Modality"]=="MR")]) > 0
        visit_has_contrast=any(class_df[(class_df["Subject Label"]==subject_label) & (class_df["StudyDate"] == study_date)]["ContrastEnhanced"])
        
        row={"Subject Label":subject_label,"StudyDate":study_date,"HasContrastGear":visit_has_contrast,"HasMR":visit_has_mr}
        contrast_gear_df=contrast_gear_df.append(pd.DataFrame(row,index=[len(contrast_gear_df)]))
    
    contrast_gear_df.to_csv(constants.CONTRAST_GEAR_RESULT_LOC)

else:
    contrast_gear_df = pd.read_csv(constants.CONTRAST_GEAR_RESULT_LOC)

contrast_gear_df.insert(len(contrast_gear_df.keys()),"ContrastCount",contrast_gear_df["HasContrastGear"].astype(int))
contrast_gear_df.insert(len(contrast_gear_df.keys()),"VisitCount",[1]*len(contrast_gear_df))
pt_gear=pd.pivot_table(contrast_gear_df,index=["Subject Label"],values=["ContrastCount","VisitCount"],aggfunc=np.sum)

visits_without_contrast_gear=np.array(pt_gear["VisitCount"])-np.array(pt_gear["ContrastCount"])
plt.hist(visits_without_contrast_gear,bins=[-0.5 + ii for ii in range(12)],color="k")
plt.show()

print("t")