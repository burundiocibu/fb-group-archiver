#!/usr/bin/env python3

import facebook
import json
import urllib.request
import os

debug = 1

def get_object(graph, id, args):
    if args.debug:
        print("-------------------------------------------------------------------------------")
    if args.debug>1:
        print("get_object({})".format(id))
    resp = graph.get_object(id=id)
    if args.debug:
        print(json.dumps(resp, indent=2))
    return resp


def walk_feed(graph, feed, args):
    meta_on_feed=True
    for i in feed:
        if i == 'data':
            for j,k in enumerate(feed[i]):
                post_id = k['id']
                if meta_on_feed and args.debug:
                    msg = graph.get_object(graph, post_id+"?metadata=1", args)
                    meta_on_feed = False
                id = k['id']+"?fields=id,name,type,message"
                id += ",created_time,updated_time,full_picture,reactions"
                id += ",comments{message,reactions,comments{id,from,message,reactions}}"
                msg = get_object(graph, id, args)
                if args.debug==0:
                    print(json.dumps(msg, indent=2))

        elif i == 'paging':
            print(json.dumps(feed[i], indent=2))
            page = feed[i]
            if 'cursors' in page:
                print("cursors:{}".format(page['cursors']))
            else:
                print("no cursors")
            print("previous:{}".format(feed[i]['previous'][:80]))
            print("next:{}".format(feed[i]['next'][:80]))


def dump_json(d, depth=0, prefix=[]):
    indent=2
    if isinstance(d, dict):
        for k,v in d.items():
            dump_json(v, depth=depth+1, prefix=[k])
    elif isinstance(d, list):
        for row,v in enumerate(d):
            dump_json(v, depth=depth+1, prefix=["[{}]".format(row)])
    else:
        fmt="{: >" + str(depth*indent) + "s}"
        print(fmt.format(''), ":".join(prefix)+":", d)


def print_feed1(d, depth=0, prefix=[]):
    if isinstance(d, dict):
        for k,v in d.items():
            if k in ["previous", "next", "before", "after"]:
                return
            print_feed1(v, depth=depth+1, prefix=prefix+[k])
    elif isinstance(d, list):
        foo=prefix.pop()
        for row,v in enumerate(d):
            bar = foo+"[{}]".format(row)
            print_feed1(v, depth=depth+1, prefix=prefix+[bar])
    else:
        print(":".join(prefix)+": ", d)

        
def url2fn(url):
    fn = url.split('/')[-1]
    fn = fn.split('?')[0]
    return fn


def feed2list(d, l=list(), parent_id='unk'):
    """Reduce a json object of a facebook feed into a 2-D array suitable to send 
    to a csv file.
    """
    if len(l)==0:
        l.append(['post_id','parent_id','updated_time','author','message','picture_url','reaction...'])

    if isinstance(d, dict):
        if 'data' in d:
            feed2list(d['data'], l, parent_id=parent_id)
        elif 'from' in d:
            name = d['from']['name'] + "(" + d['from']['id'] + ")"
            row=[d['id'], parent_id, d.get('updated_time','unk'), name,
                     d.get('message','none'),
                     url2fn(d.get('full_picture', 'none'))]
            if 'reactions' in d:
                for r in d['reactions']['data']:
                    row.append(r['name'] + "(" + r['id'] + ")" + r['type'])
            l.append(row)
            if 'comments' in d:
                feed2list(d['comments'], l, parent_id=d['id'])
    elif isinstance(d, list):
        for row,v in enumerate(d):
            feed2list(v, l, parent_id=parent_id)
    else:
        print("WTF! ... I mean unknown item encountered in feed.")
    return l


def get_photos(d, dir='.'):
    if isinstance(d, dict):
        for k,v in d.items():
            if k == 'full_picture':
                fn = os.path.join(dir, url2fn(v))
                print('Downloading', v)
                urllib.request.urlretrieve(v, fn)
            elif hasattr(v, '__iter__') and type(v) is not str:
                get_photos(v, dir)
    elif isinstance(d, list):
        for row,v in enumerate(d):
            get_photos(v, dir)
