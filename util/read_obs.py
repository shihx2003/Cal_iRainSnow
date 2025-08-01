# -*- encoding: utf-8 -*-
'''
@File    :   read_obs.py
@Create  :   2025-08-01 21:55:41
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import pandas as pd

def load_qobs(basin, **kwargs) -> pd.DataFrame:
    """
    """
    obs_dir = kwargs.get('obs_dir', './Source/Qobs/')
    df = pd.read_csv(obs_dir + f'{basin}_qobs.csv')
    df.rename(columns={'Qobs': 'obs'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])

    return df

def div_q(df, start, end) -> pd.DataFrame:

    df = df.copy()
    
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
    
    mask = (df['Date'] >= start) & (df['Date'] <= end)
    mask_df = df[mask].reset_index(drop=True)

    return mask_df

if __name__ == "__main__":
    df = load_qobs('buhahk')
    print(df)
    dfk = div_q(df, '2015-01-01', '2022-12-31')
    print(dfk)