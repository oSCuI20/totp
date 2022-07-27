# -*- coding: utf-8 -*-
#
# ./ft_otp.py
# Eduardo Banderas Alba
# 2022-07
#
# Importar config file: from config import cfg
#
class cfg:
  passwd = None
  secret = None
  dbtype = "sqlite3"
  db = {
    "filepath": None
  }

  version = "0.0.1"

  DEBUG = False

  def json():
    logger('* cfg object:')
    logger({
        'passwd': cfg.passwd,
        'secret': cfg.secret,
        'dbtype': cfg.dbtype,
        'db': cfg.db,
        'DEBUG': cfg.DEBUG
    }, out=sys.stderr)
#class cfg

import sys, os

from utils.tools import *


cfgfiles = [
  #Fichero de configuración global (producción)
  '/etc/totp/totp.cfg',

  #Fichero de configuración local (desarrollo)
  os.getcwd() + '/totp.cfg'
]

for cfgfile in cfgfiles:
  if os.path.isfile(cfgfile):
    logger("Loading configuration from `{0}`".format(cfgfile), out=sys.stderr)
    with open(cfgfile, 'r') as f:
      exec(f.read())

    break
else:
  raise Exception("ERROR: Configuration file not found")

if not cfg.secret:
  raise Exception("ERROR: The key secret is not set, you need set cfg.secret in `{0}`"
                  .format(cfgfile))

if len(cfg.secret) < 8:
    raise Exception("ERROR: The key secret is lower than 8 `{0}`".format(cfg.secret))

if not cfg.passwd:
  cfg.passwd = cfg.secret

if cfg.dbtype == 'sqlite3':
  if cfg.db['filepath'] is None:
    cfg.db['filepath'] = os.getcwd() + '/data/totp.sqlite'

  if not os.path.isdir(os.path.dirname(cfg.db['filepath'])):
    os.makedirs(os.path.dirname(cfg.db['filepath']))
#endif

#TODO dbtypes
