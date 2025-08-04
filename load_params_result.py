# -*- encoding: utf-8 -*-
'''
@File    :   load_params_result.py
@Create  :   2025-08-03 14:53:12
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
from util.read_obs import load_qobs, div_q
from util.read_sim import load_qsim, batch_load_qsim, read_sta_qsim

work_dir = "Full_PSO_xinzai"

yaml_dir = f"./Analysis/{work_dir}/jobs/"
result_dir = f"./Analysis/{work_dir}/results/"

qsim, job_params = batch_load_qsim(yaml_dir, result_dir)
qsim.to_feather(f"./Analysis/{work_dir}/{work_dir}_results.feather")
job_params.to_feather(f"./Analysis/{work_dir}/{work_dir}_jobs.feather")
print(job_params)
print(qsim.shape)
