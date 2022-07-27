# -*- coding: utf-8 -*-
#
# ./modules/totp.py
# Eduardo Banderas Alba
# 2022-07
#
# One Time Password.
#
import hashlib
import hmac
import struct
import random

from time     import time, gmtime, strftime
from base64   import b32encode, b32decode
from binascii import hexlify, unhexlify, Error
from utils.tools import *


class totp(object):

  _mod = 1
  _digits = [
    1,             # 0 digits
    10,            # 1 digits
    100,           # 2 digits
    1000,          # 3 digits
    10000,         # 4 digits
    100000,        # 5 digits
    1000000,       # 6 digits
    10000000,      # 7 digits
    100000000      # 8 digits
  ]

  _hex_secret = None
  _secret     = None
  _algo       = None
  _steps      = 30  #seconds
  _debug      = False
  _now        = None
  _counter    = None
  _conn       = None
  _version    = None

  class totpException(Exception):
    def __init__(self, msg):      self.msg = msg
    def __str__(self):            return repr(self.msg)
  #class totpException

  def __init__(self, **kwargs):
    for key, value in kwargs.items():
      self.__setattr__(key, value)

  def __del__(self):
    if self.debug:
      hex_counter, dec_counter = (0, 0)
      hex_secret, unhex = (None, None)
      if self.counter:
        hex_counter,  dec_counter = (self.counter.hex().upper(),
                                     int(self.counter.hex(), 16))

      if self._hex_secret:
        hex_secret = hexlify(self._hex_secret).decode('UTF-8')
        unhex      = self._hex_secret.decode('UTF-8')

      digits = 0
      for d in self._digits:
        if d == self.mod:
          break
        digits += 1

      if self.conn:
        self.conn.close()

      logger('* totp object:')
      logger({
        'hex-secret': hex_secret,
        'base32-secret': self.secret,
        'unhex': unhex,
        'digits': digits,
        'Step time (seconds)': self.steps,
        'Current time': strftime("%Y-%m-%d %H:%M:%S UTC (%s)", gmtime(self.now)),
        'Counter': "0x{0} ({1})".format(hex_counter, dec_counter)
      })
    #endif
  #__del__

  def generate(self):
    self.now     = time()
    self.counter = self.now / self.steps

    mac    = hmac.new(self._hex_secret, self.counter, self.algo).digest()
    offset = mac[-1] & 0x0f
    bin    = struct.unpack('>L', mac[offset:offset + 4])[0] & 0x7fffffff

    return "{0:06d}".format(bin % self.mod)
  #generate

  def random_secret(self, num=16):
    return b32encode(bytes([random.randint(0, 127) for _ in range(num)])).decode('UTF-8')

  def add(self, args):
    sql = "INSERT INTO totp (`service`, `secret`, `seed`, `type`) VALUES (?, ?, ?, ?);"

    cur = self.conn.cursor()
    cur.execute(sql, (args['service'], args['encrypted'], args['seed'], args['type']))
    self.conn.commit()
    cur.close()
  #add

  def query(self):
    sql = "SELECT * FROM totp;"
    cur = self.conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()

    return result
  #query

  def getsecret(self, service):
    sql = "SELECT secret FROM totp WHERE id = ? OR service = ? ORDER BY updated DESC;"
    cur = self.conn.cursor()
    cur.execute(sql, (service, service,))
    result = cur.fetchone()
    cur.close()
    if not result:
        return ""

    return result['secret']
  #getsecret

  @property
  def conn(self):
    return self._conn

  @conn.setter
  def conn(self, v):
    self._conn = v
    cur = self._conn.cursor()
    cur.execute("SELECT name FROM sqlite_master GROUP BY 1 HAVING type='table' AND name='totp';")
    exist = cur.fetchone()
    cur.close()

    if not exist:
      self.__initialize_table()
  #conn

  def __initialize_table(self):
    sql = """
CREATE TABLE `totp` (
  `id`                  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  `service`             VARCHAR(255) NOT NULL,
  `secret`              BLOB,
  `seed`                VARCHAR(255) NOT NULL,
  `type`                VARCHAR(255) DEFAULT 'base32',
  `updated`             DATETIME DEFAULT CURRENT_TIMESTAMP,
  `current_version`     VARCHAR(32) DEFAULT '{0}'
);
    """.format(self.version)
    cur = self.conn.cursor()
    cur.execute(sql)
    self.conn.commit()
    cur.close()
  #__initialize_table

  @property
  def secret(self):
    return self._secret

  @secret.setter
  def secret(self, v):
    try:
      if v:
        print(v)
        key = v.rstrip().upper() + '=' * ((8 - len(v.rstrip())) % 8)
        self._hex_secret = b32decode(key)
        self._secret     = key
    except Error as e:
      raise totp.totpException(e)
    except:
      raise totp.totpException("ERROR: invalid secret")
  #secret

  @property
  def algo(self):
    return self._algo

  @algo.setter
  def algo(self, v):
    if   v.lower() == 'sha1':    self._algo = hashlib.sha1
    elif v.lower() == 'sha256':  self._algo = hashlib.sha256
    elif v.lower() == 'sha512':  self._algo = hashlib.sha512
    else:
      raise totp.totpException("ERROR: `{0}` algorithm is not supported")
  #algo

  @property
  def mod(self):
    return self._mod

  @mod.setter
  def mod(self, v):
    if not isinstance(v, int):
      raise totp.totpException("Number of digits is not valid")

    self._mod = self._digits[v]
  #mod

  @property
  def steps(self):
    return self._steps

  @steps.setter
  def steps(self, v):
    if not isinstance(v, int):
      raise totp.totpException("Time step duration is not valid")

    self._steps = int(v)
  #steps

  @property
  def counter(self):
    return self._counter

  @counter.setter
  def counter(self, v):
    self._counter = struct.pack('>Q', int(v))

  @property
  def version(self):
    return self._version

  @version.setter
  def version(self, v):
    self._version = v

  @property
  def now(self):
    return self._now

  @now.setter
  def now(self, v):
    self._now = int(v)

  @property
  def debug(self):
    return self._debug

  @debug.setter
  def debug(self, v):
    self._debug = v
