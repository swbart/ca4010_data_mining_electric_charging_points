#!/usr/bin/env python

"""Reusable utility functions."""

import csv
from itertools import zip_longest
import os.path
from pathlib import Path
import requests
import shutil

from constants import IO_CHUNK_SIZE


def ensure_dir_exists(directory):
    """Ensure the given directory and all its parents exist.
    Create the directories if needed."""
    Path(directory).mkdir(parents=True, exist_ok=True)


def grouper(n, iterable, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks without reading everything
    into memory.
    See https://stackoverflow.com/questions/16289859/splitting-large-text-file-into-smaller-text-files-by-line-numbers-using-python
    """
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def download_archive(archive_url, unpack_dir):
    """Download the archive at the given URL and unpack it in the specified
    directory."""
    res = requests.get(archive_url, stream=True)
    print(res)
    # We could use tempfiles if these intermediate files take too much space.
    # However the files could be useful for debugging.
    with open(os.path.join(unpack_dir, 'dataset.zip'), 'wb') as f:
        for chunk in res.iter_content(chunk_size=IO_CHUNK_SIZE):
            f.write(chunk)
    shutil.unpack_archive(os.path.join(
        unpack_dir, 'dataset.zip'), extract_dir=unpack_dir)


def export_csv(save_path, fields, lines):
    """
    Export lines as a CSV file at the given path with the specified fields.
    lines is an array of dict's, where each dict is a mapping from field name
    to value.
    """
    with open(save_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(lines)
