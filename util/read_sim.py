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
from joblib import Parallel, delayed

def read_sta_qsim(StaQSim_path: str) -> pd.DataFrame:

    colspecs = [(0, 11), (11, 21), (21, 31), (31, 46), (46, 61), (61, 76), (76, 91)]
    df = pd.read_fwf(StaQSim_path, colspecs=colspecs, header=None)
    df.columns = ['Year', 'Month', 'Day', 'Precipitation', 'Snowmelt_Liquid', 'Historical_Runoff', 'Sim_Q']
    df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    df = df[['Date', 'Precipitation', 'Snowmelt_Liquid', 'Historical_Runoff', 'Sim_Q']]
    df.replace('***************', 0.0, inplace=True)
    
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

def load_qsim_from_dir(job_yaml, result_dir) -> pd.DataFrame:

    with open(job_yaml, 'r', encoding='utf-8') as f:
        job_config = yaml.safe_load(f)
    job_ids = list(job_config.keys())

    qsim_dfs = []
    for job_id in job_ids:
        file_path = os.path.join(result_dir, f"StaQSim_{job_id}.txt")
        df = read_sta_qsim(file_path)
        df = df[['Date', 'Sim_Q']]
        df = df.rename(columns={'Sim_Q': job_id})

        if not qsim_dfs:
            qsim_dfs.append(df)
        else:
            qsim_dfs.append(df[[job_id]])
            
    qsim_df = pd.concat(qsim_dfs, axis=1)
    job_params = pd.DataFrame.from_dict(job_config, orient='index')
    params_df = pd.json_normalize(job_params['set_params'])
    params_df['job_id'] = job_params.index

    return qsim_df, params_df

def batch_load_qsim(yamls_dir, result_dir, **kwargs) -> pd.DataFrame:
    """
    """
    yamls = [f for f in os.listdir(yamls_dir) if f.endswith('.yaml')]
    yamls.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

    def process_yaml(yaml_file, res_dir):
        print(f"Loading {yaml_file}...")
        yaml_path = os.path.join(yamls_dir, yaml_file)
        return load_qsim_from_dir(yaml_path, res_dir)

    n_jobs = kwargs.get('n_jobs', -1)
    results = Parallel(n_jobs=n_jobs)(delayed(process_yaml)(yaml_file, result_dir) for yaml_file in yamls)

    date_df = results[0][0][['Date']]
    qsim_dfs = [res[0].drop(columns=['Date']) if 'Date' in res[0].columns else res[0] for res in results]
    all_qsim = pd.concat([date_df] + qsim_dfs, axis=1)
    all_jobs = pd.concat([res[1] for res in results], axis=0)

    all_qsim.reset_index(drop=True, inplace=True)
    all_jobs.reset_index(drop=True, inplace=True)

    return all_qsim, all_jobs
