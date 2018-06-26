# -*- coding:utf-8 -*-
#  _________________________________________
# / Around computers it is difficult to     \
# | find the correct unit of time to        |
# | measure progress. Some cathedrals took  |
# | a century to complete. Can you imagine  |
# | the grandeur and scope of a program     |
# | that would take as long?                |
# |                                         |
# | -- Epigrams in Programming, ACM SIGPLAN |
# \ Sept. 1982                              /
#  -----------------------------------------
#         \   ^__^
#          \  (oo)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||

import functools
import inspect

from main import logger

# This decorator can be applied to
def with_logging(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    logger.info('LOG: Running job "%s"' % inspect.getmodule(func))
    result = func(*args, **kwargs)
    logger.info('LOG: Job "%s" completed' % inspect.getmodule(func))
    return result
  return wrapper