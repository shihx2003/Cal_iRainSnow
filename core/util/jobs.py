# -*- encoding: utf-8 -*-
'''
@File    :   jobs.py
@Create  :   2025-07-29 18:52:41
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import yaml

def generate_jobs(param_df, job_group, **kwargs):
    """
    """
    to_update_params = kwargs.get('update_params', ['K', 'CG', 'CI', 'CS', 'Kech', 'KLWL'])
    jobs = {}
    for i, row in param_df.iterrows():

        job = {
            "job_id": f"{job_group}_{i+1}",
            "set_params": row.to_dict(),
        }
        jobs[f'{job_group}_{i+1}'] = job

        if not all(param in to_update_params for param in row.index):
            raise ValueError(f"Parameter {row.index} is not in the update list {to_update_params}")
        
    with open(f'./jobs/{job_group}.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(jobs, f, default_flow_style=False, sort_keys=False)
    return jobs

def generate_mon_jobs(params_ls, job_group, **kwargs):
    """
    Generate jobs for monthly parameter updates.
    """
    to_update_params = kwargs.get('update_params', ['K', 'CG', 'CI', 'CS', 'Kech', 'KLWL'])
    os.makedirs(f'./jobs/{job_group}', exist_ok=True)
    jobs = {}
    for i in range(len(params_ls)):
        job = {
            "job_id": f"{job_group}_{i+1}",
            "set_params": params_ls[i],
        }
        jobs[f'{job_group}_{i+1}'] = job

    jobs_dict = {}
    for job_id, params in jobs.items():
        params['set_params'].to_csv(f'./jobs/{job_group}/{job_id}.csv', index=False)
        jobs_dict[job_id] = {
            'job_id': job_id,
            'params_csv': f'./jobs/{job_group}/{job_id}.csv'
        }

    with open(f'./jobs/{job_group}.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(jobs_dict, f, default_flow_style=False, sort_keys=False)
    

    return jobs