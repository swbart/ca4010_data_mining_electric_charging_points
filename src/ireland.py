#!/usr/bin/env python

"""Scraper for Republic of Ireland."""

import os.path
import sys

import common
from utils import download_archive, ensure_dir_exists, export_csv


DATASET_URL = 'http://www.cpinfo.ie/data/201907a.zip'
DATASET_NAME = '201907a.txt'

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


def preprocess(line):
    """
    Transform the given raw line into a structure suitable for our dataset.

    A line is a string with the following tab-separated parts:
        Date (yyyymmdd),
        Time (hhmm),
        Charge Point Id,
        Charge Point Type {StandardType2, CHAdeMO, CCS, FastAC},
        Status {OOS | Out of Service, OOC | Out of Contact, Part |
                Partially Occupied, Occ | Fully Occupied, Unknown | Unknown},
        Coordinates,
        Address,
        Longitude,
        Latitude

    The following fields will be used:
        Charge Point Id, Charge Point Type, Status, Address, Longitude,
        Latitude.

    The output is a dict mapping from field name to value.
    """
    try:
        (date, time, charge_point_id, charge_point_type, status, coordinates,
         address, longitude, latitude) = line.strip().split('\t')
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
    download_archive(DATASET_URL, save_dir)
    input_path = os.path.join(save_dir, DATASET_NAME)

    # Read all latest data points into a dict (memory heavy)
    # Replace incorrect characters with ? as the dataset has UTF-8 problems
    d = {}
    with open(input_path, errors='replace') as f:
        for line in f:
            # Dataset orders points from earliest to latest
            try:
                data_point = preprocess(line)
                # Take latest point as canon
                d[data_point['charge_point_id']] = data_point
            except Exception as exc:
                print('Exception processing line {} (preprocessed as {}): {}'
                      .format(line, data_point, exc))

    # Export the processed data points
    out_path = os.path.join(save_dir, '{}.{}'.format(EXPORT_DATASET_NAME,
                                                     EXPORT_DATASET_EXT))
    export_csv(out_path, FIELD_NAMES, d.values())


if __name__ == '__main__':
    main()
