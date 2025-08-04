# -*- encoding: utf-8 -*-
'''
@File    :   analysis_re.py
@Create  :   2025-08-04 11:58:15
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

from util.draw_pic import plot_streamflow
from core.util.objfun import NSE, dict_to_df
from core.util.params import adjust_mon_lumpara, load_lumpara, write_lumpara, update_lumpara, check_lumpara
from util.read_obs import load_qobs, div_q_chunk, div_q
from util.read_sim import load_qsim, batch_load_qsim, read_sta_qsim


work_dir = "Full_PSO_buhahk"
# work_dir = "Full_PSO_xinzai"
# work_dir = "Full3_PSO_niuchang"

re = 1

qobs = load_qobs(f"{work_dir.split('_')[-1]}")
qobs_cal = div_q(qobs, '2015-01-01', '2020-12-31')
qobs_eval = div_q(qobs, '2021-01-01', '2023-12-31')

qsim = read_sta_qsim(f"./Analysis/{work_dir}/re_run/{work_dir.split('_')[-1]}_re{re}/Output/StaQSim.txt")
qsim = read_sta_qsim("E:/Working/QingHaiSnow/CalRsim/Analysis/Full_PSO_buhahk/re_run/buhahk_new/Output/StaQSim.txt")
qsim = qsim.rename(columns={'Sim_Q': 'sim'})
qsim = qsim[['Date', 'sim']]
qsim.to_csv('./sim.csv', index=False)

qsim_cal = div_q(qsim, '2015-01-01', '2020-12-31')
qsim_eval = div_q(qsim, '2021-01-01', '2023-12-31')

cal_nse = dict_to_df(NSE(qobs_cal, qsim_cal), 'cal_NSE')
eval_nse = dict_to_df(NSE(qobs_eval, qsim_eval), 'eval_NSE')
print(cal_nse)
print(eval_nse)
qobs_all = div_q(qobs, '2015-01-01', '2023-12-31')
qsim_all = div_q(qsim, '2015-01-01', '2023-12-31')

plot_streamflow(qobs_all, qsim_all)
input("Press Enter to continue...")
