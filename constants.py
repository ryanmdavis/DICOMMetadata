'''
Created on Jan 27, 2020

@author: davisr28
'''


# Folder Locations

FOLDER_INDEX_150_SAVE_LOC       = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\indexed_folders_IMP150.csv"
FOLDER_INDEX_131_SAVE_LOC       = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\indexed_folders_IMP131.csv"
IMP150_METADATA_DATABASE_LOC    = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\metadata_database_IMP150.csv"
IMP131_METADATA_DATABASE_LOC    = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\metadata_database_IMP131.csv"
INDEX_IMP150_DIR                = "Z:\\data\\trials\\GO29436_IMpower150\\Images\\"
INDEX_IMP131_DIR                = "Z:\\data\\trials\\GO29437_IMpower131\\Images\\"
ERROR_TRACKER_LOC               = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\error_database.csv"
TEMP1_CSV                       = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\temp1_metadata.csv"
TEMP_CONTRAST1_CSV              = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\temp_contrast1_metadata.csv"
TEMP_CONTRAST2_CSV              = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\temp_contrast2_metadata.csv"
CONV_KERNAL_LIST_LOC            = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\conv_kernel_list.csv"
SERIES_COVERAGE_LOC             = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\series_coverage_loc.csv"
ANAT_COV_PIVOT_LOC              = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\anatomical_coverage_manual_designations_pivot.csv"
ANAT_COV_MAN_VS_META_LOC        = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\anatomical_coverage_manual_vs_meta.csv"    
ANAT_COV_MAN_STORE_LOC          = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\anatomical_coverage_manual_storage.csv"
ANAT_COV_META_STORE_LOC         = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\anatomical_coverage_metadata_storage.csv"
CONTRAST_GEAR_RESULT_LOC        = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\contrast_gear_classification_results.csv"
CT_MODEL_CONSISTENCY            = "C:\\Users\\davisr28\\Documents\\Python\\DICOMMetadata\\data\\ct_model_consistency.csv"


# Thresholds
AXIAL_SCAN_THRESHOLD            = 0.95
MM_RANGE                        = 0.05
Z_COVERAGE_TOL                  = 0.98

# strings
EMPTY                           = "empty"
INT_ERROR                       = -999
W_IV_CONTRAST                   = "w^IV contrast"