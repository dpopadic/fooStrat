# DATA LOADING ----------------------------------------------------
import pandas as pd
import numpy as np
import os
from foostrat_utils import ret_xl_cols

# major leagues ---------------------------------------------------
# get all data file names..
src_dat_path = os.path.join(os.getcwd(), 'src_data', '')
fi_nm = ['src_data/' + f for f in os.listdir(src_dat_path) if f[:13] == 'all-euro-data']

# map seasons..
extra_key = pd.DataFrame({'fi_nm':fi_nm})
extra_key['season'] = extra_key['fi_nm'].str.slice(23, 32)

# add season as additional key variable..
key_cols = ['season', 'Div', 'Date', 'HomeTeam', 'AwayTeam']
# the key columns can have 2 different symbologies..
key_cols_map = {'HT': 'HomeTeam', 'AT': 'AwayTeam'}
df = pd.DataFrame()
for f in fi_nm:
    df0 = pd.read_excel(f, sheet_name=None)
    for key, i in df0.items():
        si = extra_key[extra_key['fi_nm'] == f].iloc[0, 1]
        i['season'] = si
        if i.shape[0] == 0:
            continue
        else:
            if sum(s in key_cols for s in i.columns) != len(key_cols):
                i = i.rename(columns=key_cols_map)
            else:
                df_lf = pd.melt(i,
                                id_vars=key_cols,
                                var_name='field',
                                value_name='val').dropna()
                df = df.append(df_lf, ignore_index=True, sort=False)
        print(si + ' league: ' + i['Div'][0])

# rename columns to lower case..
df = df.rename(columns={'Div':'div',
                        'Date':'date',
                        'HomeTeam':'home_team',
                        'AwayTeam':'away_team'})
df.to_pickle('./pro_data/data_major_leagues.pkl')



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












