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

CONNECTION_TITLES = [
  'Type 2 (Socket Only)',
  'BS1363 3 Pin 13 Amp',
  'CHAdeMO',
  'Type 1 (J1772)',
  'Tesla (Roadster)',
  'Blue Commando (2P+E)',
  'Type 2 (Tethered Connector)',
  'CCS (Type 2)',
  'Tesla (Model S/X)',
  'Tesla Supercharger',
  'Europlug 2-Pin (CEE 7/16)',
  'SCAME Type 3C (Schneider-Legrand)',
  'CEE 7/5',
  'CEE 7/4 - Schuko - Type F',
  'NEMA 5-20R',
  'CEE 3 Pin',
  'CEE 5 Pin',
  'T13 - SEC1011 ( Swiss domestic 3-pin ) - Type J',
  'Avcon Connector',
  'SCAME Type 3A (Low Power)',
  'Type I (AS 3112)',
  'CCS (Type 1)',
  'Wireless Charging',
  'IEC 60309 5-pin',
  'CEE+ 7 Pin',
  'IEC 60309 3-pin',
  'XLR Plug (4 pin)',
  'Three Phase 5-Pin (AS/NZ 3123)',
]

def connection_title_to_field_name(title):
  if isinstance(title, list):
    return [connection_title_to_field_name(x) for x in title]
  
  # Remove all paranthesis.
  title = title.replace('(', '')
  title = title.replace(')', '')

  # Convert to lower case and split.
  title_split = title.lower().split()

  # Remove any '-' that's by itself. This will turn "A - B" into "A B", but
  # will leave "A-B" as is.
  for i in range(len(title_split) - 1, -1, -1):
    if title_split[i] == '' or title_split[i] == '-':
      title_split.pop(i)
  
  # Join the split title using '_'.
  title = '_'.join(title_split)

  # Append num_connections_ and return.
  return 'num_connections_' + title

def CONNECTION_FIELD_NAMES():
  return connection_title_to_field_name(CONNECTION_TITLES)

AGGREGATED_CONNECTIONS = {}
for field_name in CONNECTION_FIELD_NAMES():
  AGGREGATED_CONNECTIONS[field_name] = 0

FIELD_NAMES = [
  'uuid',
  'operator_id',
  'usage_type_id',
  'country',
  'address',
  'latitude',
  'longitude',
  'num_points',
] + CONNECTION_FIELD_NAMES()

def parse_point(line):
    """
    Parse the JSON string representation of a charging point into a Python
    object.
    """
    return json.loads(line)


def is_european(point):
    """Returns true if the continent code for the given point is Europe."""
    return point['AddressInfo']['Country']['ContinentCode'] == 'EU'

def aggregate_points(point):
  # Aggregate statistics over each point, i.e. number of points with
  # connection type X
  aggr_connections = AGGREGATED_CONNECTIONS.copy()
  for conn in point['Connections']:
    title = conn["ConnectionType"]["Title"].strip()
    if title == "Unknown":
      continue

    title = connection_title_to_field_name(title)
    if title in aggr_connections:
      aggr_connections[title] += 1
    else:
      aggr_connections[title] = 1
  return aggr_connections

def preprocess_point(point):
    """
    Preprocesses/normalizes the point dict into a flat structure
    with only the required fields.
    """
    # TODO: Replace IDs with actual information available at the
    # reference schema
      
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
      **aggregate_points(point),
    }


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        print('Usage: python '+ sys.argv[0] +' [dataset target directory]')
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
