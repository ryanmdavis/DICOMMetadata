'''
Created on Feb 5, 2020

@author: davisr28
'''

import pandas as pd

def queryFloatRange(df,key,float_value_list,range_add):
    if type(float_value_list) is not list:
        float_value_list=[float_value_list]
    
    new_df=pd.DataFrame([])
    for float_value in float_value_list:
        new_df=new_df.append(df[(df[key] >= (float_value-range_add)) & (df[key] <= (float_value+range_add))])
    
    return new_df