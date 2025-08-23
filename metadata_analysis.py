# -*- encoding: utf-8 -*-
'''
@File    :   metadata_analysis.py
@Create  :   2025-08-19 15:26:45
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import yaml
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from util.draw_pic import plot_streamflow, draw_tpso
from util.read_obs import load_qobs, load_pretem, div_q
from util.read_sim import load_qsim, read_sta_qsim

basin = 'xinzai'
pre, tem = load_pretem(basin)
qobs = load_qobs(basin)

qsim = read_sta_qsim(f"E:/Working/QingHaiSnow/CalRsim/Finial/Manual_{basin}/Output/StaQSim.txt")
qsim = qsim.rename(columns={'Sim_Q': 'sim'})
qsim = qsim[['Date', 'sim']]

pre = div_q(pre, '2015-01-01', '2023-12-31')
tem = div_q(tem, '2015-01-01', '2023-12-31')
qobs = div_q(qobs, '2015-01-01', '2023-12-31')
qsim = div_q(qsim, '2015-01-01', '2023-12-31')

draw_tpso(qsim, qobs, pre, tem, mark=basin)
