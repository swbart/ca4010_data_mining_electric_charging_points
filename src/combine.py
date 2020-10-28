#!/usr/bin/env python

"""
Module for combining the data from all countries into a single dataset.
Country data must already exist.
"""

import csv
import os.path
import sys

from utils import ensure_dir_exists


def combine_fields_and_rows(filenames):
    # See https://stackoverflow.com/questions/2512386/how-to-merge-200-csv-files-in-python
    header_keys = []
    merged_rows = []

    for filename in filenames:
        with open(filename) as f:
            reader = csv.DictReader(f)
            merged_rows.extend(list(reader))
            header_keys.extend([key for key in reader.fieldnames if key not in header_keys])
    return header_keys, merged_rows


def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print('Usage: python combine.py [dataset save path] [dataset source] [dataset source] ...')
        sys.exit(1)
    save_path = args[0]
    datasets = args[1:]
    print('Combining dataset at {}'.format(os.path.abspath(save_path)))

    # Ensure directory in which to save the dataset exists.
    ensure_dir_exists(os.path.dirname(save_path))

    # TODO: Don't read everything into memory
    # Combine datasets
    header_keys, merged_rows = combine_fields_and_rows(datasets)

    # Write out the final dataset
    with open(save_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=header_keys)
        writer.writeheader()
        writer.writerows(merged_rows)


if __name__ == '__main__':
    main()
