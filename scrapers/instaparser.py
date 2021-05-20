#!/usr/bin/env python
"""
Flattens Instagram post JSON metadata to be DataFrame compatible
----------
Decompresses JSON files for each post (they were downloaded as .xz files via the Instaloader library)
Create (and save) flat JSON file using key variables from each POST
"""

import lzma
from os import listdir
from os.path import isfile, join
import json
from pprint import pprint
import datetime

INSTAGRAM_IMAGES_PATH = f'../images/mfaboston-complete/'
OUTPUT_FILE = '20210414_instagram_posts.json' 

# get all compressed json filepaths
onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
onlyfiles = [f for f in onlyfiles if f.split('.')[-1] == 'xz']

# read all post json metadata files
posts = {"posts": []}
for json_path in onlyfiles:
    with lzma.open(f'{INSTAGRAM_IMAGES_PATH}{json_path}', mode='rt') as file:
        data = [line for line in file][0]
        d = json.loads(data)['node']
        d['filename'] = json_path
        date_text = json_path.split('.')[0]
        date_text = json_path.split('_UTC')[0]
        if 'mfaboston' not in date_text and 'iterator' not in date_text:
            file_date = datetime.datetime.strptime(date_text, '%Y-%m-%d_%H-%M-%S')
        else:
            file_date = None
        d['date'] = file_date
        posts['posts'].append(d)

# convert json posts into flattened objects
entries = []
for post in posts['posts']:
    entry = {}
    if 'edge_media_to_caption' in post:
        if post['edge_media_to_caption']['edges']:
            entry['text'] = post['edge_media_to_caption']['edges'][0]['node']['text']
    if 'date' in post:
        entry['date'] = post['date']
    if 'filename' in post:
        entry['filename'] = post['filename']
    if 'id' in post:
        entry['id'] = post['id']
    if 'shortcode' in post: 
        entry['shortcode'] = post['shortcode']
    if 'edge_media_to_comment' in post:
        entry['comments_count'] = post['edge_media_to_comment']['count'] 
    if 'comments_disabled' in post:
        entry['comments_disabled'] = post['comments_disabled']
    if 'taken_at_timestamp' in post:
        entry['taken_at_timestamp'] = post['taken_at_timestamp']
    if 'dimensions' in post:
        entry['width'] = post['dimensions']['width']
        entry['height'] = post['dimensions']['height']
    if 'display_url' in post:
        entry['display_url'] = post['display_url']
    if 'edge_liked_by' in post: 
        entry['liked_count'] = post['edge_liked_by']['count']
    if 'edge_media_preview_like' in post:
        entry['preview_liked_count'] = post['edge_media_preview_like']['count'] 
    if 'owner' in post:
        entry['user_id'] = post['owner']['id']
    if 'thumbnail_src' in post:
        entry['thumbnail_url'] = post['thumbnail_src']
    if 'is_video' in post:
        entry['is_video'] = post['is_video']
    entries.append(entry)

with open(OUTPUT_FILE, 'w') as f:
   json.dump(entries, f, ensure_ascii=False, default=str)