# -*- coding:utf-8 -*-
#  ______________________________________
# / If builders built buildings the way  \
# | programmers wrote programs, then the |
# | first woodpecker to come along would |
# \ destroy civilization.                /
#  --------------------------------------
#         \   ^__^
#          \  (OO)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||

class BaseConfig(object):
  """
  Base config for settings
  tmp_folder: tmp folder to store backup files
  tmp_
  """
  def __init__(self, config):
    self.dry_run = config.get("dry_run") or False
    self.tmp_folder = config["tmp_folder"]
    self.passphrase = config["passphrase"]
    self.log_file = config["log_file"]


class S3Config(object):
  """
  Config for S3 or qiniu or aliyun
  """
  def __init__(self, config): 
    self.access_key = config["access_key"]
    self.secret_key = config["secret_key"]
    self.bucket_name = config["bucket_name"]

class SQLConfig(object):
  """
  Config for SQL dump
  """
  def __init__(self, config):
    self.host = config["host"]
    self.database = config["database"]
    self.username = config["username"]
    # ToDo: put into databag
    self.password = config["password"]
    # back up interval: Every n minutes
    self.interval = config["interval"]
    self.interval_unit = config["interval_unit"]
    # s3 file prefix and suffix
    self.prefix = config["prefix"]
    self.suffix = config["suffix"]
    # days
    self.expired = config["expired"]


class RedisConfig(object):
  """
  Config for redis dump
  """
  def __init__(self, config):
    # rdb file path;
    self.rdb_path = config["rdb_path"] 
    # back up interval: Every n minutes
    self.interval = config["interval"]
    self.interval_unit = config["interval_unit"]
    # s3 file prefix
    self.prefix = config["prefix"]
    self.suffix = config["suffix"]
    self.expired = config["expired"]


