# -*- coding:utf-8 -*-
#  ________________________________________
# / Programmers used to batch environments \
# | may find it hard to live without giant |
# | listings; we would find it hard to use |
# | them.                                  |
# |                                        |
# \ -- D.M. Ritchie                        /
#  ----------------------------------------
#         \   ^__^
#          \  (oo)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||

import functools
import time

import schedule

from main import logger
from jobs import Heartbeat, SqlBackupJob, RedisBackupJob, MongoBackupJob
from config import BaseConfig, S3Config, SQLConfig, RedisConfig, MongoConfig
from uploader import QiniuUploader, S3Uploader


def parse_config(config):
  base_config = BaseConfig(config["base_config"])
  qiniu_config = S3Config(config["qiniu_config"])
  sql_config = [ SQLConfig(x) for x in config["sql_config"] ] if "sql_config" in config else None
  redis_config = RedisConfig(config["redis_config"]) if "redis_config" in config else None
  mongo_config =[ MongoConfig(x) for x in config['mongo_config']] if "mongo_config" in config else None
  return base_config, sql_config, redis_config, qiniu_config, mongo_config

def run(config, immediate=False):
  jobs = []
  # heartbeat job
  heartbeat = Heartbeat(1)
  jobs.append({"job": heartbeat, "interval": 1, "interval_unit": "minute"})

  base_config, sql_config, redis_config, qiniu_config, mongo_config = parse_config(config)
  qiniu_uploader = QiniuUploader(qiniu_config) if not qiniu_config.is_s3 else S3Uploader(qiniu_config)
  if sql_config:
    for config in sql_config:
      sql_backup_job = SqlBackupJob(base_config, config, qiniu_uploader)
      jobs.append({
          "job":sql_backup_job, 
          "interval": config.interval,
          "interval_unit": config.interval_unit
        })
  if redis_config:
    redis_backup_job = RedisBackupJob(base_config, redis_config, qiniu_uploader)
    jobs.append({
        "job":redis_backup_job, 
        "interval": redis_config.interval,
        "interval_unit": redis_config.interval_unit
      })
  if mongo_config:
    for config in mongo_config:
      mongo_backup_job = MongoBackupJob(base_config,config, qiniu_uploader)
      jobs.append({
          "job":mongo_backup_job, 
          "interval": config.interval,
          "interval_unit": config.interval_unit
        })

  for job in jobs:
    interval = job["interval"]
    interval_unit = job['interval_unit']
    assert interval > 0
    assert interval_unit in ['second', 'minute', 'hour']
    # One-off; run immediately for every job
    if immediate:
      logger.info("Running {} jobs immediately".format(len(jobs)))
      for job in jobs:
        job["job"].run()
        time.sleep(1)
      logger.info("Finished all jobs")
      return
    else:
      if interval_unit == 'second':
        schedule.every(interval).seconds.do(job['job'].run)
      elif interval_unit == 'minute':
        schedule.every(interval).minutes.do(job['job'].run)
      elif interval_unit == 'hour':
        schedule.every(interval).hours.do(job['job'].run)
      logger.info("Scheduled all jobs!!!")

  while 1:
    schedule.run_pending()
    time.sleep(1)
