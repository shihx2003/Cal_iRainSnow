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
from util.draw_pic import plot_streamflow, draw_tpso, draw_heat_nsepb

from core.util.objfun import NSE, dict_to_df, PBias
from util.read_obs import load_qobs, div_q_chunk, div_q, load_pretem
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

os.makedirs(f"./pic/{basin_config['name']}", exist_ok=True)
png_files = [f for f in os.listdir(f"./pic") if f.endswith(".png") 
             and os.path.isfile(os.path.join(f"./pic", f))]
for png_file in png_files:
    src_path = os.path.join(f"./pic", png_file)
    dst_path = os.path.join(f"./pic/{basin_config['name']}", png_file)
    shutil.move(src_path, dst_path)

print(f"Moved {len(png_files)} PNG files to ./pic/{basin_config['name']}")

with open(f"./config/basins/manual_cal_{basin_config['name']}.yaml", "r", encoding="utf-8") as f:
    basin_params = yaml.safe_load(f)

###################                                                 test mon
###################   1      2      3      4      5      6      7      8      9     10     11      12
lumpara = {'CG':   [0.996, 0.996, 0.996, 0.996, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.996, 0.996], 
           'CI':   [0.96,  0.92,  0.92,  0.92,  0.92,  0.92,  0.95,  0.95,  0.95,  0.95,  0.98,  0.98 ],        # 降低延缓退水，基流变大
           'CS':   [0.99,  0.99,  0.99,  0.99,  0.100, 0.010, 0.010, 0.010, 0.50,  0.10,  0.10,  0.40 ],        # 调大CS则基流变大
           'K':    [1.0,   0.3,   0.3,   0.3,   0.3,   2.2,   2.4,   2.8,   1.6,   0.8,   0.4,   1.2  ],        # 通过增大雪量，然后增加融雪速度？
           'KLWL': [5.0,   8.0,   8.0,   8.0,   8.5,   3.0,   0.5,   5.0,   4.0,   8.0,   9.0,   5.0  ],        # 雪融化的速度，化完就没了，雪量很少
           'Kech': [0.3,   0.2,   0.01,  0.001, 0.001, 0.001, 0.001, 0.001, 0.04,  0.01,  0.3,   0.3  ]}
###################   0      1      2      3      4      5      6      7      8      9     10     11 

###################   1      2      3      4      5      6      7      8      9     10     11      12
lumparb = {'CG':   [0.996, 0.996, 0.996, 0.996, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.996, 0.996], 
           'CI':   [0.96,  0.92,  0.92,  0.92,  0.92,  0.92,  0.95,  0.95,  0.95,  0.95,  0.98,  0.98 ],        # 降低延缓退水，基流变大
           'CS':   [0.99,  0.99,  0.99,  0.99,  0.100, 0.010, 0.010, 0.010, 0.50,  0.10,  0.10,  0.40 ],        # 调大CS则基流变大
           'K':    [1.0,   0.3,   0.3,   0.3,   0.3,   2.2,   2.4,   2.8,   1.6,   0.8,   0.4,   1.2  ],        # 通过增大雪量，然后增加融雪速度？
           'KLWL': [5.0,   8.0,   8.0,   8.0,   8.5,   3.0,   0.5,   5.0,   4.0,   8.0,   9.0,   5.0  ],        # 雪融化的速度，化完就没了，雪量很少
           'Kech': [0.3,   0.2,   0.01,  0.001, 0.001, 0.001, 0.001, 0.001, 0.04,  0.01,  0.3,   0.3  ]}
###################   0      1      2      3      4      5      6      7      8      9     10     11 

###################   1      2      3      4      5      6      7      8      9     10     11      12
lumparc = {'CG':   [0.996, 0.996, 0.996, 0.996, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.996, 0.996], 
           'CI':   [0.96,  0.92,  0.92,  0.92,  0.92,  0.92,  0.95,  0.95,  0.95,  0.95,  0.98,  0.98 ],        # 降低延缓退水，基流变大
           'CS':   [0.99,  0.99,  0.99,  0.99,  0.100, 0.010, 0.010, 0.010, 0.50,  0.10,  0.10,  0.40 ],        # 调大CS则基流变大
           'K':    [1.0,   0.3,   0.3,   0.3,   0.3,   2.2,   2.4,   2.8,   1.6,   0.8,   0.4,   1.2  ],        # 通过增大雪量，然后增加融雪速度？
           'KLWL': [5.0,   8.0,   8.0,   8.0,   8.5,   3.0,   0.5,   5.0,   4.0,   8.0,   9.0,   5.0  ],        # 雪融化的速度，化完就没了，雪量很少
           'Kech': [0.3,   0.2,   0.01,  0.001, 0.001, 0.001, 0.001, 0.001, 0.04,  0.01,  0.3,   0.3  ]}
###################   0      1      2      3      4      5      6      7      8      9     10     11 

###################   1      2      3      4      5      6      7      8      9     10     11      12
lumpard = {'CG':   [0.996, 0.996, 0.996, 0.996, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.996, 0.996], 
           'CI':   [0.96,  0.92,  0.92,  0.92,  0.92,  0.92,  0.95,  0.95,  0.95,  0.95,  0.98,  0.98 ],        # 降低延缓退水，基流变大
           'CS':   [0.99,  0.99,  0.99,  0.99,  0.100, 0.010, 0.010, 0.010, 0.50,  0.10,  0.10,  0.40 ],        # 调大CS则基流变大
           'K':    [1.0,   0.3,   0.3,   0.3,   0.3,   2.2,   2.4,   2.8,   1.6,   0.8,   0.4,   1.2  ],        # 通过增大雪量，然后增加融雪速度？
           'KLWL': [5.0,   8.0,   8.0,   8.0,   8.5,   3.0,   0.5,   5.0,   4.0,   8.0,   9.0,   5.0  ],        # 雪融化的速度，化完就没了，雪量很少
           'Kech': [0.3,   0.2,   0.01,  0.001, 0.001, 0.001, 0.001, 0.001, 0.04,  0.01,  0.3,   0.3  ]}
###################   0      1      2      3      4      5      6      7      8      9     10     11 
datparams = {
        'scf'                : 1.0,
        'snow_melting_coef'  : 1.0,
        'free_water_coef'    : 1.0,         # SM
        'tension_water_coef' : 0.85,        # WM
    }
set_lumpara = [pd.DataFrame(lumpara), pd.DataFrame(lumparb), pd.DataFrame(lumparc), pd.DataFrame(lumpard)]
# set_lumpara = [pd.DataFrame(lumpara)]
set_datparams = [datparams]

# for i in [0.5]:
#     param_modified = lumpara.copy()
#     print(param_modified['CI'])
#     for j in range(-5, 0):
#         param_modified['CI'][j] = i * param_modified['CI'][j]
#     print(param_modified['CI'])

#     param_modified = pd.DataFrame(param_modified)
#     set_lumpara.append(param_modified)

# for i in [0.8,0.85,0.90,0.95,1.05,1.10,1.15,1.20]:
#     # datparams_modified = datparams.copy()
#     # datparams_modified['tension_water_coef'] = i 
#     # set_datparams.append(datparams_modified)
#     param_modified = lumpara.copy()
#     param_modified['CI'] = [i * k for k in param_modified['CI']]
#     set_lumpara.append(pd.DataFrame(param_modified))

if len(set_lumpara) == 1:
    setmethod = 'datparams'  # Only datparams available
else:
    setmethod = 'lumpara'

print(f"Total {len(set_lumpara) + len(set_datparams) - 1} parameter sets for manual calibration.")

df_obs = load_qobs(basin_config["name"])
df_obs = div_q(df_obs, '2014-01-01', '2023-12-31')
job_group = f"Manual_{basin_config['name']}_{uuid4().hex[:8]}"

jobs = generate_mon_jobs(set_lumpara, set_datparams, job_group, setmethod=setmethod)
set_jobs = batch_instantiate(global_config, basin_config, jobs)
schedule_and_track_jobs(set_jobs, max_num=12)

df_sim = load_qsim(f"./jobs/{job_group}.yaml", basin_config["name"])
df_sim = div_q(df_sim, '2014-01-01', '2023-12-31')


pre, tem = load_pretem(basin_config['name'])
pre = div_q(pre, '2014-01-01', '2023-12-31')
tem = div_q(tem, '2014-01-01', '2023-12-31')
draw_heat_nsepb(df_sim, df_obs, mark=job_group)
draw_tpso(df_sim, df_obs, pre, tem, mark=job_group)

# plot_streamflow(df_obs, df_sim, job_group)
df_sim = df_sim[[col for col in df_sim.columns if not col.endswith('_SL')]]
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