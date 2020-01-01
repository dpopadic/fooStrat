# -----------------------------------------------
# --- LEAGUE STANDINGS: MAJOR LEAGUES
# -----------------------------------------------
import pandas as pd
import numpy as np
# useful packages: TensorFlow, Theano, PyTorch, Keras, Scikit-Learn, NumPy, SciPy, Pandas, statsmodels

df = pd.read_pickle('pro_data/data_major_leagues.pkl')
df.head()

# extract relevant fields..
df_f = df[(df.field == 'FTR') | (df.field == 'FTHG') | (df.field == 'FTAG')]
df_fw = df_f.pivot_table(index=['season','div','date','home_team','away_team'], columns='field', values='val', aggfunc='sum').reset_index()
df_fw[['season','div','home_team','away_team']] = df_fw[['season','div','home_team','away_team']].astype(str, errors='ignore')


# 1. home team stats..
df_h = df_fw.loc[:,['season','div','date','home_team','FTAG','FTHG','FTR']]
df_h['points'] = df_h['FTR'].apply(lambda x: 3 if x=='H' else (1 if x=='D' else 0))
df_h['res'] = df_h['FTR'].apply(lambda x: 'w' if x=='H' else ('d' if x=='D' else 'l'))
df_h.rename(columns={'home_team': 'team', 'FTAG': 'goals_received', 'FTHG': 'goals_scored'}, inplace=True)
df_h = df_h.drop(['FTR'], axis=1)

# 2. away team stats..
df_a = df_fw.loc[:,['season','div','date','away_team','FTAG','FTHG','FTR']]
df_a['points'] = df_a['FTR'].apply(lambda x: 3 if x=='A' else (1 if x=='D' else 0))
df_a['res'] = df_a['FTR'].apply(lambda x: 'w' if x=='A' else ('d' if x=='D' else 'l'))
df_a.rename(columns={'away_team': 'team', 'FTAG': 'goals_scored', 'FTHG': 'goals_received'}, inplace=True)
df_a = df_a.drop(['FTR'], axis=1)

# 3. consolidate..
dfc = pd.concat([df_h, df_a], axis=0, sort=True)
dfc[['goals_scored','goals_received']] = dfc[['goals_scored','goals_received']].apply(pd.to_numeric, errors='coerce')
dfc_tot_pts = dfc.groupby(by=['div','season','team'])[['points','goals_scored','goals_received']].sum()
dfc_tot_pts = dfc_tot_pts.reset_index()

# 4. number of wins..
df_wdl = dfc.loc[:,['season','div','date','team','res', 'points']]
dfc_agg_wdl = df_wdl.pivot_table(index=['div','season','team'], columns='res', values='points', aggfunc='count').reset_index()

# 5. add number of wins to standings..
dfc_tot_pts = pd.merge(dfc_tot_pts, dfc_agg_wdl, on=['div','season','team'], how='left')

# 6. store standings..
dfc_tot_pts.to_pickle('./pro_data/major_standings.pkl')
# tmp = pd.read_pickle('pro_data/major_standings.pkl')

# show example table..
dfc_tot_pts['div'].unique()
dfc_tot_pts['season'].unique()
tbl_ill = dfc_tot_pts[(dfc_tot_pts['div']=='E0') & (dfc_tot_pts['season']=='2019-2020')]
tbl_ill2 = tbl_ill.sort_values('points', ascending=False)
tbl_ill2['rank'] = np.array(range(1, len(tbl_ill2) + 1))





















