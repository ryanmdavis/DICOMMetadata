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

def indexFolders(d_start):
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

    folder_df.to_csv(constants.FOLDER_SAVE_DIR)

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
    return i0,i1,i2,i3,error

def isContrastEnhanced(i0,series_dir):
    cbst = constants.EMPTY if (0x0018,0x1042) not in i0 else i0[0x0018,0x1042].value # contrast bolus start time
    series_name_contrast = constants.W_IV_CONTRAST in series_dir
    
    return cbst,series_name_contrast

def isSeriesAxial(i0,folder_path):

    folder_name_non_axial=any([non_ax_str in folder_path for non_ax_str in ["Sagittal","Coronal","sagittal","coronal"]])
    image_orientation_non_axial=((float(i0[0x0020,0x0037].value[0]) < constants.AXIAL_SCAN_THRESHOLD) or (float(i0[0x0020,0x0037].value[4]) < constants.AXIAL_SCAN_THRESHOLD)) if (0x0020,0x0037) in i0 else False

    return not (folder_name_non_axial or image_orientation_non_axial)

def getSliceThickness(i0,i1,i2,i3):
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
    
    return st_series,st_im_first,st_im_last,non_sorted_slice_warning

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

def isModalityCT(i0):
    return True if (((0x0008,0x0060) in i0) and (i0[0x0008,0x0060].value == "CT")) else False

def readMetadata(i0,i1,i2,i3,folder_path):
    meta_sum={}
    
    # folder path
    meta_sum["SeriesName"]=folder_path.split("\\")[-1]
    
    # z coverage
    series_z_coverage,image_z_coverage=seriesZCoverage(i0,i3)
    meta_sum["SeriesZCoverage"]=series_z_coverage
    meta_sum["ImageZCoverage"]=image_z_coverage
    
    # patient/date info
    meta_sum["PatientName"]=i0[0x0010,0x0010].value if (0x0010,0x0010) in i0 else constants.EMPTY 
    meta_sum["StudyDate"]=i0[0x0008,0x0020].value if (0x0008,0x0020) in i0 else constants.EMPTY
    
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
    
    # get slice thickness
    st_series,st_im_first,st_im_last,non_sorted_slice_warning=getSliceThickness(i0,i1,i2,i3)
    meta_sum["SliceThicknessSeries"]=st_series
    meta_sum["SliceThicknessImageFirst"]=st_im_first
    meta_sum["SliceThicknessImageLast"]=st_im_last
    meta_sum["SliceThickness_NotSortedWarning"]=non_sorted_slice_warning

    return meta_sum

def populateMetadataDatabase(root_dir):
    
    raise UserWarning("See comments below this line!")
    # The following are interfering with reading the dataframe in pandas
    # A few of the SliceThicknessSeries rows are empty, when they should be -999
    
    
    folder_df=pd.read_csv(constants.FOLDER_SAVE_DIR,index_col=0)
    
    # find the start index
    try:
        metadata_df=pd.read_csv(constants.METADATA_DATABASE_LOC)
        if len(metadata_df)==0:
            ii_start=0
        else:
            ii_start=metadata_df["FolderIndex"].max()+1
    except:
        ii_start=0
    
    keys=[]
    
    for ii in range(int(ii_start),len(folder_df)+1):
        folder_path=os.path.join(root_dir,folder_df[folder_df.index==ii]["DicomDir"].iloc[0])
        if "_CT\\" in folder_path:
            i0,i1,i2,i3,read_error=readDicoms(folder_path)
            
            # make sure we're actually dealing with a CT
            if not read_error:
                is_ct=isModalityCT(i0)
            else:
                is_ct=False    
            
            # now go through and find the metadata
            if (not read_error) and (is_ct):
                try:
                    meta_sum=readMetadata(i0, i1, i2, i3, folder_path)
                    meta_sum["FolderIndex"]=folder_df.index[ii]
                    
                except:
                    e = sys.exc_info()[0]
                    print( "Error: %s" % e )
                    print("Folder: %s" % folder_path)
                    raise RuntimeError
                
                if len(keys) == 0:
                    keys=list(meta_sum.keys())
                    keys.sort()
                
                if ii == 0:
                    with open(constants.METADATA_DATABASE_LOC,"w",newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(keys)
                
                with open(constants.METADATA_DATABASE_LOC,"a",newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([meta_sum[key] for key in keys])
            
        #     series_st,first_st,last_st=
                print("{:2.3%} complete".format(ii/len(folder_df)))
            elif not is_ct:
                print("Skipping non-CT volume: " + folder_path)
            else:
                print("error on folder: " + folder_path)
                with open(constants.ERROR_TRACKER_LOC,"a",newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(folder_path)
                    
def loadMetadata():
    dtype={"ContrastBolusStartTime":str,"ConvKernel":str,"FolderIndex":int,"ImageZCoverage":float,"IsAxial":bool,"Manufacturer":str,"ManufacturerModelName":str,"PatientName":str,"SeriesName":str,"SeriesNameWithContrast":bool,"SeriesZCoverage":float,"SliceThicknessImageFirst":float,"SliceThicknessImageLast":float,"SliceThicknessSeries":float,"StudyDate":str}
    md_df=pd.read_csv(constants.METADATA_DATABASE_LOC, encoding = "ISO-8859-1",dtype=dtype)
    
    dt_df=md_df.apply(lambda row:pd.to_datetime(row["StudyDate"],format='%Y%m%d',errors="coerce"),axis=1)
    md_df=md_df.drop("StudyDate",axis=1)
    md_df.insert(len(md_df.keys()),"StudyDate",dt_df)

    return md_df

if __name__ == "__main__":
    
#     indexFolders(constants.INDEX_ROOT_DIR)
    populateMetadataDatabase(constants.INDEX_ROOT_DIR)
#     folder_path="Z:\\data\\trials\\GO29436_IMpower150\\Images\\280255-10262\\41993\\20150826_CT\\20150826_1736_602_Sagittal\\"
#     i0,i1,i2,i3,error=readDicoms(folder_path)
#     meta_sum=readMetadata(i0, i1, i2, i3, folder_path)
