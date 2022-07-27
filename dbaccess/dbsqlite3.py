# -*- coding: utf-8 -*-
#
# ./dbaccess/db_sqlite3.py
# Eduardo Banderas Alba
# 2022-07
#
# Database access
#

import os
import sqlite3


class dbSQLite(object):

  _dbfile  = None
  _db      = None
  _debug   = False

  class dbSQLiteException(Exception):
    def __init__(self, msg):      self.msg = msg
    def __str__(self):            return repr(self.msg)
  #class dbSQLiteException

  def __init__(self, dbfile, debug=False):
    self.dbfile = dbfile
    self.debug  = debug
    self.db     = sqlite3

  def to_dict(self, cur, row):
    out = {}
    for idx, field in enumerate(cur.description):
      out[field[0]] = row[idx]

    return out

  @property
  def db(self):
    return self._db

  @db.setter
  def db(self, v):
    if not self.dbfile:
      raise dbSQLite.dbSQLiteException("ERROR: No database file defined")

    self._db = v.connect(self.dbfile)
    self._db.row_factory = self.to_dict

  @property
  def debug(self):
    return self._debug

  @debug.setter
  def debug(self, v):
    self._debug = v

  @property
  def dbfile(self):
    return self._dbfile

  @dbfile.setter
  def dbfile(self, v):
    self._dbfile = v
#class dbSQLite
