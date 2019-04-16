#!/usr/bin/env python3
import csv
import os
import re
import sys
from collections import defaultdict
from contextlib import suppress
from typing import List

import click
import requests as req
import pandas as pd

import nsw2019.urls as urls


def interact():
    import code
    code.InteractiveConsole(locals=globals()).interact()


def mkdir(path):
    with suppress(Exception):
        os.mkdir(path)


def get_vtr():
    return req.get(urls.VTR_JSON).json()['azure']


def tform_party_name(p):
    return re.sub("[^a-zA-Z_]+", "", p.replace(' ', '_'))


def get_district_lookup():
    districts_lookup = {}
    districts_json = req.get(urls.DISTRICTS_JSON).json()
    for d in districts_json:
        d['area_id'] = d['areaId']
        districts_lookup[d['areaId']] = d
    return districts_lookup


def get_district_data(district_doc, vtr_json=None):
    vtr_json = vtr_json if vtr_json is not None else get_vtr()
    _url = urls.gen_region_fp_grp_cand_by_vote_type(**vtr_json, **district_doc)
    print(_url)
    d_html = req.get(_url).content
    tables: List[pd.DataFrame] = pd.read_html(d_html)
    keys = list(tables[0].keys())
    party_totals = []
    global t
    for t in tables:
        group = t.iat[0, 0]
        party_name = tform_party_name(str(t.iat[0, 1]))
        if party_name == "UNGROUPED_CANDIDATES":
            party_name = "TOTAL_VOTES"
            group = "_TOTAL_"
        if party_name == "nan":
            party_name = f"GROUP_{group}"
        # interact()
        # sys.exit(0)
        vals = list(t.values[-1])
        vals[0] = group
        vals[1] = party_name
        party_totals.append(vals)
    return keys, party_totals


@click.group()
def cli():
    pass


@cli.command()
@click.option('--out-dir', default='output', help='directory to output CSVs to')
# @click.option('--aggregate', is_flag=True, default=False, help='aggregate into one big CSV')
def get_fp_by_district(out_dir, aggregate=False):
    fp_dist_dir = os.path.join(out_dir, "fp_by_district")
    fp_party_dist_dir = os.path.join(out_dir, "fp_by_party_by_district")
    list(map(mkdir, [out_dir, fp_dist_dir, fp_party_dist_dir]))

    def write_csv(path, data):
        with open(path, 'w+') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)

    def write_district_csv(d, keys, data):
        write_csv(os.path.join(fp_dist_dir, f"{d}.csv"), [keys] + data)

    def write_party_csv(p, keys, data):
        write_csv(os.path.join(fp_party_dist_dir, f"{p.lower()}.csv"), [keys] + data)

    districts_lookup = get_district_lookup()
    districts = list(districts_lookup.keys())
    vtr_json = get_vtr()

    district_data = {}

    keys = []
    for d in districts:
        keys, district_data[d] = get_district_data(districts_lookup[d], vtr_json)
        write_district_csv(d, keys, district_data[d])
    all_parties = set([str(row[1]) for dd in district_data.values() for row in dd])

    party_keys = ['area_id'] + keys[2:]
    for p in all_parties:
        party_data = [[d] + row[2:] for (d, data) in district_data.items() for row in data if row[1] == p]
        write_party_csv(p, party_keys, party_data)


if __name__ == "__main__":
    cli()
