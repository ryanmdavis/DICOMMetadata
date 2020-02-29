'''
Created on Feb 28, 2020

@author: davisr28
'''
import pandas as pd
import re
import metadata
import matplotlib.pyplot as plt
import constants
import numpy as np

compute=False
if compute:
    # load metadata dataframe
    meta_df=metadata.loadMetadata(file_location="C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\metadata_database - backup 2-27-2020.csv")
    series_num_df=meta_df.apply(lambda row:row["SeriesName"].split("_")[2],axis=1).astype(int)
    meta_df.insert(len(meta_df.keys()),"Series #",series_num_df)
    meta_df=meta_df.rename(mapper={"PatientName":"PatientCode"},axis=1)
    
    # load manually curated dataframe
    man_df=pd.read_csv("C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\GO29436_TaskSeries_list_20190219.csv",dtype={"Code":str})
    man_df.loc[man_df["Anatomy"].isna(),"Anatomy"]=""
    dt_man_df=man_df.apply(lambda row:pd.to_datetime(row["Series Date"],format='%m/%d/%Y',errors="coerce"),axis=1)
    man_df.insert(len(man_df.keys()),"StudyDate",dt_man_df)
    man_df=man_df.rename(mapper={"Code":"PatientCode"},axis=1)
    
    # find the axial cap scans
    match = lambda df,el,s: df[el].str.contains(s,regex=True,flags=re.IGNORECASE)
    man_cap_df=man_df[(man_df["Anatomy"]=="Chest\\Abdomen\\Pelvis") & match(man_df,"Description","contrast")]

    series_coverage_df=man_cap_df.merge(meta_df,on=["PatientCode","StudyDate","Series #"],how="inner")[["PatientCode","StudyDate","Series #","SeriesZCoverage"]]
    series_coverage_df.to_csv(constants.SLICE_THICK_DIST_LOC)

else:

    series_coverage_df = pd.read_csv(constants.SLICE_THICK_DIST_LOC)



ax1 = plt.subplot(1,2,1)
ax1.hist(np.array(series_coverage_df["SeriesZCoverage"]),color="k")
ax1.set(xlabel="Z coverage",ylabel="Number of Series")

plt.show()

print("t")
