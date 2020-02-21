# ----------------------------------------------------
# --- DATA PROCESSING
# ----------------------------------------------------
import pandas as pd
import numpy as np
import os
from foostrat_utils import ret_xl_cols, process_data_major, process_data_minor

# source data path..
src_dat_path = os.path.join(os.getcwd(), 'src_data', '')

# major leagues ---------------------------------------------------
# get all data file names..
fi_nm = ['src_data/' + f for f in os.listdir(src_dat_path) if f[:13] == 'all-euro-data']
# map seasons..
extra_key = pd.DataFrame({'fi_nm': fi_nm, 'season': [i[23:32] for i in fi_nm]})
# process data..
df = process_data_major(fi_nm, extra_key,
                        key_cols={'Div': 'div', 'Date': 'date', 'HomeTeam': 'home_team', 'AwayTeam': 'away_team'},
                        key_cols_map={'HT': 'HomeTeam', 'AT': 'AwayTeam'})
# df.to_pickle('./pro_data/data_major_leagues.pkl')
# df = pd.read_pickle('./pro_data/data_major_leagues.pkl')
# parameter: season or fi_nm
# fi_nm = fi_nm[1:3]

# minor leagues ---------------------------------------------------
# data file..
data = pd.read_excel('src_data/new_leagues_data.xlsx', sheet_name=None)
# process data..
df2 = process_data_minor(data,
                         key_cols={'Country': 'country',
                                     'League': 'league',
                                     'Date': 'date',
                                     'Season': 'season',
                                     'Home': 'home_team',
                                     'Away': 'away_team'})


# put together and store ------------------------------------------
data_prc = pd.concat([df2, df], axis=0, sort=False)

# data synchronisation: renaming fields so that they have the same names to make it easier to process the data later in
# a concise way.
# data_prc = pd.read_pickle('pro_data/data_prc.pkl')

# full-time home/away goals, results
data_prc['field'] = data_prc['field'].replace({'FTR': 'FTR', 'Res': 'FTR',
                                               'FTHG': 'FTHG', 'HG': 'FTHG',
                                               'FTAG': 'FTAG', 'AG': 'FTAG'})

source_core = data_prc
source_core.to_pickle('./pro_data/source_core.pkl')












