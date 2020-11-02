#!/usr/bin/env python

"""
Dataset processor based on OpenChargeMap (https://openchargemap.org).

Credits go to the Open Charge Map developers, contributors, and data providers.
"""

import json
import os.path
import sys

import common
from utils import download_archive, ensure_dir_exists, export_csv


# Latest dump of the OpenChargeMap database
DATASET_URL = 'https://github.com/openchargemap/ocm-data/blob/master/poi.json.gz?raw=true'
DATASET_ARCHIVE = 'poi.json.gz'
DATASET_NAME = 'poi.json'

# Reference schema for the OpenChargeMap dump
DATASET_REFERENCE_SCHEMA_URL = 'https://raw.githubusercontent.com/openchargemap/ocm-data/master/reference.json'
DATASET_REFERENCE_SCHEMA = 'reference.json'

EXPORT_DATASET_NAME = 'openchargemap.csv'

FIELD_NAMES = [
  'uuid',
  'operator_id',
  'usage_type_id',
  'country',
  'address',
  'latitude',
  'longitude',
  'num_points',
]


def parse_point(line):
    """
    Parse the JSON string representation of a charging point into a Python
    object.
    """
    return json.loads(line)


def is_european(point):
    """Returns true if the continent code for the given point is Europe."""
    return point['AddressInfo']['Country']['ContinentCode'] == 'EU'


def preprocess_point(point):
    """
    Preprocesses/normalizes the point dict into a flat structure
    with only the required fields.
    """
    # TODO: Replace IDs with actual information available at the
    # reference schema
    # TODO: Aggregate statistics over each point, i.e. number of points with
    # connection type X
    return {
      'uuid': point['UUID'],
      'operator_id': point['OperatorID'],
      'usage_type_id': point['UsageTypeID'],
      'country': point['AddressInfo']['Country']['Title'],
      'address': ', '.join(filter(lambda item: item is not None, [
        point['AddressInfo']['Title'],
        point['AddressInfo']['AddressLine1'],
        point['AddressInfo']['AddressLine2'],
        point['AddressInfo']['Town'],
      ])),
      'latitude': point['AddressInfo']['Latitude'],
      'longitude': point['AddressInfo']['Longitude'],
      'num_points': point['NumberOfPoints'],
    }


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print('Usage: python ireland.py [dataset target directory]')
        sys.exit(1)
    save_dir = args[0]
    print('Processing dataset at {}'.format(os.path.abspath(save_dir)))

    ensure_dir_exists(save_dir)

    download_archive(DATASET_URL, save_dir, DATASET_ARCHIVE)
    input_path = os.path.join(save_dir, DATASET_NAME)

    with open(input_path) as f:
        # map and filter return iterables that are processed one by one
        # instead of all being read into memory.
        # Keep the file open for the duration of all operations or we will
        # get "closed file" errors.

        points = map(parse_point, f)
        # TODO: Validate the parsed JSON against the reference schema at https://github.com/openchargemap/ocm-data/blob/master/reference.json
        europe_points = filter(is_european, points)
        preprocessed_points = map(preprocess_point, europe_points)

        out_path = os.path.join(save_dir, EXPORT_DATASET_NAME)
        export_csv(out_path, FIELD_NAMES, preprocessed_points)


if __name__ == '__main__':
    main()
