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


if __name__ == "__main__":

    dfparams_file = "E:/Working/QingHaiSnow/CalRsim/test/Lumpara_buhahk.txt"
    job_dir = "E:/Working/QingHaiSnow/CalRsim/test"
    new_params = {
        'K': 1.5,
        'CG': 0.999,
        'CI': 0.97,
        'CS': 0.75,
        'Kech': 0.03,
        'KLWL': 5.0
    }
    update_lumpara(dfparams_file, job_dir, 'buhahk_test', new_params)