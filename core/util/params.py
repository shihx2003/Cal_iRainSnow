# -*- encoding: utf-8 -*-
'''
@File    :   params.py
@Create  :   2025-07-29 19:00:55
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import yaml
import pandas as pd

PRECISION = 1e-6

def adjust_lumpara(df, new_params):
    """
    Adjust the lumpara DataFrame based on new parameters.
    For now, the whole year is the same values
    """
    for param, value in new_params.items():
        df[param] = value
    return df

def load_lumpara(file):
    if not os.path.exists(file):
        raise FileNotFoundError(f"File {file} does not exist.")
    df = pd.read_csv(file, sep='\t')
    return df

def write_lumpara(df, job_dir):
    df.to_csv(os.path.join(job_dir), sep='\t', index=False)

def update_lumpara(lumpara_file, job_dir, new_params):
    """
    Adjust the lumpara parameters and write to a new file.
    
    Parameters
    ----------
    lumpara_file : str
        Path to the original lumpara file.
    job_dir : str
        Directory to save the adjusted lumpara file.
    basin : str
        Name of the basin.
    new_params : dict
        Dictionary of new parameters to adjust in the lumpara file.

    Returns
    ----------
    None, writes the adjusted parameters to a new file.
    """
    df = load_lumpara(lumpara_file)
    df = adjust_lumpara(df, new_params)
    write_lumpara(df, job_dir)


def check_lumpara(lumpara_file, new_params):
    """
    Check if the lumpara file exists and is valid.
    """
    if not os.path.exists(lumpara_file):
        return False
    try:
        df = load_lumpara(lumpara_file)
        if df.empty:
            return False
        for param, value in new_params.items():
            if param not in df.columns:
                return False
            col_min = df[param].min()
            col_max = df[param].max()

            if not (abs(col_min - value) < PRECISION or abs(col_max - value) < PRECISION):
                return False
        return True
    except Exception as e:
        print(f"Error checking lumpara file: {e}")
        return False


def adjust_mon_lumpara(df, new_params, **kwargs):
    df = df.copy()
    params_names = kwargs.get("params_names", ['K', 'CG', 'CI', 'CS', 'Kech', 'KLWL'])
    for param in params_names:
        df[param] = new_params[param]
    return df

def update_mon_lumpara(lumpara_file, job_dir, params_df, **kwargs):
    """
    """
    df = load_lumpara(lumpara_file)
    df = adjust_mon_lumpara(df, params_df, **kwargs)
    write_lumpara(df, job_dir)

