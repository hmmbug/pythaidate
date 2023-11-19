import logging
import os
import sys

TESTLOG = "debug.log"
if os.path.exists(TESTLOG):
    os.remove(TESTLOG)
FORMAT = "[%(filename)s:%(funcName)s():%(lineno)s] %(message)s"

bcargs = dict(
    filename=TESTLOG,
    format=FORMAT,
    level=logging.DEBUG,
)

if sys.version_info[0] < 3:
    print("Unsupported python version:", sys.version)
    exit(1)

if sys.version_info[1] <= 8:
    logging.basicConfig(**bcargs)

elif sys.version_info[1] >= 9:
    logging.basicConfig(**bcargs, encoding='utf-8')
