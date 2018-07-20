# -*- coding:utf-8 -*-
#  ________________________________________
# / Talking much about oneself can also be \
# | a means to conceal oneself.            |
# |                                        |
# \ -- Friedrich Nietzsche                 /
#  ----------------------------------------
#         \   ^__^
#          \  (OO)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||

from main import logger
from qiniu import Auth, put_file, BucketManager, etag
import boto3

class Uploader(object):
  def __init__(self):
    pass

  def upload(self):
    pass

class QiniuUploader(Uploader):
  def __init__(self, config):
    self.access_key = config.access_key
    self.secret_key = config.secret_key
    self.bucket_name = config.bucket_name

  def upload(self, key, file, expire_days=30):
    """
    key: filename
    file: file path
    expire_days: lifetime for the file
    """
    bucket_name = self.bucket_name
    q = Auth(self.access_key, self.secret_key)

    # get upload token, expires in 10 minutes
    token = q.upload_token(bucket_name, key, 600)

    ret, info = put_file(token, key, file)
    assert ret['key'] == key
    assert ret['hash'] == etag(file)

    logger.warning("successfully uploaded {}".format(file))

    bucket = BucketManager(q)
    ret, info = bucket.delete_after_days(bucket_name, key, str(expire_days))

class S3Uploader(Uploader):
  def __init__(self, config):
    self.access_key = config.access_key
    self.secret_key = config.secret_key
    self.bucket_name = config.bucket_name

  def upload(self, key, file):
    client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
    client.upload_file(file,self.bucket_name,key)
