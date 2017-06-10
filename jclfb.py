#!/usr/bin/env python3

import json
import urllib.request
import requests
import os
from pathlib import Path

debug = 0

def get_object(graph, id):
    if debug>1:
        print("-----------------------------------------------------------------")
        print("get_object({})".format(id))
    resp = graph.get_object(id=id)
    if debug and 'data' in resp:
        print("data has {} items".format(len(resp['data'])))
    if debug>3:
        print(json.dumps(resp, indent=2))
    n=0
    resp2=resp
    while True:
        n+=1
        try:
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("get {}:".format(n), resp2['paging']['next'])
            resp2 = requests.get(resp2['paging']['next']).json()
            if 'data' in resp2:
                if debug:
                    print("data has {} items".format(len(resp2['data'])))
                resp['data'] += resp2['data']
        except KeyError:
            if debug:
                print("No more data")
            break
    if 'data' in resp and debug:
        print("All data has {} items".format(len(resp['data'])))
    return resp


def dig_feed(graph, feed):
    if not 'data' in feed:
        print('No data in feed to dig...')
        return feed
    deep_data = []
    for j,k in enumerate(feed['data']):
        post_id = k['id']
        deeper = post_id + "?fields=from,message,story,created_time,updated_time,full_picture,source,attachments,reactions,comments{id,from,message,created_time,updated_time,reactions,attachments,comments{id,from,message,created_time,updated_time,reactions,attachments}}"
        msg = get_object(graph, deeper)
        if debug>1:
            print("orig:    ----------------------------------------------------")
            print(json.dumps(k, indent=2))
            print("deeper:  ----------------------------------------------------")
            print(json.dumps(msg, indent=2))
        deep_data.append(msg)
    deep_feed={}
    deep_feed['data'] = deep_data
    return deep_feed


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
            row=[d['id'], parent_id, d.get('updated_time','n/a'), name,
                     d.get('message','none'),
                     url2fn(d.get('full_picture', 'n/a'))]
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


def feed2csv():
    with open(args.csv_file, "w") as fh:
        csv_fh = csv.writer(fh, quoting=csv.QUOTE_ALL)
        feed_list = fb.feed2list(feed)
        csv_fh.writerows(feed_list)



def get_photos(d, dir='.'):
    if isinstance(d, dict):
        for k,v in d.items():
            if k in ['full_picture', 'source', 'src']:
                p = Path(dir, url2fn(v))
                if p.suffix in ['.jpg', '.mp4', '.png']:
                    if p.exists():
                        if debug>1:
                            print("Have {}:{}".format(k, p.name))
                    else:
                        print('Downloading {}:{}'.format(k, p.name))
                        if debug:
                            print(v)
                        try:
                            urllib.request.urlretrieve(v, p)
                        except urllib.error.HTTPError as err:
                            print(err)
                            p.touch()
                else:
                    if debug>1:
                        print("Skipping {}:{}".format(k, p.name))
            elif hasattr(v, '__iter__') and type(v) is not str:
                get_photos(v, dir)
    elif isinstance(d, list):
        for row,v in enumerate(d):
            get_photos(v, dir)


def fmt_name(d):
    return d['name'] + "(" + d['id'] + ")" + d.get('type','')


def print_field(d, field, prefix):
    if field in d:
        print(prefix+"**"+field +":**", d[field])
        del d[field]


def feed2text(d, depth=0):
    indent=2
    fmt="{: >" + str(depth*indent) + "s}"
    prefix = fmt.format('')
    if isinstance(d, dict):
        if 'from' in d:
            print(prefix, '-----------------------------------------------------')
            print(prefix, 'from:', fmt_name(d['from']))
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
            print(prefix, 'picture:', url2fn(d['full_picture']))
            del d['full_picture']
        if 'source' in d:
            print(prefix, 'source:', url2fn(d['source']))
            del d['source']
        if 'reactions' in d:
            print(prefix, 'reactions:', len(d['reactions']['data']))
            for l in d['reactions']['data']:
                print(prefix, '  ', fmt_name(l))
            del d['reactions']
        if 'description_tags' in d:
            for l in d['description_tags']:
                print(prefix, 'tag:', fmt_name(l))
            del d['description_tags']
        if 'media' in d:
            print(prefix, 'media:', url2fn(d['media']['image']['src']))
            del d['media']

        if 'attachments' in d:
            print(prefix, 'attachments:')
            print_feed(d['attachments'], depth=depth+1)
            del d['attachments']
        if 'subattachments' in d:
            print(prefix, 'subattachments:')
            print_feed(d['subattachments'], depth=depth+1)
            del d['subattachments']
        if 'data' in d:
            print_feed(d['data'], depth=depth+1)
            del d['data']
        if 'comments' in d:
            print(prefix, 'comments:')
            print_feed(d['comments'], depth=depth+1)
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
            print_feed(v, depth=depth)


