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

from jobs import Heartbeat, SqlBackupJob, RedisBackupJob
from config import BaseConfig, S3Config, SQLConfig, RedisConfig
from uploader import QiniuUploader



def parse_config(config):
  base_config = BaseConfig(config["base_config"])
  qiniu_config = S3Config(config["qiniu_config"])
  sql_config = [ SQLConfig(x) for x in config["sql_config"] ] if "sql_config" in config else None
  redis_config = RedisConfig(config["redis_config"]) if "redis_config" in config else None
  return base_config, sql_config, redis_config, qiniu_config

def run(config):
  jobs = []
  # heartbeat job
  heartbeat = Heartbeat(1)
  jobs.append({"job": heartbeat, "interval": 1})

  base_config, sql_config, redis_config, qiniu_config = parse_config(config)
  qiniu_uploader = QiniuUploader(qiniu_config)
  if sql_config:
    for config in sql_config:
      sql_backup_job = SqlBackupJob(base_config, config, qiniu_uploader)
      jobs.append({"job":sql_backup_job, "interval": config.interval})
  redis_backup_job = RedisBackupJob(base_config, redis_config, qiniu_uploader)
  jobs.append({"job":redis_backup_job, "interval": redis_config.interval})

  for job in jobs:
    interval = job["interval"]
    assert interval > 0
    schedule.every(interval).minutes.do(job['job'].run)

  while 1:
    schedule.run_pending()
    time.sleep(1)