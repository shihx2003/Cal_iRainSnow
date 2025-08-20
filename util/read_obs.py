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

def div_q_chunk(df, start, end, chunk_size=500) -> pd.DataFrame:
    """
    """
    df = df.copy()
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
    result = []
    for start_idx in range(0, len(df), chunk_size):
        chunk = df.iloc[start_idx:start_idx+chunk_size]
        mask = (chunk['Date'] >= start) & (chunk['Date'] <= end)
        chunk_filtered = chunk.loc[mask]
        result.append(chunk_filtered)
    mask_df = pd.concat(result, ignore_index=True)
    
    return mask_df

def load_pretem(basin, **kwargs) -> pd.DataFrame:
    """
    """
    pre_file = kwargs.get('pre_file', './Source/meteodata/pre_avg.csv')
    tem_file = kwargs.get('tem_file', './Source/meteodata/tem_avg.csv')
    

    pre = pd.read_csv(pre_file)
    pre.rename(columns={'time': 'Date'}, inplace=True)
    pre['Date'] = pd.to_datetime(pre['Date'])

    tem = pd.read_csv(tem_file)
    tem.rename(columns={'time': 'Date'}, inplace=True)
    tem['Date'] = pd.to_datetime(tem['Date'])

    pre = pre[['Date', basin]]
    tem = tem[['Date', basin]]

    pre.rename(columns={basin: 'pre'}, inplace=True)
    tem.rename(columns={basin: 'tem'}, inplace=True)

    return pre, tem


if __name__ == "__main__":
    df = load_qobs('buhahk')
    print(df)
    dfk = div_q(df, '2015-01-01', '2022-12-31')
    print(dfk)