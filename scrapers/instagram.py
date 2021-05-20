#!/usr/bin/env python
"""
Download Instagram files tagged with MFA.
This script WILL eventually be blocked-- Each time you get booted:
    1. Update the SINCE/ UNTIL to leave off on the last day that was scraped
    2. Update USERNAME/ PASSWORD to a new burner account
"""

from datetime import datetime
import time
import instaloader
import numpy as np
import os

# Instagram credentials -- will likely need multiple
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')

# Instagram ids for MFA
LOCATION_ID = '1125480'
PROFILE_ID = 'mfaboston'

# Update each time scraper is blocked
SINCE = datetime(2019, 1, 1)
UNTIL = datetime(2019, 10, 11)

class InstagramRateController(instaloader.RateController):
    """
    Modify rates during scrape to prevent bot detection
    Still likely need to swap through burner accounts and good idea to play with delay numbers
    """
    def sleep(self, secs):
        delay = np.random.randint(5,15)
        time.sleep(delay)
    
    def query_waittime(self, query_type, current_time, untracked_queries=False):
        return 5.0

L = instaloader.Instaloader(save_metadata=True,
                            compress_json=True,
                            download_videos=False,
                            rate_controller=lambda ctx: InstagramRateController(ctx))
profile = instaloader.Profile.from_username(L.context, PROFILE_ID)
L.login(USERNAME, PASSWORD)

# Saves images to a folder inside the one this script is being run from 
for post in L.get_location_posts(LOCATION_ID):
    if post.date > UNTIL:
        continue
    L.download_post(post, target=LOCATION_ID)
