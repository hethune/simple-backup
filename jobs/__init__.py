# -*- coding:utf-8 -*-

#  ________________________________________
# / The way to love anything is to realize \
# \ that it might be lost.                 /
#  ----------------------------------------
#         \   ^__^
#          \  (OO)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||

import delegator
import datetime
import os

from helper import with_logging
from main import logger

class BackupJob(object):
  """
  base class for backup jobs
  real jobs should extend this class
  """
  def __init__(self):
    pass

  def run(self):
    pass

  @staticmethod
  def safe_delete(file_path):
    if os.path.isfile(file_path):
      os.remove(file_path)
      logger.info("deleted file {}".format(file_path))

  @staticmethod
  def construct_filename(prefix, tags, suffix, base_folder,dt=None):
    """
    tags: @list
    dt: datetime object
    return: prefix-tags-tags-tags-yyyymmdd-epoch.suffix
    """
    now = datetime.datetime.utcnow()
    if not dt:
      year, month, day = now.year,now.month,now.day
    else:
      year, month, day = dt.year,dt.month,dt.day

    epoch = int(now.strftime('%s'))
    # prefix-database-yyyymmdd-epoch
    tmp_file_name = "{}-{}-{}-{}.{}".format(
        prefix, 
        "-".join(tags),
        "{}{}{}".format(year,month,day),
        epoch,
        suffix
      )

    tmp_file_name_with_path = "{}/{}".format(base_folder, tmp_file_name)

    return tmp_file_name, tmp_file_name_with_path

  @staticmethod
  def construct_dt(dateiso):
    # date iso string like 2018-01-01
    return datetime.datetime(int(dateiso.split("-")[0]),
                            int(dateiso.split("-")[1]),
                            int(dateiso.split("-")[2])
                            )

  @staticmethod
  def date_range(start_date, end_date):
    for ordinal in range(start_date.toordinal(), end_date.toordinal()):
        yield datetime.date.fromordinal(ordinal)

class Heartbeat(BackupJob):
  """
  Heartbeat
  """
  def __init__(self, n):
    self.counter = 0
    self.internal = n

  def run(self):
    self.counter += 1
    logger.info("Heartbeat for every {} seconds. Total time is {}".format(self.internal, self.counter))

class SqlBackupJob(BackupJob):
  """
  Back up a mysql database
  """

  def __init__(self, base_config, sql_config, uploader):
    self.base_config = base_config
    self.sql_config = sql_config
    self.uploader = uploader

  @with_logging
  def run(self):
    tmp_file_name, tmp_file_name_with_path = BackupJob.construct_filename(
        self.sql_config.prefix,
        # need an array
        [self.sql_config.database],
        self.sql_config.suffix,
        self.base_config.tmp_folder
      )

    try:
      # dump sql to file
      # mysqldump -h xxx -d xxx -u root | gzip --best | openssl des -salt -k xxxxxx
      sql_dump_command = "mysqldump -h{} -u{} -p{} {}".format(
          self.sql_config.host, 
          self.sql_config.username,
          self.sql_config.password,
          self.sql_config.database
        ) if self.sql_config.password else "mysqldump -h {} -u {}".format(
          self.sql_config.host, 
          self.sql_config.username,
          self.sql_config.database
        )

      command = "{} | gzip --best | openssl des -salt -k {} > {}".format(
        sql_dump_command,
        self.base_config.passphrase,
        tmp_file_name_with_path
      )

      logger.debug("running {}".format(command))
      c = delegator.run(command)

      logger.warning("dumped back up file {}".format(tmp_file_name))

      if c.return_code != 0:
        raise RuntimeError(c.std_err)

      # upload if not dry_run
      if not self.base_config.dry_run:
        self.uploader.upload(tmp_file_name, tmp_file_name_with_path, self.sql_config.expired)

    except (RuntimeError, AssertionError) as  e:
      # log
      logger.error(e)
    finally:
      # delete 
      if self.base_config.delete_tmp_file:
        BackupJob.safe_delete(tmp_file_name_with_path)
      else:
        logger.warning("tmp file deletion is off!")

class RedisBackupJob(BackupJob):
  """
  Back up redis rdb file
  """
  def __init__(self, base_config, redis_config, uploader):
    self.base_config = base_config
    self.redis_config = redis_config
    self.uploader = uploader

  @with_logging
  def run(self):
    tmp_file_name, tmp_file_name_with_path = BackupJob.construct_filename(
        self.redis_config.prefix,
        # need an array
        ["redis"],
        self.redis_config.suffix,
        self.base_config.tmp_folder
      )

    try:
      command = "cp {} {}".format(self.redis_config.rdb_path, tmp_file_name_with_path)
      logger.debug("running {}".format(command))
      c = delegator.run(command)
      if c.return_code != 0:
        raise RuntimeError(c.std_err)

      command = "gzip --best {} | openssl des -salt -k {} > {}".format(
        tmp_file_name_with_path,
        self.base_config.passphrase,
        tmp_file_name_with_path
      )
      if not self.base_config.dry_run:
        self.uploader.upload(tmp_file_name, tmp_file_name_with_path, self.redis_config.expired)

    except (RuntimeError, AssertionError) as  e:
      # log
      logger.error(e)
    finally:
      # delete 
      if self.base_config.delete_tmp_file:
        BackupJob.safe_delete(tmp_file_name_with_path)
      else:
        logger.warning("tmp file deletion is off!")

class MongoBackupJob(BackupJob):
  """
  Back up a mongo database
  """

  def __init__(self, base_config, mongo_config, uploader):
    self.base_config = base_config
    self.mongo_config = mongo_config
    self.uploader = uploader

  def run(self):
    if self.mongo_config.ds_start and self.mongo_config.ds_end:
      for ds in self.date_range(start_date=self.mongo_config.ds_start, 
                                end_date=self.mongo_config.ds_end):
        self._run(ds.isoformat())
    else:
      self._run(ds=datetime.date.today().isoformat())

  @with_logging
  def _run(self,ds):
    tmp_file_name, tmp_file_name_with_path = BackupJob.construct_filename(
        self.mongo_config.prefix,
        # need an array
        [self.mongo_config.database],
        self.mongo_config.suffix,
        self.base_config.tmp_folder,
        self.construct_dt(ds)
      )

    try:
      # dump mongo collection to file
      # mongodump --username xxx --password xxx --host xxx --db xxx --collection xx --out xxx
      mongo_dump_command = "mongodump --host {} --username {} --password {} --db {} -c Airbnb-{}".format(
          self.mongo_config.host, 
          self.mongo_config.username,
          self.mongo_config.password,
          self.mongo_config.database,
          "{}-{}-{}".format(ds.split('-')[0],ds.split('-')[1],ds.split('-')[2])
        ) if self.mongo_config.password else "mongodump --host {} --db {} -c Airbnb-{}".format(
          self.mongo_config.host, 
          self.mongo_config.database,
           "{}-{}-{}".format(ds.split('-')[0],ds.split('-')[1],ds.split('-')[2])
        )

      command = "{} --out - | gzip --best | openssl des -salt -k {} > {}".format(
        mongo_dump_command,
        self.base_config.passphrase,
        tmp_file_name_with_path
      )

      logger.debug("running {}".format(command))
      c = delegator.run(command)


      logger.warning("dumped back up file {}".format(tmp_file_name))

      if c.return_code != 0:
        raise RuntimeError(c.std_err)

      # upload if not dry_run
      if not self.base_config.dry_run:
        self.uploader.upload(tmp_file_name, tmp_file_name_with_path)

    except (RuntimeError, AssertionError) as  e:
      # log
      logger.error(e)
    finally:
      # delete 
      if self.base_config.delete_tmp_file:
        BackupJob.safe_delete(tmp_file_name_with_path)
      else:
        logger.warning("tmp file deletion is off!")
