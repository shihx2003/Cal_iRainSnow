# -*- encoding: utf-8 -*-
'''
@File    :   read_StaQSim.py
@Create  :   2025-08-01 20:29:55
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import yaml
import pandas as pd
import numpy as np

def read_sta_qsim(StaQSim_path: str) -> pd.DataFrame:

    colspecs = [(0, 11), (11, 21), (21, 31), (31, 46), (46, 61), (61, 76), (76, 91)]
    df = pd.read_fwf(StaQSim_path, colspecs=colspecs, header=None)
    df.columns = ['Year', 'Month', 'Day', 'Precipitation', 'Snowmelt_Liquid', 'Historical_Runoff', 'Sim_Q']
    df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    df = df[['Date', 'Precipitation', 'Snowmelt_Liquid', 'Historical_Runoff', 'Sim_Q']]
    df.replace('***************', 9999999999.0000, inplace=True)
    
    df['Date'] = pd.to_datetime(df['Date'])
    df['Sim_Q'] = df['Sim_Q'].astype(float)
    
    return df

def load_qsim(job_yaml, basin, **kwargs) -> pd.DataFrame:

    result_dir = kwargs.get('result_dir', './Results/')

    with open(job_yaml, 'r', encoding='utf-8') as f:
        job_config = yaml.safe_load(f)
    job_ids = list(job_config.keys())

    qsim_dfs = []
    for job_id in job_ids:
        file_path = os.path.join(result_dir, basin, f"StaQSim_{job_id}.txt")
        df = read_sta_qsim(file_path)
        df = df[['Date', 'Sim_Q']]
        df = df.rename(columns={'Sim_Q': job_id})

        if not qsim_dfs:
            qsim_dfs.append(df)
        else:
            qsim_dfs.append(df[[job_id]])
            
    qsim_df = pd.concat(qsim_dfs, axis=1)

    return qsim_df

if __name__ == "__main__":
    job_yaml = '.\\jobs\\iRainSnowJob_buhahk_test_1.yaml'
    df = load_qsim(job_yaml, 'buhahk2')
    print(df)
    df.to_csv('E:/Working/QingHaiSnow/CalRsim/test/buhahk_qsim.csv', index=False)