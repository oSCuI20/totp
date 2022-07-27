# -*- coding: utf-8 -*-
#
# ./utils/tools.py
# Eduardo Banderas Alba
# 2022-07
#
# Tools functions
#
import os, sys, json

def logger(msg, out=sys.stdout):
  try:
    if isinstance(msg, dict) or isinstance(msg, list) or isinstance(msg, tuple):
      msg = json.dumps(msg, indent=2)
  except:
    pass

  out.write(msg + "\n")
#logger


def halt(msg, code = 0):
  logger(msg, out=sys.stderr)
  sys.exit(code)
#_halt
