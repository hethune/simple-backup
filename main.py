# -*- coding:utf-8 -*-
#  ___________________________
# < Is this really happening? >
#  ---------------------------
#         \   ^__^
#          \  (oo)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||

from time import sleep
import argparse

def load_config():
  import yaml
  with open('config.yml') as config_file:
    config = yaml.load(config_file)
    return config

config = load_config()

import logging
import sys
logger = logging.getLogger()
# it's very import to keep daemon running
logger.propagate = False
handler = logging.FileHandler(config["base_config"]["log_file"])
formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

log_level_config = config["base_config"]["log_level"]
assert log_level_config in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
if log_level_config == 'DEBUG':
  log_level = logging.DEBUG
elif log_level_config == 'INFO':
  log_level = logging.INFO
elif log_level_config == 'WARNING':
  log_level = logging.WARNING
elif log_level_config == 'ERROR':
  log_level = logging.ERROR  

logger.setLevel(log_level)

class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''

   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

stdout_logger = logging.getLogger('STDOUT')
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl

stderr_logger = logging.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl

keep_fds = [handler.stream.fileno()]

def action():
  run(config)

from daemonize import Daemonize
pid = "/tmp/simple_backup.pid"
daemon = Daemonize(app="simple_backup", pid=pid, action=action, keep_fds=keep_fds)

if __name__ == "__main__":
  from run import run
  parser = argparse.ArgumentParser(description='Simple Backup')
  parser.add_argument('-d', "--daemon", help="Daemon mode", action="store_true")
  args = parser.parse_args()
  logger.info("############### starting simple backup services #######################")
  if args.daemon:
    daemon.start()
  else:
    action()
  
