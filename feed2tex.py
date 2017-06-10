#!/usr/bin/env python3
# to run in conda:
# . activate facebook

import sys
import os
import json
import argparse
from pathlib import Path
import re

import jclfb as fb

parser = argparse.ArgumentParser(
    description="""Convert json archive of a facebook group to a text version
    thats kinda like the page.""")

parser.add_argument("-d", "--debug", default=0, action="count",
    help="Increase the level of debug output.")

parser.add_argument("-p", "--pictures-dir", metavar="dir",
    help="Directory where the pictures are stored.")

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

def url2fn(url):
    fn = url.split('/')[-1]
    fn = fn.split('?')[0]
    return fn

def fmt_name(d):
    return d['name'] + " (" + d['id'] + ") " + d.get('type','')

cleaner = str.maketrans('\x01\x03', 'xx')

def sanitize(s):
    s = s.replace('_', '\_')
    s = s.replace('&', '\&')
    s = s.replace('$', '\$')
    s = s.replace('#', '\#')
    s = s.replace('\x01', ' ')
    s = s.replace('\x03', ' ')
    return s


def print_field(d, field):
    if field in d:
        if field == 'from':
            print('\\item[from:]', sanitize(fmt_name(d['from'])))
        elif field in ['source', 'media', 'full_picture']:
            if field in ['full_picture', 'source']:
                url = d[field]
            else:
                url = d[field]['image']['src']
            p = Path(args.pictures_dir, url2fn(url))
            if p.suffix not in ['.php']:
                fn = sanitize(str(p))
                print('\\item[' + sanitize(field) + ':] ' + fn)
            if p.suffix in ['.jpg', '.png'] and p.exists():
                print("\\par\\includegraphics[width=4.5in]{" + str(p) +"}" )
        else:
            print("\\item[" + sanitize(field) + ":] " + sanitize(d[field]))
        del d[field]

    
def feed2tex(d):
    if isinstance(d, dict):
        print_field(d, 'from')
        print_field(d, 'created_time')
        print_field(d, 'updated_time')
        print_field(d, 'message')
        print_field(d, 'story')
        print_field(d, 'description')
        print_field(d, 'title')
        print_field(d, 'full_picture')
        print_field(d, 'source')
        if 'reactions' in d:
            print('\\begin{itemize}')
            for i,name in enumerate(d['reactions']['data']):
                if i==0:
                    print('\\item[reactions:]', fmt_name(name))
                else:
                    print('\\item[]', fmt_name(name))
            print('\\end{itemize}')
            del d['reactions']
        if 'description_tags' in d:
            for l in d['description_tags']:
                print('\\item[tag:]', sanitize(fmt_name(l)))
            del d['description_tags']
        print_field(d, 'media')

        if 'attachments' in d:
            print('\\begin{itemize}')
            print('\\item[attachments:] -----------------------------------')
            feed2tex(d['attachments'])
            del d['attachments']
            print('\\end{itemize}')
        if 'subattachments' in d:
            print('\\begin{itemize}')
            print('\\item[subattachments:] -----------------------------------')
            feed2tex(d['subattachments'])
            del d['subattachments']
            print('\\end{itemize}')
        if 'data' in d:
            feed2tex(d['data'])
            del d['data']
        if 'comments' in d:
            print('\\begin{itemize}')
            print('\\item[coments:] -----------------------------------')
            feed2tex(d['comments'])
            del d['comments']
            print('\\end{itemize}')
        
        if 'paging' in d:
            del d['paging']
        if 'target' in d:
            del d['target']
        #if len(d):
            #print(json.dumps(d, indent=2))
        print("\\end{itemize}")
        #print('\\noindent\\rule{2cm}{0.4pt}')
        print("\\begin{itemize}")
        print("\\item -----------------------------------")
        
    elif isinstance(d, list):
        for row,v in enumerate(d):
            feed2tex(v)

print("""
\\documentclass[11pt]{article}
\\usepackage{graphicx}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{listings}
\\lstset{
basicstyle=\small\ttfamily,
breaklines=true
}

\\pagestyle{empty}

\\begin{document}

\\renewcommand\\labelitemi{1}
\\renewcommand\\labelitemii{2}
\\renewcommand\\labelitemiii{3}
\\renewcommand\\labelitemiv{4}

\\begin{itemize}
""")

feed2tex(feed)

print("""
\\item end 
\\end{itemize}
\\end{document}
""")
