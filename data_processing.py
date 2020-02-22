# ----------------------------------------------------
# --- DATA PROCESSING
# ----------------------------------------------------
# This script reads the necessary data files and processes them into the right shape. As of now,
# two different data source formats are handled: major leagues, minor leagues
import pandas as pd
import numpy as np
import os
from foostrat_utils import update_data_latest, update_data_historic

# history update ------------------------------------------------------
update_data_historic(path='src_data/',
                     file_desc='all-euro-data',
                     file_key=[23, 32],
                     file_key_name='season',
                     file_desc_2='new_leagues_data.xlsx',
                     file_key_name_2='Season')


# latest update ------------------------------------------------------
# read existing
source_core = pd.read_pickle('pro_data/source_core.pkl')
# update data
update_data_latest(ex=source_core,
                   new_1='latest_results_major.xlsx',
                   new_2='latest_results_minor.xlsx',
                   season='2019-2020',
                   path='src_data/')












