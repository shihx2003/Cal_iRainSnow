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
import seaborn as sns


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
    sim_cols = [col for col in qsim.columns if (col != 'Date' and not col.endswith('_SL'))]
    print(sim_cols)
    sim_SL_cols = [col for col in sim_cols if (col != 'Date' and col.endswith('_SL'))]
    years = qobs.index.year.unique()
    for year in years:
        fig, ax = plt.subplots(figsize=(12, 6))
        qobs_year = qobs[qobs.index.year == year]
        ax.plot(qobs_year.index, qobs_year.values, alpha=0.8, color='black', linestyle='-', label='Observed', linewidth=1)

        ax2 = ax.twinx()
        ax2.spines['right'].set_position(('outward', 60))
        ax3 = ax.twinx()
        pre_year = pre[pre.index.year == year]
        tem_year = tem[tem.index.year == year]

        ax2.bar(pre_year.index, pre_year.values, alpha=0.15, color='blue', width=1.0, label='Precipitation')
        ax3.plot(tem_year.index, tem_year.values, alpha=0.15, color='green', linewidth=1.5, label='Temperature')

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
            qsim_year_SL = qsim[f'{col}_SL'][qsim.index.year == year]

            ax.plot(qsim_year.index, qsim_year.values, f'{color}', linestyle='--', label=f'{col}', linewidth=1.2)
            ax.plot(qsim_year_SL.index, qsim_year_SL.values, f'{color}', linestyle='-', linewidth=1)

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

def cal_heat_nsepb(qsim_df, qobs_df, mark=None):
    qobs = qobs_df.set_index('Date')['obs']
    qsim = qsim_df.set_index('Date')
    sim_cols = [col for col in qsim.columns if (col != 'Date' and not col.endswith('_SL'))]

    nse_values = []
    pb_values = []
    years = qobs.index.year.unique()

    for col in sim_cols:
        qsim_col = qsim[col]
        nse_col = []
        pb_col = []

        for year in years:

            sim_col_year = qsim_col[qsim_col.index.year == year]
            obs_col_year = qobs[qobs.index.year == year]

            nse_col_year = []
            pb_col_year = []

            for month in range(1, 13):
                sim_col_year_month = sim_col_year[sim_col_year.index.month == month]
                obs_col_year_month = obs_col_year[obs_col_year.index.month == month]
                common_idx = sim_col_year_month.index.intersection(obs_col_year_month.index)
                if len(common_idx) > 0:
                    obs_vals = obs_col_year_month.loc[common_idx].values
                    sim_vals = sim_col_year_month.loc[common_idx].values
                    nse = 1 - (np.sum((sim_vals - obs_vals) ** 2) / np.sum((obs_vals - np.mean(obs_vals)) ** 2))
                    pb = (np.sum(sim_vals) - np.sum(obs_vals)) / np.sum(obs_vals) * 100
                else:
                    nse = np.nan
                    pb = np.nan
                
                nse_col_year.append(nse)
                pb_col_year.append(pb)
            nse_col.append(nse_col_year)
            pb_col.append(pb_col_year)
            
        nse_values.append(nse_col)
        pb_values.append(pb_col)

    nse_values = np.array(nse_values)
    pb_values = np.array(pb_values)

    nse_avg = []
    pb_avg = []
    for col in sim_cols:
        qsim_col = qsim[col]
        nse_avg_month = []
        pb_avg_month = []
        for month in range(1, 13):
            sim_col_month = qsim_col[qsim_col.index.month == month]
            obs_month = qobs[qobs.index.month == month]
            sim_vals = sim_col_month.values
            obs_vals = obs_month.values

            nse = 1 - (np.sum((sim_vals - obs_vals) ** 2) / np.sum((obs_vals - np.mean(obs_vals)) ** 2))
            pb = (np.sum(sim_vals) - np.sum(obs_vals)) / np.sum(obs_vals) * 100

            nse_avg_month.append(nse)
            pb_avg_month.append(pb)

        nse_avg.append(nse_avg_month)
        pb_avg.append(pb_avg_month)

    nse_avg = np.array(nse_avg)
    pb_avg = np.array(pb_avg)

    return nse_values, pb_values, nse_avg, pb_avg

def draw_heat_nsepb(qsim_df, qobs_df, mark=None):
    nse_values, pb_values, nse_avg, pb_avg  = cal_heat_nsepb(qsim_df, qobs_df, mark=mark)
    
    # Get simulation column names
    sim_cols = [col for col in qsim_df.columns if (col != 'Date' and not col.endswith('_SL'))]
    years = qobs_df.set_index('Date')['obs'].index.year.unique()
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    
    # Create heatmaps for each simulation column
    for i, col in enumerate(sim_cols):
        # Create a figure with two subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # NSE heatmap
        sns.heatmap(nse_values[i], annot=True, cmap='RdYlGn', vmin=-1, vmax=1, 
                   xticklabels=months, yticklabels=years, fmt='.2f', ax=ax1)
        ax1.set_title(f'NSE for {col}')
        ax1.set_ylabel('Year')
        ax1.set_xlabel('Month')
        
        # PB heatmap
        sns.heatmap(pb_values[i], annot=True, cmap='coolwarm', vmin=-100, vmax=100, 
                   xticklabels=months, yticklabels=years, fmt='.1f', ax=ax2)
        ax2.set_title(f'Percent Bias (PB) for {col}')
        ax2.set_ylabel('Year')
        ax2.set_xlabel('Month')
        
        # Main title for the figure
        plt.suptitle(f'Performance Metrics for {col}', fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout with space for suptitle
        # Add grid to both heatmaps        

        # Make grid appear on top of heatmap
        ax1.set_axisbelow(False)
        ax2.set_axisbelow(False)
        # Calculate overall NSE for this column
        overall_qsim = qsim_df.set_index('Date')[col]
        overall_qobs = qobs_df.set_index('Date')['obs']
        common_idx = overall_qsim.index.intersection(overall_qobs.index)
        
        if len(common_idx) > 0:
            obs_vals = overall_qobs.loc[common_idx].values
            sim_vals = overall_qsim.loc[common_idx].values
            overall_nse = 1 - (np.sum((sim_vals - obs_vals) ** 2) / np.sum((obs_vals - np.mean(obs_vals)) ** 2))
            overall_pb = (np.sum(sim_vals) - np.sum(obs_vals)) / np.sum(obs_vals) * 100
            
            # Calculate calibration period metrics (2015-2020)
            cal_idx = [idx for idx in common_idx if '2015-01-01' <= str(idx) <= '2020-12-31']
            if len(cal_idx) > 0:
                cal_obs_vals = overall_qobs.loc[cal_idx].values
                cal_sim_vals = overall_qsim.loc[cal_idx].values
                cal_nse = 1 - (np.sum((cal_sim_vals - cal_obs_vals) ** 2) / np.sum((cal_obs_vals - np.mean(cal_obs_vals)) ** 2))
                cal_pb = (np.sum(cal_sim_vals) - np.sum(cal_obs_vals)) / np.sum(cal_obs_vals) * 100
            else:
                cal_nse = cal_pb = float('nan')
                
            # Calculate validation period metrics (2021-2023)
            val_idx = [idx for idx in common_idx if '2021-01-01' <= str(idx) <= '2023-12-31']
            if len(val_idx) > 0:
                val_obs_vals = overall_qobs.loc[val_idx].values
                val_sim_vals = overall_qsim.loc[val_idx].values
                val_nse = 1 - (np.sum((val_sim_vals - val_obs_vals) ** 2) / np.sum((val_obs_vals - np.mean(val_obs_vals)) ** 2))
                val_pb = (np.sum(val_sim_vals) - np.sum(val_obs_vals)) / np.sum(val_obs_vals) * 100
            else:
                val_nse = val_pb = float('nan')
            
            # Add text annotation for overall, calibration and validation metrics
            fig.text(0.5, 0.03, f'Overall NSE: {overall_nse:.3f}   Overall PB: {overall_pb:.2f}%', 
            ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
            fig.text(0.25, 0.01, f'Calibration (2015-2020) NSE: {cal_nse:.3f}   PB: {cal_pb:.2f}%', 
            ha='center', fontsize=10, bbox=dict(facecolor='lightyellow', alpha=0.8))
            fig.text(0.75, 0.01, f'Validation (2021-2023) NSE: {val_nse:.3f}   PB: {val_pb:.2f}%', 
            ha='center', fontsize=10, bbox=dict(facecolor='lightblue', alpha=0.8))
        # Save the figure
        if mark:
            plt.savefig(f'./pic/{col}_heat.png', dpi=300)
        else:
            plt.savefig(f'./pic/{col}_heat.png', dpi=300)
        plt.close()
    
    print(f"Combined NSE and PB heatmaps saved to ./pic/")

    # Plot the average NSE and PB across all months for each simulation model
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    sim_cols_short = [col[-4:] for col in sim_cols]
    # NSE heatmap for job average
    sns.heatmap(nse_avg, annot=True, cmap='RdYlGn', vmin=-1, vmax=1, 
               xticklabels=months, yticklabels=sim_cols_short, fmt='.2f', ax=ax1)
    ax1.set_title('Average NSE by Month')
    ax1.set_ylabel('Simulation Model')
    ax1.set_xlabel('Month')
    
    # PB heatmap for job average
    sns.heatmap(pb_avg, annot=True, cmap='coolwarm', vmin=-50, vmax=50, 
               xticklabels=months, yticklabels=sim_cols_short, fmt='.1f', ax=ax2)
    ax2.set_title('Average Percent Bias (PB) by Month')
    ax2.set_ylabel('Simulation Model')
    ax2.set_xlabel('Month')
    
    # Main title for the figure
    plt.suptitle('Average Performance Metrics Across Models', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Save the figure
    if mark:
        plt.savefig(f'./pic/{mark}_avg.png', dpi=300)
    else:
        plt.savefig(f'./pic/avg.png', dpi=300)
    plt.close()
    
    print("Average metrics heatmap saved to ./pic/")
