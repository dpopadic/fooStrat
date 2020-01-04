# DATA LOADING ----------------------------------------------------
import pandas as pd
import numpy as np
import os
from foostrat_utils import ret_xl_cols

# source data path..
src_dat_path = os.path.join(os.getcwd(), 'src_data', '')

# major leagues ---------------------------------------------------
# get all data file names..
fi_nm = ['src_data/' + f for f in os.listdir(src_dat_path) if f[:13] == 'all-euro-data']
# map seasons..
extra_key = pd.DataFrame({'fi_nm':fi_nm, 'season':[i[23:32] for i in fi_nm]})
# process data..
df = process_data_major(fi_nm, extra_key)
df.to_pickle('./pro_data/data_major_leagues.pkl')


# parameter: season or fi_nm
# fi_nm = fi_nm[1:3]

# niche leagues ---------------------------------------------------
# data file..
di = pd.read_excel('src_data/new_leagues_data.xlsx', sheet_name=None)
# add season as additional key variable..
key_cols = ['Country', 'League', 'Season', 'Date', 'Home', 'Away']
# i = pd.read_excel('src_data/new_leagues_data.xlsx', sheet_name='BRA')

df = pd.DataFrame()
for key, i in di.items():
    if i.shape[0] == 0:
        # in case of no data skip to next..
        continue
    else:
        df_lf = pd.melt(i,
                        id_vars=key_cols,
                        var_name='field',
                        value_name='val').dropna()
        df = df.append(df_lf, ignore_index=True, sort=False)
        print(i['Country'][0])

# transform to appropriate shape..
df['div'] = df['Country'] + ' ' + df['League']
del(df['Country'])
del(df['League'])
df = df.rename(columns={'Date':'date',
                        'Season':'season',
                        'Home':'home_team',
                        'Away':'away_team'})
df.to_pickle('./pro_data/data_niche_leagues.pkl')












