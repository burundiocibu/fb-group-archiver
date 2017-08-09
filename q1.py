#!/usr/bin/env python3
# to run in conda:
# . activate facebook

import facebook

import sys
import os
import json
import argparse
import dateutil.parser
import datetime

import jclfb as fb

parser = argparse.ArgumentParser(
    description="""Query feed.""")

parser.add_argument("-d", "--debug", default=0, action="count",
    help="Increase the level of debug output.")

parser.add_argument("--start-time",
    default=dateutil.parser.parse("Jan 1 2000 00:00+0000"),
    type=dateutil.parser.parse,
    help="Ignore actions prior to this time.")

parser.add_argument("--stop-time",
    default=dateutil.parser.parse("Jan 1 2100 00:00+0000"),
    type=dateutil.parser.parse,
    help="Ignore actions after this time.")

parser.add_argument(dest="input_file", 
     help="JSON archive of facebook group.")

args = parser.parse_args()

print("Ignoring actions before this time:", args.start_time)
print("Ignoring actions after this time:", args.stop_time)

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

members = dict()
for m in group['458515477648717/members?limit=1000']['data']:
    members[m['id']] = m['name']

# for each id, a list of times
posts = dict()
reactions = dict()
comments = dict()

for post in feed['data']:
    t = dateutil.parser.parse(post['created_time'])
    if t>args.start_time and t<args.stop_time:
        id = post['from']['id']
        posts[id] = posts.get(id, list()) + [t]
        if 'reactions' in post:
            for reaction in post['reactions']['data']:
                id = reaction['id']
                reactions[id] = reactions.get(id, list()) + [t]
    if 'comments' in post:
        for c in post['comments']['data']:
            t = dateutil.parser.parse(c['created_time'])
            if t>args.start_time and t<args.stop_time:
                id = c['from']['id']
                comments[id] = comments.get(id, list()) + [t]
            
lurkers = set(members.keys()) - set(posts.keys()) - set(reactions.keys()) - set(comments.keys())
react_only = set(reactions.keys()) - set(posts.keys()) - set(comments.keys())
post_only = set(posts.keys()) - set(reactions.keys()) - set(comments.keys())
comment_only = set(comments.keys()) - set(reactions.keys()) - set(posts.keys())

def ppct(n,m):
    return "{} ({:2.2f}%)".format(n, 100*n/m)

def pmem(msg, members, ids):
    print(msg, ppct(len(ids), len(members)))
    for id in ids:
        if id in members:
            print("   ", members[id].encode('utf-8'))
        else:
            print("   ", id, ", no longer a member")
    print("")

print("Members:", len(members))
pmem("Members that lurked:", members, lurkers)
pmem("Members that posted:", members, posts)
pmem("Members that commented:", members, comments)
pmem("Members that reacted:", members, reactions)
pmem("Members that only posted:", members, post_only)
pmem("Members that only reacted:", members, react_only)
pmem("Members that only commented:", members, comment_only)

post_then_react = set()
react_then_post = set()
post_then_comment = set()
comment_then_post = set()
react_then_comment = set()
comment_then_react = set()
for id,pt in posts.items():
    rt = reactions.get(id, list())
    if len(pt) and len(rt):
        if min(pt) < min(rt):
            post_then_react.add(id)
        else:
            react_then_post.add(id)
    ct = comments.get(id, list())
    if len(pt) and len(ct):
        if min(pt) < min(ct):
            post_then_comment.add(id)
        else:
            comment_then_post.add(id)
    if len(rt) and len(ct):
        if min(pt) < min(ct):
            react_then_comment.add(id)
        else:
            comment_then_react.add(id)

pmem("Members that post then react:", members, post_then_react)
pmem("Members that react then post:", members, react_then_post)

pmem("Members that post then comment:", members, post_then_comment)
pmem("Members that comment then post:", members, comment_then_post)

pmem("Members that react then comment:", members, react_then_comment)
pmem("Members that comment then react:", members, comment_then_react)
