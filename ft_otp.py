#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ./ft_otp.py
# Eduardo Banderas Alba
# 2022-07
#
"""
    -g filename.key      File with the string to use. Content can be in hex or base32
    -t <type>            Select the type of string contained in the file <filename.key>
                           type    => base32|hex
                           default => base32
    -g filename.key -P   It requests a password to encrypt the content of the filename.key
    -gk filename.key     Generate OTP, this mode don´t store any information
    -gkf filename.key    Generate random passphrase in base32
    -gkP                 Generate random password for encryption data
    -k                   Generate OTP
    -k -P                Request password for decryption
    -s seconds           TOTP time-step duration (default=`30`)
    -d digits            Number of digits in one-time-password
    -q                   Show info stored in database
    -a algorithm         Support values are sha1, sha256, sha512 (default sha1)
    -S service           Name of the service where otp will be used, default totp
    -h                   Show help

  # Configuration file: ./totp.cfg, /etc/totp/totp.cfg
  # Usage:
  #   Generate OTP using filename.key
    - ./{0} -gk filename.key [-t <base32|hex>] [-a <sha1|sha256|sha512>]
  #   Save key into database
    - ./{0} -g filename.key -S service [-P] [-t <base32|hex>]
  #   Generate OTP using database
    - ./{0} -k -S service [-P] [-s <seconds>] [-d <digits>] [-a <sha1|sha256|sha512>]
  #   Consult the information stored in the database
    - ./{0} -q [-S service]
"""
import sys, os

from getpass         import getpass

from utils.tools     import *

from modules.aes     import aes
from modules.config  import cfg
from modules.totp    import totp

from dbaccess.dbsqlite3  import dbSQLite


class args:
  newkey    = False
  totp      = False
  query     = False
  getpasswd = False
  key       = None
  type      = 'base32'
  algorithm = 'sha1'
  service   = None
  seconds   = 30
  digits    = 6
  genrandom = {
    'run': False,
    'file': None
  }

  genrandompasswd = False

  def json():
    logger('* args object:')
    logger({
      'newkey': args.newkey,
      'totp': args.totp,
      'query': args.query,
      'genrandom': args.genrandom,
      'genrandompasswd': args.genrandompasswd,
      'key': args.key,
      'type': args.type,
      'algorithm': args.algorithm,
      'service': args.service,
      'getpasswd': args.getpasswd,
      'seconds': args.seconds,
      'digits': args.digits
    }, out=sys.stderr)
#class args


def main():
  parse_arguments(args)

  db = dbSQLite  # hack
  if args.type == 'base32':
    pass #TODO check if content is base32

  if args.type == 'hex':
    pass #TODO check if content is hex

  if args.getpasswd:
    logger('  - Enter the encryption password')
    cfg.passwd = getpass("  - Password: ")
    if not cfg.passwd:
      halt('    - Password has not been entered')

  try:
    otp = totp(**{
      'conn':    db(cfg.db['filepath'], cfg.DEBUG).db,
      'version': cfg.version,
      'debug':   cfg.DEBUG,
      'secret':  args.key,
      'algo':    args.algorithm,
      'mod':     args.digits,
      'steps':   args.seconds
    })

    if args.newkey and args.totp:  #Simple usage
      logger('OTP Code: {0}'.format(otp.generate()))

    elif args.genrandom['run']:
      with open(args.genrandom['file'], 'w') as fw:
        secret = otp.random_secret()
        fw.write(secret)

      logger('OTP Random secret {0}'.format(secret))
    elif args.genrandompasswd:
      cipher = aes(debug=cfg.DEBUG)
      logger('Generate random password for encryption data: {0}'.format(cipher.random_key(32)))

    elif args.newkey:  #load newkey
      cipher = aes(cfg.passwd, cfg.secret, cfg.DEBUG)
      cipher.encrypt(args.key)
      result = otp.getsecret(args.service)
      if result:
        halt('  - The service exists in database', 1)

      otp.add({
        'service': args.service,
        'type': args.type,
        'seed': cfg.secret,
        'encrypted': cipher.encrypted
      })

    elif args.totp:  #Time-Based One-Time Password
      result = otp.getsecret(args.service)
      if not result:
        halt("  - Service not found in database", 1)

      cipher    = aes(cfg.passwd, cfg.secret, cfg.DEBUG)
      encrypted = otp.getsecret(args.service)
      cipher.decrypt(encrypted)
      otp.secret = cipher.decrypted
      logger('OTP Code: {0}'.format(otp.generate()))

    elif args.query:
      for result in otp.query():
        s = ""

        for k, v in result.items():
          s += '{0}: {1} ; '.format(k, v)

        logger(s)

  except Exception as e:
    logger("* {0}".format(e))

  if cfg.DEBUG:
    cfg.json()
    args.json()
#main


def parse_arguments(args):
  options_ = [ '-g', '-k', '-gk', '-gkf', '-gkP', '-S', '-a', '-t', '-P', '-d', '-s', '-q', '-h' ]
  options  = ' '.join(sys.argv[1:]).strip().split(' ')
  filename = None

  i = 0
  while len(options) > i:
    data = options[i]
    if data == '-h':
      _halt_with_doc('', 0)
    elif data == '-P':
      args.getpasswd = True
    elif data == '-q':
      args.query = True
    elif data == '-k':
      args.totp = True
    elif data == '-gkP':
      args.genrandompasswd = True
    elif data in options_:
      i += 1;
      if data == '-g' or data == '-gk':
        args.newkey = True
        filename    = options[i]

      if data == '-gk':
        args.newkey = True
        args.totp   = True

      if data == '-gkf':
        args.genrandom['run']  = True
        args.genrandom['file'] = options[i]

      if data == '-t':
        if options[i] not in [ 'base32', 'hex' ]:
          halt("ERROR: don't support -t options `{0}`".format(options[i]))

        args.type = options[i]
      #endif

      if data == '-S':         args.service   = options[i]
      if data == '-a':         args.algorithm = options[i]
      if data == '-s':         args.seconds   = int(options[i])
      if data == '-d':         args.digits    = int(options[i])
    i += 1
  #endwhile

  if len(options) < 1:
    _halt_with_doc('', 0)

  if filename:
    if not os.path.isfile(filename):
      halt("ERROR: No such file, '{0}'".format(filename))

    with open(filename, 'rb') as f:
      args.key = f.read().rstrip().decode('UTF-8')

  if args.service is None:
    logger("WARNING: No service identified", out=sys.stderr)
#parse_arguments


def _halt_with_doc(msg, code = 0):
  halt('\n' + msg + '\n' + '-' * 80 + __doc__.format(sys.argv[0]), code)
#_halt_with_doc


if __name__ == "__main__":
  try:    reload(sys); sys.setdefaultencoding("utf8")
  except: pass

  if cfg.dbtype == 'sqlite3':
    try:      import sqlite3 as db
    except ModuleNotFoundError as e:
      halt("ERROR: {0}".format(e), 1)

  main()
