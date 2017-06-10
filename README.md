# fb-group-archiver
Some tools to archive a facebook group to JSON and convert it to LaTeX.

To archive a group, log into the Facebook graph explorer (https://developers.facebook.com/tools/explorer) and get a user
token that has the manage_group_pages permission set and your user is an administrator for the group.

Next, run get-group.py to download the text of the feed and the various metadata:
```
get-group.py -g "group name" -f group.json -p group_picts -u user_token
```

To generate a pdf file of the group with the static images inline:
```
feed2tex.py -p group_picts group.json > group.tex
pdflatex group.tex
```
