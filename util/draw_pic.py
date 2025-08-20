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
                pb = (np.sum(sim_vals) - np.sum(obs_vals)) / np.sum(obs_vals) * 100
                plt.figtext(0.15, 0.02 + i*0.03, f'{col} NSE: {nse:.3f}', fontsize=9, color=color)
                plt.figtext(0.65, 0.02 + i*0.03, f'{col} PB: {pb:.2f}%', fontsize=9, color=color)
        ax.set_title(f'Streamflow Comparison {year}', fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Streamflow (m³/s)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))  # Change '%b' to '%m' for numerical months
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        plt.tight_layout()
        if mark:
            plt.savefig(f'{output_dir}/{mark}_{year}.png', dpi=300)
        else:
            plt.savefig(f'{output_dir}/{year}.png', dpi=300)
        plt.close()

    print(f"Annual streamflow plots saved to {output_dir}")


def draw_tpso(qsim_df, qobs_df, pre_df, tem_df, mark=None, output_dir='./pic/'):
    """
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Set Date as index
    qobs = qobs_df.set_index('Date')['obs']
    pre = pre_df.set_index('Date')['pre']
    tem = tem_df.set_index('Date')['tem']
    qsim = qsim_df.set_index('Date')
    sim_cols = [col for col in qsim.columns if col != 'Date']
    years = qobs.index.year.unique()
    for year in years:
        fig, ax = plt.subplots(figsize=(12, 6))
        qobs_year = qobs[qobs.index.year == year]
        ax.plot(qobs_year.index, qobs_year.values, 'b-', label='Observed', linewidth=2)

        ax2 = ax.twinx()
        ax2.spines['right'].set_position(('outward', 60))
        ax3 = ax.twinx()
        pre_year = pre[pre.index.year == year]
        tem_year = tem[tem.index.year == year]

        ax2.bar(pre_year.index, pre_year.values, alpha=0.4, color='blue', width=1.0, label='Precipitation')
        ax3.plot(tem_year.index, tem_year.values, alpha=0.8, color='green', linewidth=1.5, label='Temperature')

        ax3.axhline(y=0, color='green', linestyle='--', alpha=0.8, label='0°C')

        colors = ['red', 'orange', 'green', 'cyan', 'magenta', 'yellow', 'black', 'purple', 'brown', 
             'pink', 'gray', 'olive', 'navy', 'teal', 'coral', 'crimson', 
             'gold', 'indigo', 'lime', 'maroon', 'sienna', 'turquoise',
             'darkred', 'darkorange', 'darkgreen', 'darkblue', 'darkviolet',
             'mediumseagreen', 'steelblue', 'tomato', 'chocolate', 'peru',
             'mediumorchid', 'dodgerblue', 'firebrick', 'forestgreen', 'goldenrod']
        for i, col in enumerate(sim_cols):
            color = colors[i % len(colors)]
            qsim_year = qsim[col][qsim.index.year == year]
            ax.plot(qsim_year.index, qsim_year.values, f'{color}', linestyle='--', label=f'{col}', linewidth=1.5)
            common_idx = qobs_year.index.intersection(qsim_year.index)
            if len(common_idx) > 0:
                obs_vals = qobs_year.loc[common_idx].values
                sim_vals = qsim_year.loc[common_idx].values
                nse = 1 - (np.sum((sim_vals - obs_vals) ** 2) / np.sum((obs_vals - np.mean(obs_vals)) ** 2))
                pb = (np.sum(sim_vals) - np.sum(obs_vals)) / np.sum(obs_vals) * 100
                plt.figtext(0.15, 0.02 + i*0.03, f'{col} NSE: {nse:.3f}', fontsize=9, color=color)
                plt.figtext(0.65, 0.02 + i*0.03, f'{col} PB: {pb:.2f}%', fontsize=9, color=color)

        ax.set_title(f'Streamflow Comparison {year}', fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Streamflow (m³/s)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))  # Change '%b' to '%m' for numerical months
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        ax2.set_ylabel('Precipitation (mm)', color='blue', fontsize=12)
        ax2.tick_params(axis='y', colors='blue')
        ax3.set_ylabel('Temperature (°C)', color='green', fontsize=12)
        ax3.tick_params(axis='y', colors='green')
        # ax2.invert_yaxis()

        # Create a combined legend for all axes
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines3, labels3 = ax3.get_legend_handles_labels()
        
        ax.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, 
              loc='upper right', bbox_to_anchor=(1.0, 1.0),
              ncol=1, frameon=True)
        plt.tight_layout()

        if mark:
            plt.savefig(f'{output_dir}/{mark}_{year}.png', dpi=300)
        else:
            plt.savefig(f'{output_dir}/{year}.png', dpi=300)
        plt.close()

    print(f"Annual streamflow plots saved to {output_dir}")