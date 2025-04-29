#!/usr/bin/sh
PYTHON_PATH=/cygdrive/c/Python27
PATH=$PYTHON_PATH:$PATH

python src/pyutils/enum.py  # currently fails due to shadowed "string" module
python test/nputils/test_min_dtype.py
python test/nputils/test_recarray.py
python test/pyutils/cycle/test_bicycle.py
