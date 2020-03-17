'''
Created on Mar 3, 2020

@author: davisr28
'''
import pandas as pd
import constants
import numpy as np
import metadata

meta_df=metadata.loadMetadata(file_location=constants.METADATA_DATABASE_LOC)
meta_df.insert(0,"count",[1]*len(meta_df))
model_pivot_df=(pd.pivot_table(meta_df, index=["PatientCode"], columns=["ManufacturerModelName"], values=["count"],aggfunc=np.sum) > 0).astype(int)
manufacturer_pivot_df=(pd.pivot_table(meta_df, index=["PatientCode"], columns=["Manufacturer"], values=["count"],aggfunc=np.sum) > 0).astype(int)
patient_model_count_df=pd.DataFrame(model_pivot_df.sum(axis=1),columns=["Model"])
patient_manufacturer_count_df=pd.DataFrame(manufacturer_pivot_df.sum(axis=1),columns=["Manufacturer"])

model_manuf_df=patient_model_count_df.join(patient_manufacturer_count_df)
# model_manuf_df=patient_model_count_df.join(patient_manufacturer_count_df,lsuffix="_model",rsuffix="_manufacturer")

model_manuf_df.to_csv(constants.CT_MODEL_CONSISTENCY)
print("Done")