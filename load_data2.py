# -----------------------------------------------
# --- DATA MAPPING
# -----------------------------------------------
import pandas as pd
import numpy as np
import os
from foostrat_utils import comp_pts, reconfig_res, ret_xl_cols

# get all data file names..
src_dat_path = os.path.join(os.getcwd(), 'src_data', '')
fi_nm = ['src_data/' + f for f in os.listdir(src_dat_path) if f[:13] == 'all-euro-data']

extra_key = pd.DataFrame({'fi_nm':fi_nm})
extra_key['Season'] = extra_key['fi_nm']
extra_key['fi_nm'].str.replace(f[23:32])

# summarise all available column names..
df_cols = ret_xl_cols(file_names=fi_nm, id_col="Div")

# Problem: For the same fields, some columns are defined as HomeTeam and others as HT..
# create a column mapping table by analysing the columns across data
ht_clmn = ['HomeTeam', 'HT']
at_clmn = ['AwayTeam', 'HT']
odds_clmn_h = ['AvgH', 'B365H', 'BWH', 'IWH', 'PSH', 'WHH', 'VCH', 'BbAvH', 'PSCH']
odds_clmn_d = ['AvgD', 'B365D', 'BWD', 'IWD', 'PSD', 'WHD', 'VCD', 'BbAvD', 'PSCD']
odds_clmn_a = ['AvgA', 'B365A', 'BWA', 'IWA', 'PSA', 'WHA', 'VCA', 'BbAvA', 'PSCA']
odds_clmn_b25 = ['BbMx<2.5', 'BbAv<2.5']
odds_clmn_a25 = ['BbMx>2.5', 'BbAv>2.5']

df_cols_un = pd.DataFrame(df_cols.groupby("field")["field"].apply(np.unique))
df_cols_un.shape
df_cols_un.to_clipboard(sep=",")

# major leagues data
# ---


df = pd.DataFrame()
# the key columns can have 2 different symbologies..
# .. add season as key variable
key_cols = ['Season', 'Div', 'Date', 'HomeTeam', 'AwayTeam']
key_cols_map = {'HT': 'HomeTeam', 'AT': 'AwayTeam'}

for f in fi_nm:
    df0 = pd.read_excel(f, sheet_name=None)
    for key, i in df0.items():
        i['Season'] = f[23:32]
        i.shape[0]
        # check which key columns exist and rename if neccessary..
        if sum(s in key_cols for s in i.columns) != len(key_cols):
            i = i.rename(columns=key_cols_map)
        elif i.shape[0] == 0:
            # in case of no data skip to next..
            continue
        else:
        df_lf = pd.melt(i,
                        id_vars=key_cols,
                        var_name='field',
                        value_name='val').dropna()
        df = df.append(df_lf, ignore_index=True, sort=False)
        print(f[23:32] + ' league: ' + i['Div'][0])

df = df.rename(columns={'Season':'season',
                        'Div':'div',
                        'Date':'date',
                        'HomeTeam':'home_team',
                        'AwayTeam':'away_team'})
df.to_pickle('./pro_data/major_leagues.pkl')



