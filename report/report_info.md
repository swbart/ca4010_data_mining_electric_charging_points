# Report

## Idea and dataset description

Given the increase in electric vehicles over the years, we want to collect a dataset of all the electric charging points across Europe.

## Data preparation

To make collaboration and versioning easy we have decided to use Git/GitHub.

However, we will not track the datasets themselves in Git, as the datasets are very large and tracking them will be inefficient.

We will create programmatic utilities to download and prepare the datasets in order to make the dataset collection easily reproducible. We will use Python due its platform independence. We could have also used shell/batch scripts however these are dependent on Unix/Windows. We will use shell scripts for simple tasks, but we should provide both a shell and a batch script.

We will use the CSV format, a very popular human and machine readable format for datasets.

### Ireland

The primary source of data is ESB's maintained map of all (its own or other company) charging points at https://esb.ie/ecars/charge-point-map.

We have found this article http://www.mlopt.com/?p=6598 that describes datasets of Irish charging points at historic times published at http://www.cpinfo.ie/data/archive.html. There also exists http://www.cpinfo.ie/ for real time queries of specific charging points.

The repo at https://github.com/slimtomatillo/irish_EV_charger_status utilises the dataset above and could be of use to us.

For first iteration we have decided to use the most recent data at cpinfo.ie, downloading the 2019 July archive. This brings the problem of getting the most recent as opposed to historic data. In future iterations we could build our own bot for the ESB map for scraping the most recent data. We could probably also mine extra data such as the provider of the electric charging point (ESB or other).

Since the datasets can be considerable in size, we should do as much line-oriented processing as possible, avoiding reading entire datasets into memory.

While processing the precompiled dataset at cpinfo we have come across the issue of the dataset being incredibly large (over 200 MB). This made it hard to check the dataset in a text editor (the data kept loading). It took some time to figure out that the dataset actually contained multiple data points for a single electric charging point. The data points were taken at different points in time (since the dataset was for analysing statuses of charging points). To solve this problem we read every line and took only the most recent data point (last in the dataset).

#### Validation

There also exists https://data.gov.ie/dataset/ev-charge-points, which is a government dataset of all charging points in Cork for July 2018. We can compare our final Irish dataset against this "sub" dataset to ensure there is consistency (within historic limits).

### France

France has some datasets at https://www.data.gouv.fr/en/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/ and https://github.com/etalab/notebooks/blob/master/irve/irve.ipynb

### All European countries

After further research we have discovered that there exist global maps that list the charging points at any part of the globe!
This simplified our job significantly. Instead of having to scrape every European country by ourselves, we can just scrape one of the
exchaustive world maps for European data.

One such map is https://openchargemap.org. It is a public initiative that transparently collects the data of charging points from all over the world.
We can use the repo at https://github.com/openchargemap/ocm-data for recent data snapshots.

### Overall validation

We can use various aggregated statistics that indicate how many charging points are there per countries in Europe, such as https://ec.europa.eu/transport/facts-fundings/scoreboard/compare/energy-union-innovation/ev-charging-points_en (2017 estimate). Each country's dataset should have the approximate number of charging points indicated.

## Algorithm description

## Results and analysis
