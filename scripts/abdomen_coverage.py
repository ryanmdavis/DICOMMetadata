'''
Created on Feb 27, 2020

@author: davisr28
'''
import pandas as pd

# Read in the classification report
class_df=pd.read_csv("G:\\Shared drives\\PHC DS Imaging\\Projects\\DICOM Metadata Characterization\\IMpower150_complete_report.csv")

total_number_patients=len(class_df.drop_duplicates(subset="Subject Label"))
ab_df=class_df[class_df["Classification List"].str.contains("Abdomen")]
total_number_patients_with_abdomen=len(ab_df.drop_duplicates(subset="Subject Label"))

print("Of %d patients, %d had an at least one abdomen label during any visit." % (total_number_patients,total_number_patients_with_abdomen))