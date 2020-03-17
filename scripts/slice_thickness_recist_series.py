'''
Created on Feb 5, 2020

@author: davisr28
'''

import pandas as pd
import constants
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import query as q

matplotlib.rcParams.update({'font.size': 16}) 

dtype={"ContrastBolusStartTime":str,"ConvKernel":str,"FolderIndex":int,"ImageZCoverage":float,"IsAxial":bool,"Manufacturer":str,"ManufacturerModelName":str,"PatientName":str,"SeriesName":str,"SeriesNameWithContrast":bool,"SeriesZCoverage":float,"SliceThicknessImageFirst":float,"SliceThicknessImageLast":float,"SliceThicknessSeries":float,"StudyDate":str}
md_df=pd.read_csv(constants.METADATA_DATABASE_LOC, encoding = "ISO-8859-1",dtype=dtype,index_col="FolderIndex")
folders_df=pd.read_csv(r"C:\Users\davisr28\Documents\Python\DICOMMetadata\data\indexed_folders.csv",index_col=0)
folders_df.insert(len(folders_df.keys()),"FolderName",folders_df.apply(lambda row:row["DicomDir"].split("\\")[3],axis=1))
folders_df=folders_df.drop("DicomDir",axis=1)

# join fodler index in md_df to indext folders, which we'll later merge with the recist series dataframe
md_df=md_df.join(folders_df)

recist_df=pd.read_csv(r"G:\Shared drives\PHC DS Imaging\Projects\DICOM Metadata Characterization\GO29436_recist_series.csv",dtype={"Date":str})
recist_df.insert(len(recist_df.keys()),"FolderName",recist_df.apply(lambda row:row["Path"].split("/")[12],axis=1))
recist_df=recist_df.rename(mapper={"Patient":"SitePatient","Date":"StudyDate"},axis=1)

# left metadata onto recist folders
recist_md_df=recist_df.merge(md_df,on=["SitePatient","StudyDate","FolderName"],how="left")
num_bins=50
plt.hist(recist_md_df["SliceThicknessImageLast"],bins=[ii/num_bins for ii in range(0,6*num_bins)])
plt.xlabel("slice thickness (mm)")
plt.ylabel("number of image series")
plt.title("Histogram of slice thicknesses of series read by RECIST")
plt.show()