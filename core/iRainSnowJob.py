# -*- encoding: utf-8 -*-
'''
@File    :   iRainSnowJob.py
@Create  :   2025-07-29 11:10:38
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib

import os
import yaml
import shutil
import logging
import subprocess
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed
from core.util.params import update_lumpara, check_lumpara, update_mon_lumpara, update_dat_params
from subprocess import CREATE_NEW_CONSOLE

logger = logging.getLogger(__name__)

class iRainSnowInitializer:
    def __init__(self, global_config, basin_config, job_config):
        """
        Initialize the iRainSnow job with global, basin, and job configurations.

        Parameters
        ----------
        global_config : dict
            Global configuration dictionary.
        basin_config : dict
            Basin configuration dictionary.
        job_config : dict
            Job configuration dictionary.
            - job_id: str
                Unique identifier for the job.
            - set_params: dict
                Parameters to set for the job. 
                e.g. new_params = {'K': 1.5, 'CG': 0.999, 'CI': 0.97, 
                                  'CS': 0.75, 'Kech': 0.03, 'KLWL': 5.0}
        """
        self.ROOT = global_config['ROOT']
        self.default_lumpara_path = os.path.join(self.ROOT, 'Source', 'params', 'Lumpara_basin.txt')
        self.result_dir = os.path.join(self.ROOT, 'Results')

        self.basin_name = basin_config['name']
        

        self.src_dir = os.path.join(self.ROOT, 'Source', self.basin_name)
        self.run_dir = os.path.join(self.ROOT, 'Run', self.basin_name)

        self.job_id = job_config['job_id']
        self.set_params = job_config.get('set_params', None)
        self.dat_params = job_config.get('datparams', None)

    def copy_files(self):
        """ 
        """
        self.job_dir = os.path.join(self.run_dir, self.job_id)
        logger.info(f"Copying {self.src_dir} to {self.job_dir} ...")
        if not os.path.exists(self.src_dir):
            raise FileNotFoundError(f"src_dir {self.src_dir} does not exist.")
        i = 0
        while os.path.exists(self.job_dir):
            i += 1
            self.job_dir = os.path.join(self.run_dir, self.job_id) + f"_{i}"
            if i > 5:
                raise RuntimeError(f"Failed to create a new job directory after 5 attempts.")
        os.makedirs(self.job_dir)
        try:
            shutil.copytree(self.src_dir, self.job_dir, dirs_exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Error copying folder: {e}")
        logger.info(f"Copied to {self.job_dir}")
        
        self.exe_path = os.path.join(self.job_dir, 'iRainSnow-QH.exe')
        return self.job_dir

    def set_dat_params(self):
        self.default_dat_path = os.path.join(self.ROOT, 'Source', 'params', 'Configure_basin.dat')
        self.dat_path = os.path.join(self.job_dir, 'Configure.dat')
        if self.dat_params is None:
            logger.warning("No dat parameters provided, skipping dat parameter update.")
            shutil.copy(self.default_dat_path, self.dat_path)
        else:
            update_dat_params(self.default_dat_path, self.dat_params, self.dat_path)

    def inital_params(self):
        self.lumpara_file = os.path.join(self.job_dir, 'Data', f"Lumpara_{self.basin_name}.txt")
        self.default_lumpara_path = os.path.join(self.ROOT, 'Source', 'params', 'Lumpara_basin.txt')

        if  isinstance(self.set_params, dict):
            logger.info(f"Initializing parameters for {self.basin_name} in {self.job_dir} ...")
            update_lumpara(self.default_lumpara_path, self.lumpara_file, self.set_params)

            if not check_lumpara(self.lumpara_file, self.set_params):
                raise ValueError(f"Invalid parameters in {self.lumpara_file}. Please check the parameters.")
            
            logger.info(f"Parameters initialized in {self.lumpara_file}")
        elif isinstance(self.set_params, pd.DataFrame):
            update_mon_lumpara(self.default_lumpara_path, self.lumpara_file, self.set_params, params_names=['K', 'CG', 'CI', 'CS', 'Kech', 'KLWL'])

        else:
            logger.error("set_params must be a dictionary or a DataFrame.")
            raise TypeError("set_params must be a dictionary or a DataFrame.")
        
    def inital_job(self):
        """
        Initialize the job by copying files and setting parameters.
        """
        try:
            self.copy_files()
            self.set_dat_params()
            self.inital_params()
        except Exception as e:
            logger.error(f"Error initializing job {self.job_id}: {e}")
            raise RuntimeError(f"Failed to initialize job {self.job_id}: {e}")

    def run_exe(self):
        log_path = os.path.join(self.job_dir, f'iRainSnow_{self.job_id}.log')
        saving_found = False

        try:
            # Import the necessary constant for creating a new console window
            
            logger.info(f"Running iRainSnow.exe in visible console window for job {self.job_id}...")
            
            # Run in visible console window
            process = subprocess.Popen(
                [self.exe_path],
                cwd=self.job_dir,
                creationflags=CREATE_NEW_CONSOLE,
                shell=True
            )
            
            # Wait for process to complete
            process.wait()
            
            # Check return code
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, self.exe_path)
            
            # Check for success by looking for output files
            output_file = os.path.join(self.job_dir, 'Output', "StaQSim.txt")
            if os.path.exists(output_file):
                saving_found = True
                logger.info(f"Job {self.job_id} completed successfully.")
            else:
                logger.warning(f"Job {self.job_id} finished but output file not found.")
                raise RuntimeError("iRainSnow.exe finished but did not create expected output files.")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running iRainSnow.exe: {e}")
            raise RuntimeError(f"Failed to run iRainSnow.exe: {e}")

        finally:
            logger.info(f"Finished running iRainSnow.exe for job {self.job_id}")
            saving_found = True
            return saving_found

    def collect(self, mark=None):
        """
        Collect results from the job directory.
        This method can be extended to collect specific results as needed.
        """
        self.result_file = os.path.join(self.job_dir, 'Output', "StaQSim.txt")
        if not os.path.exists(self.result_file):
            logger.warning(f"Result file {self.result_file} does not exist.")
            self.result_file = os.path.join(self.ROOT, 'Source', "def_result", f"StaQSim_def_{self.basin_name}.txt")

            output_path_mark = os.path.join(self.result_dir, self.basin_name, f"StaQSim_{self.job_id}_loss.txt")
            output_path = os.path.join(self.result_dir, self.basin_name, f"StaQSim_{self.job_id}.txt")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(self.result_file, output_path)
            os.makedirs(os.path.dirname(output_path_mark), exist_ok=True)
            shutil.copy(self.result_file, output_path_mark)
        else:
            logger.info(f"Results collected from {self.result_file}")
            # copy results to a specific location
            if mark is not None:
                output_path_mark = os.path.join(self.result_dir, self.basin_name, f"StaQSim_{self.job_id}_{mark}.txt")
                output_path = os.path.join(self.result_dir, self.basin_name, f"StaQSim_{self.job_id}.txt")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.copy(self.result_file, output_path)
                os.makedirs(os.path.dirname(output_path_mark), exist_ok=True)
                shutil.copy(self.result_file, output_path_mark)
            else:
                output_path = os.path.join(self.result_dir, self.basin_name, f"StaQSim_{self.job_id}.txt")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.copy(self.result_file, output_path)

            logger.info(f"Copied results to {output_path}")

    def cleanup(self):

        logger.info(f"Cleaning job directory {self.job_dir}...")

        # 要保留的文件路径
        keep_files = {
            os.path.join(self.job_dir, 'Output', 'StaQSim.txt'),
            os.path.join(self.job_dir, 'Data', f"Lumpara_{self.basin_name}.txt"),
            os.path.join(self.job_dir, 'Configure.dat')
        }
    
        for path in keep_files:
            if not os.path.exists(path):
                logger.warning(f"File to preserve does not exist: {path}")

        for root, dirs, files in os.walk(self.job_dir, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in keep_files:
                    try:
                        os.remove(file_path)
                        logger.debug(f"Deleted file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove file {file_path}: {e}")
            keep_dirs = {self.job_dir,
                        os.path.join(self.job_dir, 'Data'),
                        os.path.join(self.job_dir, 'Output')}
            if root not in keep_dirs:
                try:
                    shutil.rmtree(root)
                    logger.debug(f"Deleted directory: {root}")
                except Exception as e:
                    logger.error(f"Failed to remove directory {root}: {e}")

        logger.info("Job directory cleaned successfully.")

    def run(self):
        self.inital_job()
        return_code = self.run_exe()

        if return_code:
            self.collect()
            # self.cleanup()
        else:
            self.collect(mark="error")

