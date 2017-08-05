#!/usr/bin/env python3
# to run in conda:
# . activate facebook

import facebook

import sys
import os
import json
import argparse
import dateutil.parser
import pprint

import jclfb as fb

parser = argparse.ArgumentParser(
    description="""Dump feed.""")

parser.add_argument(dest="input_file", 
     help="JSON archive of facebook group.")

args = parser.parse_args()

with open(args.input_file, "r") as fh:
    group = json.load(fh)
    for k in group:
        if k[-4:] == 'feed':
            feed = group[k]
            break

if feed is None:
    print("No feed found.")
    os.exit(-1)

for post in feed['data']:
    print("-------------------------------------------------------------------")
    pprint.pprint(post)
