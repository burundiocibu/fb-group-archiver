#!/usr/bin/env python3
# to run in conda:
# . activate facebook

import sys
import facebook
import json
import argparse

import jclfb as fb

parser = argparse.ArgumentParser(
    description="""Archive a facebook group feed to a csv file.""")

parser.add_argument("-d", "--debug", default=0, action="count",
    help="Increase the level of debug output.")

parser.add_argument("-v", "--verbose", default=0, action="count",
    help="Increase the level of status output.")

parser.add_argument("-j", "--json-file", metavar="fn"
    help="Save retrived feed into this file as a json encoded data.")

parser.add_argument("-c", "--csv-file", metavar="fn"
    help="Reduce feed and save in this file as csv data.")

parser.add_argume("-i", "--input", metavar="fn"
     help="Do not query facebook for feed data but read from provided json file.")

args = parser.parse_args()


littlej_id = "10155878310229528"
app_id = "1652232008140001"
app_token="1652232008140001|RgEqBmc_zvs5zWa8Cwo0BlaV-5k"
# This seems to be a long lived token for debugging apps.
# This token doesn't seem to get access to the feed so I'm assuming that I didn't
# give it manage_group_pages access....
app_user_token = "EAAXesj3uhOEBAKonnKSjpksgdU3Fdp1ar4Kwosf0o2o9HOgfbEoaoDCBi4lMkbAl36nTo5NzGcsqNOVbh4zbfIfyj0PuEutg24BAT1VvWUzwBqQ3LJ1BTu1oOAY75ZAWfopFXVUGJVwwj7FKx4hKufTej8AM1Bi9QWc6AowMRG6pZB35ox"
user_token = app_user_token

# Generate this from the graph API explorer and make sure manage_group_pages is granted
user_token = "EAACEdEose0cBAAuZC4tBfZAxJCNKZCZAlyt0e2iVV3OkVXEZBsUW1Tr7EUZB9276yv7jfBfWAiusenQvAZAOuLM8OnRGL1vrmxMNFPBV5vF4SjrbFwBbEt2dpjyZCIClk5DLvCndi1KRLot0pZC4PlyWVu8XiXtNwROZBPSVCo6ZBNhTXOdErCV40Hw"

graph = facebook.GraphAPI(access_token=user_token, version='2.9')

groups = graph.search(type='group', q='Super Secret Group for Just Us')
if args.debug>1:
    print(json.dumps(groups, indent=2))

group = groups['data'][0]
group_id = group['id']

group = fb.get_object(graph, group_id, args)

members = fb.get_object(graph, group_id+"/members",args)

#feed = fb.get_object(graph, group_id+"/feed", args)
#fb.walk_feed(graph, feed, args)

feed = fb.get_object(graph, group_id+"/feed?fields=id,from,message,created_time,updated_time,full_picture,reactions,comments{id,from,message,reactions,comments{id,from,message,reactions}}", args)

#print(json.dumps(feed, indent=2))
#fb.print_feed1(feed)
import csv
fh = csv.writer(open("foo.csv", "w"), quoting=csv.QUOTE_MINIMAL)
write_feed_csv(fh, feed)
