#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version: Thu 22 Aug 2013
#   Initial build.
#

import os

import ted

ipath = ted.paths['data']['small']['path']
fname = 'fpC_all_uniq.csv'
ifname = os.path.join(ipath, fname)

with open(ifname, 'r') as fsock:
    lines = fsock.readlines()

lines = [lines[-1]] + lines[:-1]

with open(ifname, 'w') as fsock:
    fsock.write(''.join(lines))
