#!/usr/bin/env python

import csv
import os.path
import shutil
import sys

import requests
import requests_cache

from utils import ensure_dir_exists


DATASET_URL = 'http://www.cpinfo.ie/data/201907a.zip'
DATASET_NAME = '201907a.txt'

CHUNK_SIZE = 128

# Maximum lines that should be included in a single final dataset instance.
MAX_EXPORT_DATASET_LINES = 30000
EXPORT_DATASET_NAME = 'ireland'
EXPORT_DATASET_EXT = 'csv'

FIELD_NAMES = [
  'charge_point_id',
  'charge_point_type',
  'status',
  'address',
  'longitude',
  'latitude'
]


# All responses will be cached to a sqlite database.
# By default requests doesn't do caching.
# Moreover some dataset servers don't support caching.
# Thus we build our own cache locally.
# Delete the cache if you want to redownload everything.
requests_cache.install_cache('cache')


def download(save_dir):
    res = requests.get(DATASET_URL, stream=True)
    print(res)
    # We could use tempfiles if these intermediate files take too much space.
    # However the files could be useful for debugging.
    with open(os.path.join(save_dir, 'dataset.zip'), 'wb') as f:
        for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)
    shutil.unpack_archive(os.path.join(
        save_dir, 'dataset.zip'), extract_dir=save_dir)


def preprocess(line):
    """
    Preprocess lines in dataset, line-by-line.

    Each line in the dataset has the following tab-separated parts:
    Date (yyyymmdd),
    Time (hhmm),
    Charge Point Id,
    Charge Point Type {StandardType2, CHAdeMO, CCS, FastAC},
    Status {OOS | Out of Service, OOC | Out of Contact, Part | Partially Occupied, Occ | Fully Occupied, Unknown | Unknown},
    Coordinates,
    Address,
    Longitude,
    Latitude

    The following fields will be used: Charge Point Id, Charge Point Type, Status, Address, Longitude, Latitude.
    """
    try:
        date, time, charge_point_id, charge_point_type, status, coordinates, address, longitude, latitude = line.strip().split('\t')
        return {
            "charge_point_id": charge_point_id,
            "charge_point_type": charge_point_type,
            "status": status,
            "address": address,
            "longitude": longitude,
            "latitude": latitude
        }
    except Exception as exc:
        print('Error processing {}: {}'.format(line, exc))
        return {k: None for k in FIELD_NAMES}


def export(save_path, lines):
    with open(save_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
        writer.writeheader()
        writer.writerows(lines)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print('Usage: python ireland.py [dataset target directory]')
        sys.exit(1)
    save_dir = args[0]
    print('Processing dataset at {}'.format(os.path.abspath(save_dir)))

    # Create target directory with all parents if it doesn't exist
    ensure_dir_exists(save_dir)

    # Download dataset and extract it
    download(save_dir)
    input_path = os.path.join(save_dir, DATASET_NAME)

    # Read all latest data points into a dict (memory heavy)
    # Replace incorrect characters with ? as the dataset has some UTF-8 problems
    d = {}
    with open(input_path, errors='replace') as f:
        for line in f:
            # Dataset orders points from earliest to latest
            try:
                data_point = preprocess(line)
                # Take latest point as canon
                d[data_point['charge_point_id']] = data_point
            except Exception as exc:
                print('Exception processing line {} (preprocessed as {}): {}'.format(line, data_point, exc))
    out_path = os.path.join(save_dir, '{}.{}'.format(EXPORT_DATASET_NAME, EXPORT_DATASET_EXT))
    with open(out_path, 'w'):
        export(out_path, d.values())


if __name__ == '__main__':
    main()
