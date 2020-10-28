#!/usr/bin/env python

"""Initialisations common to all country scrapers."""

import requests_cache


# All responses will be cached to a sqlite database.
# By default requests doesn't do caching.
# Moreover some dataset servers don't support caching.
# Thus we build our own cache locally.
# Delete the cache if you want to redownload everything.
requests_cache.install_cache('cache')
