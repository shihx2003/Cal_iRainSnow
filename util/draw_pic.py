# -*- encoding: utf-8 -*-
'''
@File    :   draw_pic.py
@Create  :   2025-08-04 21:21:17
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def plot_streamflow(qobs_df, qsim_df, mark=None, output_dir='./pic/'):
    """
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Set Date as index
    qobs = qobs_df.set_index('Date')['obs']
    qsim = qsim_df.set_index('Date')
    sim_cols = [col for col in qsim.columns if col != 'Date']
    years = qobs.index.year.unique()
    for year in years:
        fig, ax = plt.subplots(figsize=(12, 6))
        qobs_year = qobs[qobs.index.year == year]
        ax.plot(qobs_year.index, qobs_year.values, 'b-', label='Observed', linewidth=2)
        colors = ['r', 'g', 'c', 'm', 'y', 'k']
        for i, col in enumerate(sim_cols):
            color = colors[i % len(colors)]
            qsim_year = qsim[col][qsim.index.year == year]
            ax.plot(qsim_year.index, qsim_year.values, f'{color}--', label=f'{col}', linewidth=1.5)
            common_idx = qobs_year.index.intersection(qsim_year.index)
            if len(common_idx) > 0:
                obs_vals = qobs_year.loc[common_idx].values
                sim_vals = qsim_year.loc[common_idx].values
                nse = 1 - (np.sum((sim_vals - obs_vals) ** 2) / np.sum((obs_vals - np.mean(obs_vals)) ** 2))
                plt.figtext(0.15, 0.02 + i*0.03, f'{col} NSE: {nse:.3f}', fontsize=9, color=color)
        ax.set_title(f'Streamflow Comparison {year}', fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Streamflow (m³/s)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        plt.tight_layout()
        if mark:
            plt.savefig(f'{output_dir}/{mark}_{year}.png', dpi=300)
        else:
            plt.savefig(f'{output_dir}/{year}.png', dpi=300)
        plt.close()

    print(f"Annual streamflow plots saved to {output_dir}")
