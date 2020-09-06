'''
Created on Jan 27, 2020

Note to self: need to add slice spacing and body part examined tags

@author: davisr28
'''

import os
import pandas as pd
import constants
import pydicom
import csv
import sys

# scan frequency: average time between scans, average time between first and last scan
# z coverage of series
# contrast use = 
# recon kernal
# slice thickness

def indexFolders(d_start,save_loc):
    folder_df=pd.DataFrame([])
    patient_num=0
    
    num_patients=len(os.listdir(d_start))
    
    for root, dirs, files in os.walk(d_start):
        if len(root) == 53:
            patient_num=patient_num+1
            print("%f %% complete " %(100*patient_num/num_patients))
        # rules out scouts (len(files)==1) and directories without dicom files
        if (len(files) > 1) and ((".dcm" in files[0]) or (".dcm" in files[1])):
            folder_df=folder_df.append(pd.DataFrame([root[len(d_start):]],columns=["DicomDir"]),ignore_index=True)

    folder_df.to_csv(constants.FOLDER_INDEX_131_SAVE_LOC)

def readDicoms(folder):
    # note that for this function, I'm reading the 2nd, 3rd, 2nd to last, 3rd to last scans because the first (and maybe last) 
    # could be a localizer
    dcm_files = [file for file in os.listdir(folder) if ".dcm" in file]
    
    i_file=0
    image=pydicom.dcmread(os.path.join(folder,dcm_files[i_file]))
    while (0x0008,0x0008) in image and any(["LOCALIZER" in element for element in image[0x0008,0x0008].value]) and (i_file<len(dcm_files)-1):
        i_file=i_file+1
        image=pydicom.dcmread(os.path.join(folder,dcm_files[i_file]))
        
    
    try:
        i0=pydicom.dcmread(os.path.join(folder,dcm_files[i_file]))
        i1=pydicom.dcmread(os.path.join(folder,dcm_files[i_file+1]))
        i2=pydicom.dcmread(os.path.join(folder,dcm_files[-3]))
        i3=pydicom.dcmread(os.path.join(folder,dcm_files[-2]))
        error=False
    except:
        error=True
        (i0,i1,i2,i3) = (0,0,0,0)
    return i0,i1,i2,i3,error,len(dcm_files)

def isContrastEnhanced(i0,series_dir):
    cbst = constants.EMPTY if (0x0018,0x1042) not in i0 else i0[0x0018,0x1042].value # contrast bolus start time
    series_name_contrast = constants.W_IV_CONTRAST in series_dir
    
    return cbst,series_name_contrast

def isSeriesAxial(i0,folder_path):

    folder_name_non_axial=any([non_ax_str in folder_path for non_ax_str in ["Sagittal","Coronal","sagittal","coronal"]])
    image_orientation_non_axial=((float(i0[0x0020,0x0037].value[0]) < constants.AXIAL_SCAN_THRESHOLD) or (float(i0[0x0020,0x0037].value[4]) < constants.AXIAL_SCAN_THRESHOLD)) if (0x0020,0x0037) in i0 else False

    return not (folder_name_non_axial or image_orientation_non_axial)

def getSliceThickness(i0,i1,i2,i3,num_dcm_files):
    st_series=i0[0x0018,0x0050].value if (0x0018,0x0050) in i0 else constants.INT_ERROR 
    slice_pos_delta_first=(i0[0x0020,0x0032].value[2]-i1[0x0020,0x0032].value[2]) if ((0x0020,0x0032) in i0) and ((0x0020,0x0032) in i1) else constants.INT_ERROR
    slice_pos_delta_last=(i2[0x0020,0x0032].value[2]-i3[0x0020,0x0032].value[2]) if ((0x0020,0x0032) in i2) and ((0x0020,0x0032) in i3) else constants.INT_ERROR
    
    # since images may not be sorted in the folder, need to make sure we're acconting for how many slices are in between the images
    if len(str(i0[0x0020,0x0013].value))*len(str(i1[0x0020,0x0013].value))*len(str(i2[0x0020,0x0013].value))*len(str(i3[0x0020,0x0013].value)) != 0:
        # if none of the strings are empty
        first_instance_num_delta=i1[0x0020,0x0013].value-i0[0x0020,0x0013].value
        last_instance_num_delta=i3[0x0020,0x0013].value-i2[0x0020,0x0013].value
    else:
        # if one of them is zero, write the instance num delta to 1,1
        # right now, the user is not being notified when this statement occurs
        first_instance_num_delta,last_instance_num_delta=(1,1)
    
    st_im_first=abs(slice_pos_delta_first/first_instance_num_delta) if first_instance_num_delta != 0 else constants.INT_ERROR
    st_im_last=abs(slice_pos_delta_last/last_instance_num_delta) if last_instance_num_delta != 0 else constants.INT_ERROR
    
    if first_instance_num_delta != 1 or last_instance_num_delta != 1:
        non_sorted_slice_warning=str(True)
    else:
        non_sorted_slice_warning=str(False)
    
    
    # infer the position of the first and last slice
    try:
        mm_per_instance=slice_pos_delta_first/first_instance_num_delta if first_instance_num_delta != 0 else constants.INT_ERROR
        i0_instance=float(i0[0x0020,0x0013].value) if (0x0020,0x0013) in i0  else constants.INT_ERROR
        i0_pos=float(i0[0x0020,0x0032].value[2]) if (0x0020,0x0032) in i0  else float(constants.INT_ERROR)
        
        first_inst_num=1
        last_inst_num=num_dcm_files
        
        last_slice_pos=(i0_instance-last_inst_num)*mm_per_instance+i0_pos
        first_slice_pos=(i0_instance-first_inst_num)*mm_per_instance+i0_pos
    except:
        last_slice_pos=float(constants.INT_ERROR)
        first_slice_pos=float(constants.INT_ERROR)
    return st_series,st_im_first,st_im_last,non_sorted_slice_warning,last_slice_pos,first_slice_pos

def seriesZCoverage(i0,i3):
    if ((0x0020,0x1041) in i0) and (((0x0020,0x1041) in i3) and (len(str(i0[0x0020,0x1041].value))>0) and (len(str(i3[0x0020,0x1041].value)))>0):
        series_z_coverage=abs(float(i0[0x0020,0x1041].value)-float(i3[0x0020,0x1041].value))
    else:
        series_z_coverage = constants.INT_ERROR
    
    if ((0x0020,0x0032) in i0) and ((0x0020,0x0032) in i3):
        image_z_coverage=abs(float(i0[0x0020,0x0032].value[2]) -float(i3[0x0020,0x0032].value[2]))
    else:
        image_z_coverage = constants.INT_ERROR
    return series_z_coverage,image_z_coverage

def seriesZCoverage2(st_im_last,num_dcm_files):
    return st_im_last*num_dcm_files


def isModalityCT(i0):
    return True if (((0x0008,0x0060) in i0) and (i0[0x0008,0x0060].value == "CT")) else False

def isModalityPT(i0):
    return True if (((0x0008,0x0060) in i0) and (i0[0x0008,0x0060].value == "PT")) else False

def readMetadataFolder(folder):
    i0,i1,i2,i3,read_error,num_dcm_files = readDicoms(folder)
    meta_sum = readMetadata(i0,i1,i2,i3,folder,num_dcm_files)
    return meta_sum

def readMetadata(i0,i1,i2,i3,folder_path,num_dcm_files):
    meta_sum={}
    
    # folder path
    meta_sum["SeriesName"]=folder_path.split("\\")[-1]
    
    # get slice thickness
    st_series,st_im_first,st_im_last,non_sorted_slice_warning,last_slice_pos,first_slice_pos=getSliceThickness(i0,i1,i2,i3,num_dcm_files)
    meta_sum["SliceThicknessSeries"]=st_series
    meta_sum["SliceThicknessImageFirst"]=st_im_first
    meta_sum["SliceThicknessImageLast"]=st_im_last
    meta_sum["SliceThickness_NotSortedWarning"]=non_sorted_slice_warning
    meta_sum["FirstSlice"]=first_slice_pos
    meta_sum["LastSlice"]=last_slice_pos
    
    # z coverage
    meta_sum["SeriesZCoverageImg"]=seriesZCoverage2((st_im_last+st_im_last)/2,num_dcm_files)
    cov1=abs(meta_sum["LastSlice"]-meta_sum["FirstSlice"])
    cov2=abs(meta_sum["SeriesZCoverageImg"])
#     print("%s,%s"%(str(cov1),str(cov2)))
    
    # cov1*0.95 < cov2 < cov1*1.05:
    if ((cov1*constants.Z_COVERAGE_TOL) <= cov2) and (cov2 <= cov1*(2-constants.Z_COVERAGE_TOL)):
        meta_sum["SeriesCoverageErrorFlag"] = False
    else:
        meta_sum["SeriesCoverageErrorFlag"] = True

    # patient/date info
    meta_sum["PatientCode"]=i0[0x0010,0x0010].value if (0x0010,0x0010) in i0 else constants.EMPTY 
    meta_sum["StudyDate"]=i0[0x0008,0x0020].value if (0x0008,0x0020) in i0 else constants.EMPTY
    meta_sum["SitePatient"]=folder_path.split("\\")[5]
    
    # software
    meta_sum["ConvKernel"]=i0[0x0018,0x1210].value if (0x0018,0x1210) in i0 else constants.EMPTY
    meta_sum["Manufacturer"]=i0[0x0008,0x0070].value if (0x0008,0x0070) in i0 else constants.EMPTY 
    meta_sum["ManufacturerModelName"]=i0[0x0008,0x1090].value if (0x0008,0x1090) in i0 else constants.EMPTY
    
    # check if axial
    meta_sum["IsAxial"] = isSeriesAxial(i0,folder_path)
    
    # check for contrast enhancementdavis
    cbst,series_name_contrast=isContrastEnhanced(i0, folder_path)
    meta_sum["ContrastBolusStartTime"]=cbst
    meta_sum["SeriesNameWithContrast"]=series_name_contrast
    
    return meta_sum

def populateMetadataDatabase(root_dir,folder_index_loc,metadata_database_loc,modality):
    
#     raise UserWarning("See comments below this line!")
    # The following are interfering with reading the dataframe in pandas
    # A few of the SliceThicknessSeries rows are empty, when they should be -999
    
    
    folder_df=pd.read_csv(folder_index_loc,index_col=0)
    
    # find the start index
    try:
        metadata_df=pd.read_csv(metadata_database_loc)
        if len(metadata_df)==0:
            ii_start=0
        else:
            ii_start=metadata_df["FolderIndex"].max()+1
    except:
        ii_start=0
        first_row = True
    
    keys = []
    
    for ii in range(int(ii_start),len(folder_df)+1):
        folder_path=os.path.join(root_dir,folder_df[folder_df.index==ii]["DicomDir"].iloc[0])
        if "_"+modality+"\\" in folder_path:
            i0, i1, i2, i3, read_error, num_dcm_files=readDicoms(folder_path)
            
            # make sure we're actually dealing with a CT
            if not read_error:
                if modality == "CT":
                    is_modality_correct = isModalityCT(i0)
                elif modality == "PT":
                    is_modality_correct = isModalityPT(i0)
                else:
                    raise RuntimeError("can't handle modality %s" % modality)
            else:
                is_modality_correct=False
            
            # now go through and find the metadata
            if (not read_error) and (is_modality_correct):
                try:
                    meta_sum=readMetadata(i0, i1, i2, i3, folder_path,num_dcm_files)
                    meta_sum["FolderIndex"]=folder_df.index[ii]
                    meta_sum["NumFiles"]=num_dcm_files
                except:
                    e = sys.exc_info()[0]
                    print( "Error: %s" % e )
                    print("Folder: %s" % folder_path)
                    raise RuntimeError
                
                if len(keys) == 0:
                    keys=list(meta_sum.keys())
                    keys.sort()
                
                if first_row:
                    print("Wrote column names")
                    with open(metadata_database_loc,"w",newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(keys)
                    first_row = False
                
                with open(metadata_database_loc,"a",newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([meta_sum[key] for key in keys])
            
        #     series_st,first_st,last_st=
                print("{:2.3%} complete".format(ii/len(folder_df)))
            elif not is_modality_correct:
                print("Skipping non-%s volume: "%modality + folder_path)
            else:
                print("error on folder: " + folder_path)
                with open(constants.ERROR_TRACKER_LOC,"a",newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(folder_path)
                    
def loadMetadata(file_location):
    dtype={"ContrastBolusStartTime":str,"ConvKernel":str,"FolderIndex":int,"ImageZCoverage":float,"IsAxial":bool,"Manufacturer":str,"ManufacturerModelName":str,"PatientCode":str,"SeriesName":str,"SeriesNameWithContrast":bool,"SeriesZCoverage":float,"SliceThicknessImageFirst":float,"SliceThicknessImageLast":float,"SliceThicknessSeries":float,"StudyDate":str,"FirstSlice":float,"LastSlice":float}
    md_df=pd.read_csv(file_location, encoding = "ISO-8859-1",dtype=dtype)
    
    dt_df=md_df.apply(lambda row:pd.to_datetime(row["StudyDate"],format='%Y%m%d',errors="coerce"),axis=1)
    md_df=md_df.drop("StudyDate",axis=1)
    md_df.insert(len(md_df.keys()),"StudyDate",dt_df)

    return md_df

if __name__ == "__main__":

    # indexFolders(constants.INDEX_IMP131_DIR,constants.FOLDER_INDEX_131_SAVE_LOC)
    populateMetadataDatabase(constants.INDEX_IMP131_DIR,constants.FOLDER_INDEX_131_SAVE_LOC,constants.IMP131_METADATA_DATABASE_LOC,"PT")
#     folder_path="Z://data//trials//GO29436_IMpower150//Images//279836-11994//11573//20160916_CT//20160916_1459_3_w^IV contrast//"
#     i0,i1,i2,i3,error,num_files=readDicoms(folder_path)
#     meta_sum=readMetadata(i0, i1, i2, i3, folder_path,num_files)
    print("Done")
