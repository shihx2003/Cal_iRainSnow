# -*- encoding: utf-8 -*-
'''
@File    :   PSO_cal.py
@Create  :   2025-08-02 16:40:30
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

import pyswarms as ps
from deap import base, creator, tools, algorithms
from scipy.optimize import differential_evolution

from core.util.objfun import NSE, dict_to_df
from util.read_obs import load_qobs, div_q
from util.read_sim import load_qsim
from core.iRainSnowJob import iRainSnowInitializer
from core.RunningJobs import batch_instantiate, schedule_and_track_jobs
from core.util.jobs import generate_jobs

# === 配置日志 ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GA_Optimizer")

# === 读取配置文件 ===
with open("./config/iRainSnow.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

global_config = config["global"]
basin_config = {"name": "buhahk"}

param_names = config["parameters_info"]["names"]
print(len(param_names))
param_ranges = config["parameters_info"]["ranges"]
param_bounds = [[param_ranges[name][0] for name in param_names], [param_ranges[name][1] for name in param_names]]
print(len(param_bounds))

print("param_bounds:", param_bounds)
print("param_bounds shape:", np.array(param_bounds).shape)

# === 读取观测数据（不变）===
df_obs = load_qobs(basin_config["name"])
df_obs = div_q(df_obs, '2015-01-01', '2020-12-31')

iters_count = 1
def evaluate_swarm(x):

    global iters_count
    x_df = pd.DataFrame(x, columns=param_names)
    job_group = f"Full_PSO_{basin_config['name']}_{iters_count}"
    jobs = generate_jobs(x_df, job_group)
    set_jobs = batch_instantiate(global_config, basin_config, jobs)
    schedule_and_track_jobs(set_jobs, max_num=12)

    df_sim = load_qsim(f"./jobs/{job_group}.yaml", basin_config["name"])
    df_sim = div_q(df_sim, '2015-01-01', '2020-12-31')
    print(df_obs, df_sim)
    nse_dict = NSE(df_obs, df_sim)
    nse_df = dict_to_df(nse_dict, "nse")

    obj = nse_df["nse"].values * (-1)
    
    iters_count += 1
    return obj


options = {
    'c1': 2.05,
    'c2': 2.05,
    'w': 0.7298
}


optimizer = ps.single.GlobalBestPSO(
    n_particles=20,
    dimensions=len(param_names),
    options=options,
    bounds=param_bounds

)


best_cost, best_pos = optimizer.optimize(evaluate_swarm, iters=100)

print(f"Best parameters: {best_pos}")
print(f"Best NSE: {best_cost}")