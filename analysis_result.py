# -*- encoding: utf-8 -*-
'''
@File    :   analysis_result.py
@Create  :   2025-08-03 23:38:40
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import yaml
import random
import logging
import numpy as np
import pandas as pd
from uuid import uuid4

from core.util.objfun import NSE, dict_to_df
from util.read_obs import load_qobs, div_q_chunk, div_q
from util.read_sim import load_qsim, batch_load_qsim, read_sta_qsim

# work_dir = "Full_PSO_buhahk"
work_dir = "Full_PSO_xinzai"
# work_dir = "Full3_PSO_niuchang"

print(f"Loading observations for {work_dir.split('_')[-1]}")
qobs = load_qobs(f"{work_dir.split('_')[-1]}")
qsim = pd.read_feather(f"./Analysis/{work_dir}/{work_dir}_results.feather")
job_params = pd.read_feather(f"./Analysis/{work_dir}/{work_dir}_jobs.feather")
qsim.to_csv(f"./Analysis/{work_dir}/{work_dir}_results.csv", index=False)

qsim = div_q(qsim, '2015-01-01', '2023-12-31')
qobs = div_q(qobs, '2015-01-01', '2023-12-31')
all_q = qsim.copy()
all_q['Date'] = pd.to_datetime(all_q['Date'])
all_q["obs"] = qobs["obs"]

all_q = all_q.set_index("Date")
all_q_mon = all_q.groupby(pd.Grouper(freq='M'))

mon_dict = {i: [] for i in range(1, 13)}
for mon, group in all_q_mon:
    # print(f"Processing month: {mon}")
    group = group.reset_index()
    sim = group.copy().drop(columns=['obs'])
    obs = group[['Date', 'obs']]
    nse_dict = NSE(obs, sim)
    nse_df = dict_to_df(nse_dict, f"{mon.strftime('%Y_%m')}_NSE")
    month_num = mon.month
    mon_dict[month_num].append(nse_df)

    max_nse_idx = nse_df[f"{mon.strftime('%Y_%m')}_NSE"].idxmax()
    max_nse = nse_df.loc[max_nse_idx, f"{mon.strftime('%Y_%m')}_NSE"]
    max_nse_jobid = nse_df.loc[max_nse_idx, 'job_id']
    print(f"Month {mon.strftime('%Y-%m')}: Max NSE = {max_nse:.4f}, JobID = {max_nse_jobid}")


job_id_df = mon_dict[1][0][['job_id']]
mon_avg_ls = []
max_nse_jobid_ls = []
for mon in range(1, 13):
    mon_list = mon_dict[mon]
    mon_list = [res.drop(columns=['job_id']) if 'job_id' in res.columns else res for res in mon_list]
    mon_df = pd.concat(mon_list, axis=1)
    mon_df = pd.concat([job_id_df, mon_df], axis=1)

    print(f"Saving month {mon} results...")
    mon_df = mon_df.set_index('job_id')
    avg_mon_df = mon_df.mean(axis=1)
    avg_mon_df = avg_mon_df.to_frame(name=f"avg_{mon:02d}")
    avg_mon_df = avg_mon_df.reset_index()
    mon_avg_ls.append(avg_mon_df)
    print(avg_mon_df)
    max_nse_idx = avg_mon_df[f"avg_{mon:02d}"].idxmax()
    max_nse = avg_mon_df.loc[max_nse_idx, f"avg_{mon:02d}"]
    max_nse_jobid = avg_mon_df.loc[max_nse_idx, 'job_id']
    print(f"Month {mon:02d}: Max Avg NSE = {max_nse:.4f}, JobID = {max_nse_jobid}")

    max_nse_jobid_ls.append(max_nse_jobid)

best_param = pd.DataFrame()
for mon in range(1, 13):
    mon_best_param = job_params[job_params['job_id'] == max_nse_jobid_ls[mon-1]].iloc[0].to_dict()
    mon_best_param = pd.DataFrame([mon_best_param])
    mon_best_param['month'] = mon
    best_param = pd.concat([best_param, mon_best_param], axis=0)

print(best_param)
best_param.to_csv(f"./Analysis/{work_dir}/{work_dir}_best_params.csv", index=False)
print("Saving all months average results...")
