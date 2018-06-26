# Simple Backup
```
              _
__      _____| |__   ___  _ __ ___   ___
\ \ /\ / / _ \ '_ \ / _ \| '_ ` _ \ / _ \
 \ V  V /  __/ | | | (_) | | | | | |  __/
  \_/\_/ \___|_| |_|\___/|_| |_| |_|\___|
```
Backup local sql db or redis dump to amazon s3, qiniu or aliyun

## Usage
```
python main.py
```
or in run as `daemon`
```
python main.py -d
```

## Configure
copy `config.yml.sample` to `config.yml`

`sql_config` is an array, in case there are multiple db to back up

`dry_run` do not upload to s3 if set to `True`