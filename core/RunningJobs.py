# -*- encoding: utf-8 -*-
'''
@File    :   RunningJobs.py
@Create  :   2025-07-29 12:37:16
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.iRainSnowJob import iRainSnowInitializer

logger = logging.getLogger(__name__)

def batch_instantiate(global_config, basin_config, jobs:dict=None):
    """
    jobs: {
        'job_id': 'job1_test_1',
        'set_params': {
            'param1': 'value1',
            'param2': 'value2',
        }
    """
    set_jobs = {}
    if jobs is not None:
        for job_id, config in jobs.items():
            set_jobs[job_id] = iRainSnowInitializer(global_config, basin_config, config)   
    return set_jobs


def schedule_and_track_jobs(set_jobs: dict, max_num: int = 7):
    """
    Schedule and track multiple iRainSnowInitializer jobs concurrently.

    Parameters
    ----------
    set_jobs : dict
        Dictionary of jobs to be scheduled and tracked.
        Format: {'job_id': iRainSnowInitializer instance}
    max_num : int, optional
        Maximum number of concurrent jobs (default: 7)
    """
    job_ids = list(set_jobs.keys())
    waiting_ids = job_ids.copy()
    runned_ids = []
    finished_ids = []
    error_ids = []

    max_workers = min(max_num, len(job_ids))

    def run_wrapper(job_id, job_instance):
        try:
            logger.info(f"Starting job: {job_id}")
            waiting_ids.remove(job_id)

            job_instance.run()

            runned_ids.append(job_id)
            finished_ids.append(job_id)
            
            logger.info(f"Job completed successfully: {job_id}")
            return (job_id, "success")
        except Exception as e:
            error_ids.append(job_id)
            logger.error(f"Job failed: {job_id}, Error: {e}")
            logger.debug(traceback.format_exc())
            return (job_id, "failed", str(e))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_jobid = {
            executor.submit(run_wrapper, job_id, set_jobs[job_id]): job_id
            for job_id in job_ids
        }

        for future in as_completed(future_to_jobid):
            job_id = future_to_jobid[future]
            try:
                result = future.result()
                logger.info(f"[Result] Job {job_id}: {result}")

            except Exception as e:
                logger.exception(f"[Unhandled Exception] Job {job_id} raised: {e}")

    # collect results
    if len(runned_ids) == len(finished_ids) + len(error_ids):
        logger.info(f"All jobs have been processed. Summary:")
    else:
        logger.warning(f"Some jobs were not processed correctly. Summary : Waiting jobs: {waiting_ids}")
    
    for finished_id in finished_ids:
        set_jobs[finished_id].collect()

    for error_id in error_ids:
        set_jobs[error_id].collect(mark="error")

    logger.info(f"All jobs completed. Summary:")
    logger.info(f"Runned jobs: {runned_ids}")
    logger.info(f"Finished jobs: {finished_ids}")
    logger.info(f"Error jobs: {error_ids}")
