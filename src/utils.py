#!/usr/bin/env python

"""Reusable utility functions."""

import csv
import gzip
from itertools import zip_longest
import os.path
from pathlib import Path
import re
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


def uncompress_gzip(gzip_path, target_dir):
    """
    Uncompress a gzip file into the target directory.

    Credits to https://stackoverflow.com/a/57923425.
    """
    # Gzip is for compressing a single file
    # Get the target file name
    # Note that this will override the archive if it does not end in .gz
    filename = os.path.split(gzip_path)[-1]
    filename = re.sub(r"\.gz$", "", filename, flags=re.IGNORECASE)

    with gzip.open(gzip_path, 'rb') as f_in:
        with open(os.path.join(target_dir, filename), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# Add the ability to "unarchive" ".gz" files using the shutil.unpack_archive
# function
shutil.register_unpack_format('gz',
                              ['.gz', ],
                              uncompress_gzip)


def download_archive(archive_url, unpack_dir, archive_name='dataset.zip'):
    """Download the archive at the given URL and unpack it in the specified
    directory."""
    res = requests.get(archive_url, stream=True)
    print(res)
    # We could use tempfiles if these intermediate files take too much space.
    # However the files could be useful for debugging.
    with open(os.path.join(unpack_dir, archive_name), 'wb') as f:
        for chunk in res.iter_content(chunk_size=IO_CHUNK_SIZE):
            f.write(chunk)
    shutil.unpack_archive(os.path.join(
        unpack_dir, archive_name), extract_dir=unpack_dir)


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
