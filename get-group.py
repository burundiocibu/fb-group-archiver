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

parser.add_argument("-c", "--csv-file", metavar="fn",
    help="Reduce feed from group and save in this file as csv data.")

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
    group[group_id] = fb.get_object(graph, group_id, args)

    members = group_id+"/members"
    group[members] = fb.get_object(graph, members, args)

    #todo: check the cursors to see if all the request was retrieved.
    group[group_id+'/feed'] = fb.get_object(graph, group_id+"/feed?fields=id,from,message,created_time,updated_time,full_picture,reactions,comments{id,from,message,reactions,comments{id,from,message,reactions}}", args)
    
elif args.input_file:
    with open(args.input_file, "r") as fh:
        group = json.load(fh)
        
else:
    print("No input data specified.")
    sys.exit(-1)

for k in group:
    if k[-4:] == 'feed':
        feed = group[k]
if feed is None:
    print("No feed found in group.")

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

if args.csv_file:
    with open(args.csv_file, "w") as fh:
        csv_fh = csv.writer(fh, quoting=csv.QUOTE_ALL)
        feed_list = fb.feed2list(feed)
        csv_fh.writerows(feed_list)
