#!/usr/bin/env python3
# to run in conda:
# . activate facebook

import facebook

import sys
import os
import json
import csv
import argparse

import jclfb as fb

parser = argparse.ArgumentParser(
    description="""Archive a facebook group to a json or csv file.""")

parser.add_argument("-d", "--debug", default=0, action="count",
    help="Increase the level of debug output.")

parser.add_argument("-j", "--json-file", metavar="fn",
    help="Save retrieved group into this file as a JSON encoded data.")

parser.add_argument("-u", "--user-token",
    help="Query the group from facebook using the provided user token."
    " This may be generated from the facebook graph API explorer. Make sure"
    " the manage_group_pages permission is granted and the user is an admin for"
    " the group."
    " https://developers.facebook.com/tools/explorer")

parser.add_argument("-p", "--pictures-dir", metavar="dir",
    help="Download the pictures into the indicated directory.")

parser.add_argument("-g", "--group-name", metavar="name",
    help="Group name to archive.")

parser.add_argument("-i", "--input-file", metavar="fn",
     help="Do not query facebook for data but read from provided json file.")

args = parser.parse_args()

fb.debug = args.debug

if args.user_token and args.group_name:
    graph = facebook.GraphAPI(access_token=args.user_token, version='2.9')

    groups = graph.search(type='group', q=args.group_name)
    if args.debug>1:
        print(json.dumps(groups, indent=2))

    gr = groups['data'][0]
    print("Downloading group:")
    print(json.dumps(gr))
    group_id = gr['id']

    group = dict()
    group[group_id] = fb.get_object(graph, group_id)

    members = group_id+"/members?limit=1000"
    group[members] = fb.get_object(graph, members)

    # This is a breadth first querry and then fill in each feed
    feed = fb.get_object(graph,
        group_id+"/feed?limit=100?fields=id,from,message,created_time,updated_time")
    feed = fb.dig_feed(graph, feed)
    group[group_id+'/feed'] = feed
    
elif args.input_file:
    with open(args.input_file, "r") as fh:
        group = json.load(fh)
    for k in group:
        if k[-4:] == 'feed':
            feed = group[k]
            break

else:
    print("No input data specified.")
    sys.exit(-1)

if feed is None:
    print("No feed found.")

if args.debug>1:
    print(json.dumps(group, indent=2))
    #fb.print_feed1(group)

if args.pictures_dir:
    try: os.makedirs(args.pictures_dir)
    except: pass
    fb.get_photos(feed, args.pictures_dir)

if args.json_file:
    with open(args.json_file, "w") as fh:
        json.dump(group, fh)
