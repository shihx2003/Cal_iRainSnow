# -*- encoding: utf-8 -*-
'''
@File    :   iRainSnowJob.py
@Create  :   2025-07-29 11:10:38
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import subprocess
import os
import shutil
import logging

import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.util.params import update_lumpara, check_lumpara
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
        self.set_params = job_config.get('set_params', {})

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
        
        self.exe_path = os.path.join(self.job_dir, 'iRainSnow.exe')
        return self.job_dir

    def inital_params(self):
        logger.info(f"Initializing parameters for {self.basin_name} in {self.job_dir} ...")

        self.lumpara_file = os.path.join(self.job_dir, 'Data', f"Lumpara_{self.basin_name}.txt")
        self.default_lumpara_path = os.path.join(self.ROOT, 'Source', 'params', 'Lumpara_basin.txt')
        update_lumpara(self.default_lumpara_path, self.lumpara_file, self.set_params)

        if not check_lumpara(self.lumpara_file, self.set_params):
            raise ValueError(f"Invalid parameters in {self.lumpara_file}. Please check the parameters.")
        
        logger.info(f"Parameters initialized in {self.lumpara_file}")


    def inital_job(self):
        """
        Initialize the job by copying files and setting parameters.
        """
        try:
            self.copy_files()
            self.inital_params()
        except Exception as e:
            logger.error(f"Error initializing job {self.job_id}: {e}")
            raise RuntimeError(f"Failed to initialize job {self.job_id}: {e}")

    def run_exe(self):
        log_path = os.path.join(self.job_dir, f'iRainSnow_{self.job_id}.log')
        saving_found = False

        try:
            with open(log_path, "w") as log_file:
                process = subprocess.Popen(
                    [self.exe_path],
                    cwd=self.job_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                for line in process.stdout:
                    log_file.write(line)
                    if "Saving results" in line:
                        saving_found = True
                process.wait()

                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, self.exe_path)
                if not saving_found:
                    logger.warning(f"Job {self.job_id} finished without 'Saving results' message.")
                    raise RuntimeError("iRainSnow.exe finished but did not report 'Saving results'.")
                logger.info(f"Job {self.job_id} completed successfully.")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running iRainSnow.exe: {e}")
            raise RuntimeError(f"Failed to run iRainSnow.exe: {e}")

        finally:
            logger.info(f"Finished running iRainSnow.exe for job {self.job_id}")
            return saving_found

    def collect(self, mark=None):
        """
        Collect results from the job directory.
        This method can be extended to collect specific results as needed.
        """
        self.result_file = os.path.join(self.job_dir, 'Output', "StaQSim.txt")
        if not os.path.exists(self.result_file):
            logger.warning(f"Result file {self.result_file} does not exist.")
        else:
            logger.info(f"Results collected from {self.result_file}")
            # copy results to a specific location
            if mark is not None:
                output_path = os.path.join(self.result_dir, self.basin_name, f"StaQSim_{self.job_id}_{mark}.txt")
            else:
                output_path = os.path.join(self.result_dir, self.basin_name, f"StaQSim_{self.job_id}.txt")
                
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(self.result_file, output_path)
            logger.info(f"Copied results to {output_path}")

    def clean(self):
        """
        Clean up the job directory.
        """
        pass

    def run(self):
        self.inital_job()
        return_code = self.run_exe()

        if return_code:
            self.collect()
        else:
            self.collect(mark="error")

