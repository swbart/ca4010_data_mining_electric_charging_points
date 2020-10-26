#!/usr/bin/env python

from itertools import zip_longest
from pathlib import Path


def ensure_dir_exists(directory):
    Path(directory).mkdir(parents=True, exist_ok=True)


def grouper(n, iterable, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks without reading everything into memory.
    See https://stackoverflow.com/questions/16289859/splitting-large-text-file-into-smaller-text-files-by-line-numbers-using-python
    """
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)
