'''
Created on Feb 28, 2020

@author: davisr28
'''
import pandas as pd
import re
import metadata
import matplotlib.pyplot as plt
import matplotlib
import constants
import numpy as np

# graph parameters
matplotlib.rcParams.update({'font.size': 16}) 

# convenience function for regex matching in df
match = lambda df,el,s: df[el].str.contains(s,regex=True,flags=re.IGNORECASE)

compute=False
if compute:
    # load metadata dataframe
    meta_df=metadata.loadMetadata(file_location="C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\metadata_database.csv")
    series_num_df=meta_df.apply(lambda row:row["SeriesName"].split("_")[2],axis=1).astype(int)
    meta_df.insert(len(meta_df.keys()),"Series #",series_num_df)
    meta_df=meta_df.rename(mapper={"PatientName":"PatientCode","NumFiles":"# Files"},axis=1)
    
    # load manually curated dataframe
    man_df=pd.read_csv("C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\GO29436_TaskSeries_list_20190219.csv",dtype={"Code":str})
    man_df.loc[man_df["Anatomy"].isna(),"Anatomy"]=""
    dt_man_df=man_df.apply(lambda row:pd.to_datetime(row["Series Date"],format='%m/%d/%Y',errors="coerce"),axis=1)
    man_df.insert(len(man_df.keys()),"StudyDate",dt_man_df)
    man_df=man_df.rename(mapper={"Code":"PatientCode"},axis=1)
    man_df=man_df[~man_df["Description"].isna()]
    
    # get axial scans
    man_axial_df=man_df[match(man_df,"Description","contrast")]
    
    # Match series to scan coverage
    series_coverage_df=man_axial_df.merge(meta_df,on=["PatientCode","StudyDate","Series #","# Files"],how="inner")[["PatientCode","StudyDate","Series #","# Files","Anatomy","SeriesZCoverageImg","FirstSlice","LastSlice"]]
    print("Matched %f.f percent of axial manually curated series." % (100*len(series_coverage_df)/len(man_axial_df)))
    series_coverage_df.to_csv(constants.SERIES_COVERAGE_LOC)

#     man_cap_df=man_df[(man_df["Anatomy"]=="Chest\\Abdomen\\Pelvis") & match(man_df,"Description","contrast")]
# 
#     series_coverage_df=man_cap_df.merge(meta_df,on=["PatientCode","StudyDate","Series #","# Files"],how="inner")[["PatientCode","StudyDate","Series #","# Files","SeriesZCoverageImg"]]
#     series_coverage_df.to_csv(constants.SLICE_THICK_DIST_LOC)

else:

    series_coverage_df = pd.read_csv(constants.SERIES_COVERAGE_LOC)

# remove series where there was an error, which were set to a negative number
series_coverage_df=series_coverage_df[series_coverage_df["SeriesZCoverageImg"] >=10]

hist_bins=[0 + 50*ii for ii in range(30)]
bin_centers=[np.mean([hist_bins[ii],hist_bins[ii+1]]) for ii in range(len(hist_bins)-1)]

cap_hist=np.histogram(np.array(series_coverage_df[(series_coverage_df["Anatomy"]=="Chest\\Abdomen\\Pelvis")]["SeriesZCoverageImg"]),bins=hist_bins)
ca_hist=np.histogram(np.array(series_coverage_df[(series_coverage_df["Anatomy"]=="Chest\\Abdomen")]["SeriesZCoverageImg"]),bins=hist_bins)
ap_hist=np.histogram(np.array(series_coverage_df[(series_coverage_df["Anatomy"]=="Abdomen\\Pelvis")]["SeriesZCoverageImg"]),bins=hist_bins)
c_hist=np.histogram(np.array(series_coverage_df[(series_coverage_df["Anatomy"]=="Chest")]["SeriesZCoverageImg"]),bins=hist_bins)
brain_hist=np.histogram(np.array(series_coverage_df[(series_coverage_df["Anatomy"]=="Brain")]["SeriesZCoverageImg"]),bins=hist_bins)


# ax1.hist(np.array(man_cap_df["SeriesZCoverageImg"]),color="k",bins=[0 + 50*ii for ii in range(30)])
plt.plot(bin_centers,cap_hist[0],label="Chest/Abdomen/Pelvis")
plt.plot(bin_centers,ca_hist[0],label="Chest/Abdomen")
plt.plot(bin_centers,ap_hist[0],label="Abdomen/Pelvis")
plt.plot(bin_centers,brain_hist[0],label="Brain")
plt.plot(bin_centers,c_hist[0],label="Chest")


plt.legend(loc="upper right")
plt.xlabel("series z coverage (mm)")
plt.ylabel("number of series")
plt.show()

print("t")
