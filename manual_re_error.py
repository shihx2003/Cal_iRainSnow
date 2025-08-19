# -*- encoding: utf-8 -*-
'''
@File    :   manual_re_error.py
@Create  :   2025-08-06 12:30:15
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
# -*- encoding: utf-8 -*-
'''
@File    :   manual_cal.py
@Create  :   2025-08-04 12:47:26
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

from core.iRainSnowJob import iRainSnowInitializer
from core.RunningJobs import batch_instantiate, schedule_and_track_jobs
from core.util.jobs import generate_jobs, generate_mon_jobs
from util.draw_pic import plot_streamflow

from core.util.objfun import NSE, dict_to_df, PBias
from util.read_obs import load_qobs, div_q_chunk, div_q
from core.util.params import adjust_mon_lumpara, load_lumpara, write_lumpara, update_lumpara, check_lumpara
from util.read_sim import load_qsim, batch_load_qsim, read_sta_qsim
import os
from datetime import datetime
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GA_Optimizer")

with open("./config/iRainSnow.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

global_config = config["global"]
basin_config = {"name": "xinzai"}


with open(f"./config/basins/manual_cal_{basin_config['name']}.yaml", "r", encoding="utf-8") as f:
    basin_params = yaml.safe_load(f)

job_group = "Manual_xinzai_b32a864e"


yaml_file = f"./jobs/{job_group}.yaml"
with open(yaml_file, "r", encoding="utf-8") as f:
    job_config = yaml.safe_load(f)
basin_name = basin_config["name"]
df_obs = load_qobs(basin_config["name"])
df_obs = div_q(df_obs, '2014-01-01', '2023-12-31')

set_datparams = []
set_lumpara = []
df_ls = []
for job_id in job_config:

    set_datparams.append(job_config[job_id]["datparams"])
    set_lumpara.append(pd.read_csv(job_config[job_id]["params_csv"]))

    df = read_sta_qsim(f"./Run/{basin_config['name']}/{job_id}/Output/StaQSim.txt")
    df = df[['Date', 'Sim_Q']]
    df = df.rename(columns={'Sim_Q': job_id})

    if not df_ls:
        df_ls.append(df)
    else:
        df_ls.append(df[[job_id]])
df_sim = pd.concat(df_ls, axis=1)
df_sim = div_q(df_sim, '2014-01-01', '2023-12-31')
print(df_sim)
plot_streamflow(df_obs, df_sim, job_group)

cal_sim = div_q(df_sim, '2015-01-01', '2020-12-31')
cal_obs = div_q(df_obs, '2015-01-01', '2020-12-31')
val_sim = div_q(df_sim, '2021-01-01', '2023-12-31')
val_obs = div_q(df_obs, '2021-01-01', '2023-12-31')

nse_cal = dict_to_df(NSE(cal_obs, cal_sim), "nse_cal")
nse_val = dict_to_df(NSE(val_obs, val_sim), "nse_val")
pb_cal = dict_to_df(PBias(cal_obs, cal_sim), "pb_cal")
pb_val = dict_to_df(PBias(val_obs, val_sim), "pb_val")

print(nse_cal)
print(nse_val)

print(pb_cal)
print(pb_val)

log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"manual_{basin_config['name']}.log")

print(pd.DataFrame(set_lumpara[0]))
print(pd.DataFrame(set_datparams))

with open(log_file, "a") as f:
    f.write(f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    f.write(f"Job Group: {job_group}\n")
    f.write(f"NSE Calibration:\n{nse_cal}\n")
    f.write(f"NSE Validation:\n{nse_val}\n")
    f.write(f"PBias Calibration:\n{pb_cal}\n")
    f.write(f"PBias Validation:\n{pb_val}\n")
    f.write("-" * 50 + "\n")

    f.write(f"Parameter Sets (Lumpara):\n{pd.DataFrame(set_lumpara[0])}\n")
    f.write(f"Parameter Sets (Datparams):\n{pd.DataFrame(set_datparams)}\n")

input("Press Enter to exit...")