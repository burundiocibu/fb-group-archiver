#!/usr/bin/env python3
# to run in conda:
# . activate facebook

import facebook

import sys
import os
import json
import argparse

import jclfb as fb


def print_field(d, field, prefix):
    if field in d:
        print(prefix+field +":", d[field])
        del d[field]


def feed2text(d, depth=0):
    indent=2
    fmt="{: >" + str(depth*indent) + "s}"
    prefix = fmt.format('')
    if isinstance(d, dict):
        if 'from' in d:
            print(prefix, '-----------------------------------------------------')
            print(prefix, 'from:', fb.fmt_name(d['from']))
            del d['from']
        if 'id' in d:
            del d['id']
        print_field(d, 'created_time', prefix)
        print_field(d, 'updated_time', prefix)
        print_field(d, 'message', prefix)
        print_field(d, 'story', prefix)
        print_field(d, 'description', prefix)
        print_field(d, 'title', prefix)
        if 'full_picture' in d:
            print(prefix, 'picture:', fb.url2fn(d['full_picture']))
            del d['full_picture']
        if 'source' in d:
            print(prefix, 'source:', fb.url2fn(d['source']))
            del d['source']
        if 'reactions' in d:
            print(prefix, 'reactions:', len(d['reactions']['data']))
            for l in d['reactions']['data']:
                print(prefix, '  ', fb.fmt_name(l))
            del d['reactions']
        if 'description_tags' in d:
            for l in d['description_tags']:
                print(prefix, 'tag:', fb.fmt_name(l))
            del d['description_tags']
        if 'media' in d:
            print(prefix, 'media:', fb.url2fn(d['media']['image']['src']))
            del d['media']

        if 'attachments' in d:
            print(prefix, 'attachments:')
            feed2text(d['attachments'], depth=depth+1)
            del d['attachments']
        if 'subattachments' in d:
            print(prefix, 'subattachments:')
            feed2text(d['subattachments'], depth=depth+1)
            del d['subattachments']
        if 'data' in d:
            feed2text(d['data'], depth=depth+1)
            del d['data']
        if 'comments' in d:
            print(prefix, 'comments:')
            feed2text(d['comments'], depth=depth+1)
            del d['comments']

        if 'paging' in d:
            del d['paging']
        if 'target' in d:
            del d['target']
        #if len(d):
            #print(json.dumps(d, indent=2))
        print(prefix, '.')
        
    elif isinstance(d, list):
        for row,v in enumerate(d):
            feed2text(v, depth=depth)


parser = argparse.ArgumentParser(
    description="""Convert json archive of a facebook group to a text version
    thats kinda like the page.""")

parser.add_argument("-d", "--debug", default=0, action="count",
    help="Increase the level of debug output.")

parser.add_argument(dest="input_file", 
     help="JSON archive of facebook group.")

args = parser.parse_args()

fb.debug = args.debug
with open(args.input_file, "r") as fh:
    group = json.load(fh)
    for k in group:
        if k[-4:] == 'feed':
            feed = group[k]
            break

if feed is None:
    print("No feed found.")
    os.exit(-1)

feed2text(feed)
