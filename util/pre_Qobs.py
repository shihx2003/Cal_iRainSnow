# -*- encoding: utf-8 -*-
'''
@File    :   pre_Qobs.py
@Create  :   2025-07-28 21:03:29
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib

import pandas as pd
import numpy as np

def generate_daily_dates(year):
    start = f'{year}-01-01'
    end = f'{year}-12-31'
    dates = pd.date_range(start=start, end=end, freq='D')
    return dates

basin = ['纳赤台','察汗乌苏', '新寨', '布哈河口', '牛场']
basin_en = ['nachitai', 'chanhanwusu', 'xinzai', 'buhahk', 'niuchang']
for i in range(len(basin)):
    print(f'Processing {basin[i]}...')
    qobs_df = pd.read_excel("E:/Working/QingHaiSnow/CalRsim/BasinRun/Qobs/02-五站日均流量.xlsx", sheet_name=basin[i])
    basin_q = []
    basin_t = []
    for year in range(2014, 2024):
        column_name = f"{year}年"
        temp_dates = generate_daily_dates(year)
        temp_qobs = qobs_df[column_name].values
        temp_qobs = temp_qobs[~np.isnan(temp_qobs)]

        basin_q.append(temp_qobs)
        basin_t.append(temp_dates)
    basin_q = np.concatenate(basin_q)
    basin_t = np.concatenate(basin_t)
    qobs = pd.DataFrame({
        'Date': basin_t,
        'Qobs': basin_q
    })
    qobs.to_csv(f'E:/Working/QingHaiSnow/CalRsim/BasinRun/Qobs/{basin_en[i]}_qobs.csv', index=False)


    
