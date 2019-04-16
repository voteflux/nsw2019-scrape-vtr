import time


# vtr_json needs to be pulled first for many calls
from typing import NamedTuple


def gen_vtr_json():
    return f"https://vtr.elections.nsw.gov.au/vtr.json?_={time.time() * 1000 // 1}"


# Constant URLs
VTR_JSON = gen_vtr_json()
DISTRICTS_JSON = "https://vtr.elections.nsw.gov.au/districts.json"


# URLs needing generation
def gen_region_fp_grp_cand_by_vote_type(id='', type='', share='', area_id='', storage='', **kwargs):
    """keys: id, type, share, area_id, storage, time_micro"""
    return ("https://{id}.{type}.core.windows.net/{share}/lc/{area_id}" +
            "/dop/fp_by_grp_and_candidate_by_vote_type_report.html{storage}")\
        .format(id=id, type=type, share=share, area_id=area_id, storage=storage)
