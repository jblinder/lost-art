#!/usr/bin/env python
"""
Downloads MFA collection data
----------
Hops between proxies to prevent blocking
Requests will sometimes fail either due to bot detection or proxies failing.
Can either download entire collection, or just missing objects that failed (saved as a pickle)
Saves final data as a pickled Pandas Dataframe (it will need to be cleaned)
"""

import requests
from bs4 import BeautifulSoup
from time import sleep
import random
import pickle
import pandas as pd
from fp.fp import FreeProxy
from random_user_agent.user_agent import UserAgent

# Add extra delays to requests and save temp data
BE_NICE = True
# Use after initial scrape to only download ids that have fallen through the cracks
USE_MISSING_IDS = False
# Used after initial scrape to name pkl where data is saved to prevent overwrites -- Look in directory and increment based on the last 
SCRAPE_ATTEMPT_COUNT = 0
# Location of missing object ids list
MISSING_OBJECTS_PKL_PATH  = 'missing_object_ids.pkl'
# Location of MFA Collection Pandas Datafram (use for data analysis)
OBJECTS_PKL_PATH = 'mfa_collection.pkl'

'''
HTML Parsing
'''

def get_element(page, field):
    el = page.find('div', field)
    if not el:
        return None
    if el.findChildren('span', 'topLabel'):
        el = [child.text for child in el.findChildren('span')]
        el[0] = f'**{el[0].upper()}**'
        el = ' '.join(el)
    elif el.findChildren('span'):
        el = ' '.join([child.text for child in el.findChildren('span')])
    else:
        el = el.text
    el = el.replace('"', '\\"')
    return el


def get_title(page, field):
    el = page.find('div', field)
    if not el:
        return None
    if el.findChildren('span', 'topLabel'):
        el = [child.text for child in el.findChildren('h2')]
        el[0] = f'[[{el[0].upper()}]]'
        el = ' '.join(el)
    else:
        el = ' '.join([child.text for child in el.findChildren('h2')])
    el = el.replace('"', '\\"')
    return el


def get_onview(page, field):
    el = page.find('div', field)
    if not el:
        return None
    el = [child.text for child in el.findChildren('a')]
    el = ' '.join(el).lstrip().rstrip()
    return el


def get_images(page):
    el = page.find_all('a', 'emuseum-colorbox-img')
    image_ids = [tag['data-media-id'] for tag in el]
    if image_ids:
        return image_ids
    el = page.find('div', 'download-image')
    if not el:
        return []
    el = el.findChildren()[0]['src'].split('dispatcher/')[1]
    el = el.split('/preview')[0]
    image_ids = [el]
    return image_ids


def get_object_ids(page):
    results = page.find_all('div', ['result', 'item'])
    ids = [result['data-emuseum-id'] for result in results]
    return ids


def get_object_data(page, object_id):
    title = get_title(page, 'titleField')
    people = get_element(page, 'peopleField')
    culture = get_element(page, 'cultureField')
    period = get_element(page, 'periodField')
    display_date = get_element(page, 'displayDateField')
    object_geography = get_element(page, 'objectGeographyField')
    medium = get_element(page, 'mediumField')
    dimensions = get_element(page, 'dimensionsField')
    creditline = get_element(page, 'creditlineField')
    involine = get_element(page, 'involineField')
    collections = get_element(page, 'collectionTermsField')
    if collections:
        collections = collections.split('** ')[-1]
        collections = collections.split(',')
    classifications = get_element(page, 'classificationsField') 
    if classifications:
        classifications = classifications.split('** ')[-1]
        classifications = classifications.split('–')
    onview = get_onview(page, 'onviewField')
    if onview:
        onview = onview.split('** ')[-1]
        onview = onview.split(',')
    inscribed = get_element(page, 'inscribedField')
    web_description = get_element(page, 'webDescriptionField')
    description = get_element(page, 'descriptionField')
    provenance = get_element(page, 'provenanceField')
    image_ids = get_images(page)

    data = {
        "id": object_id,
        "title": title,
        "people": people,
        "culture": culture,
        "period": period,
        "displayDate": display_date,
        "objectGeography": object_geography,
        "medium": medium,
        "dimensions": dimensions,
        "creditline": creditline,
        "involine": involine,
        "onview": onview,
        "collectionTerms": collections,
        "classifications": classifications,
        "inscribed": inscribed,
        "webDescription": web_description,
        "description": description,
        "provenance": provenance,
        "image_ids": image_ids
    }
    return data

'''
Requests
'''

def request_page(url):
    """
    Request a page from MFA website in a non-bot(ish) way, parse page into soup
    """
    # Randomly select user_agent and proxy
    user_agent_rotator = UserAgent(limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    headers_mobile = {
        'User-Agent': user_agent
    }
    proxy = FreeProxy(rand=True).get()

    try:
        page = requests.get(url, headers=headers_mobile, proxies={
                            "http": proxy})
        soup = BeautifulSoup(page.content, 'html.parser')
    except:
        print(f'Failed requesting page with proxy http://{proxy.ip}:{proxy.port}')
        soup = None
    return soup

def get_page_count():
    """
    Number of collection search result pages
    """
    url = f'http://collections.mfa.org/search/Objects/onview%3Atrue/*/images?filter=imageExistence%3Atrue&page=1'
    soup = request_page(url)
    enum_text = soup.find('span', 'maxPages').text.replace('/', '')
    page_count = enum_text.replace(' ', '')
    return int(page_count)

def download_object_ids(): 
    """
    All object ids returned from collection search query
    """
    object_ids = []
    page_count = get_page_count() # Total pages to iterate through
    print(f'number of pages in search: {page_count}')

    # Get all of the work ids from search pages
    for page_num in range(page_count):
        url = f'https://collections.mfa.org/search/Objects/onview%3Atrue/*/images?filter=imageExistence%3Atrue&page={page_num}'
        page = request_page(url)
        ids = get_object_ids(page)
        object_ids.append(list(ids))
    object_ids = [item for sublist in object_ids for item in sublist]

def download_objects(object_ids): 
    """
    Scraped data for a collection object
    """
    # Download works
    missing_ids = []
    for object_id in object_ids:
        url = f'http://collections.mfa.org/objects/{object_id}/'
        page = request_page(url)

        if not page:
            missing_ids.append(object_id)
            continue
        object_data = get_object_data(page, object_id)
        objects.append(object_data)

        if BE_NICE:
            sleep_time = random.randint(5, 15)
            sleep(sleep_time)

    # Keep track of any denied requests or when free proxies fail
    if missing_ids:
        with open(MISSING_OBJECTS_PKL_PATH, 'wb') as f:
            pickle.dump(missing_ids, f)
    return objects

def start_download(use_missing_ids):
    """
    Download all collection objects or just missing objects
    """
    object_ids = None
    if not use_missing_ids:
        object_ids = download_object_ids()
        objects = download_objects(object_ids) 
        df = pd.DataFrame(objects)
        df.to_pickle(OBJECTS_PKL_PATH)        
        return

    with open(MISSING_OBJECTS_PKL_PATH, 'rb') as f:
        object_ids = pickle.load(f)
        object_ids = list(set(object_ids))
        objects = download_objects(object_ids) 

        df_missing = pd.DataFrame(objects)
        df_original = pd.read_pickle(OBJECTS_PKL_PATH)
        df_original = df_original.append(df_missing)
        df_original.to_pickle(OBJECTS_PKL_PATH)        
        
# Start downloading all on-view works or just missing ones
start_download(USE_MISSING_IDS)