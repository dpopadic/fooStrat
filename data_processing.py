# DATA LOADING ----------------------------------------------------
import pandas as pd
import numpy as np
import os
from foostrat_utils import ret_xl_cols, process_data_major

# source data path..
src_dat_path = os.path.join(os.getcwd(), 'src_data', '')

# major leagues ---------------------------------------------------
# get all data file names..
fi_nm = ['src_data/' + f for f in os.listdir(src_dat_path) if f[:13] == 'all-euro-data']
# map seasons..
extra_key = pd.DataFrame({'fi_nm':fi_nm, 'season':[i[23:32] for i in fi_nm]})
# process data..
df = process_data_major(fi_nm, extra_key,
                        key_cols = {'Div': 'div', 'Date': 'date', 'HomeTeam': 'home_team', 'AwayTeam': 'away_team'},
                        key_cols_map = {'HT': 'HomeTeam', 'AT': 'AwayTeam'})
df.to_pickle('./pro_data/data_major_leagues.pkl')
# df = pd.read_pickle('./pro_data/data_major_leagues.pkl')
# parameter: season or fi_nm
# fi_nm = fi_nm[1:3]

# niche leagues ---------------------------------------------------
# data file..
data = pd.read_excel('src_data/new_leagues_data.xlsx', sheet_name=None)
# process data..
df2 = process_data_minor(data,
                         key_cols = {'Country':'country',
                                     'League':'league',
                                     'Date':'date',
                                     'Season':'season',
                                     'Home':'home_team',
                                     'Away': 'away_team'})


# put together ----------------------------------------------------
data_prc = pd.concat([df2, df], axis=0, sort=False)
data_prc.to_pickle('./pro_data/data_prc.pkl')












