# -----------------------------------------------
# --- LEAGUE STANDINGS: MAJOR LEAGUES
# -----------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import comp_pts, reconfig_res
# useful packages: TensorFlow, Theano, PyTorch, Keras, Scikit-Learn, NumPy, SciPy, Pandas, statsmodels

df = pd.read_pickle('pro_data/major_leagues.pkl')
df.head()
# see all column names..
for col in df.columns:
    print(col)

# mapping leagues..
competition = {'E0':'England Premier League',
               'E1':'England Championship League',
               'E2':'England Football League One',
               'E3':'England Football League Two',
               'EC':'England National League',
               'SC0':'Scottish Premiership',
               'SC1':'Scottish Championship',
               'SC2':'Scottish League One',
               'SC3':'Scottish League Two',
               'D1':'German Bundesliga',
               'D2':'German 2. Bundesliga',
               'SP1':'Spain La Liga',
               'SP2':'Spain Segunda Division',
               'I1':'Italy Serie A',
               'I2':'Italy Serie B',
               'F1':'France Ligue 1',
               'F2':'France Ligue 2',
               'N1':'Dutch Eredivisie ',
               'B1':'Belgian First Division A',
               'P1':'Portugal',
               'T1':'Turkey Süper Lig',
               'G1':'Greek Super League'}
ml_map = pd.DataFrame(list(competition.items()), columns=['Div', 'Competition'])
df = pd.merge(df, ml_map, on=['Div'], how='left')

# 1. home team stats..
df_h = df[['Competition','Season', 'HomeTeam','FTR','FTHG','FTAG']]
df_h.columns = ['Competition','Season', 'Home','Res','Gsco','Grec']
df_h["Res"] = df_h["Res"].apply(reconfig_res, persp='home')
df_h["Points"] = df_h["Res"].apply(comp_pts)
df_h['Team'] = df_h['Home']
del(df_h['Home'])
df_h.head()

# 2. away team stats..
df_a = df[['Competition','Season', 'AwayTeam','FTR','FTHG','FTAG']]
df_a.columns = ['Competition','Season', 'Away','Res','Grec','Gsco']
df_a["Res"] = df_a["Res"].apply(reconfig_res, persp='away')
df_a["Points"] = df_a["Res"].apply(comp_pts)
df_a['Team'] = df_a['Away']
del(df_a['Away'])
df_a.head()

# 3. consolidate..
dfc = pd.concat([df_h, df_a], axis=0, sort=True)
dfc_tot_pts = dfc.groupby(by=['Competition','Season','Team'])[['Points','Gsco','Grec']].sum()
dfc_tot_pts = dfc_tot_pts.reset_index()

# 4. number of wins..
dfc_agg_wdl = dfc.pivot_table(index=['Competition','Season','Team'], columns='Res', values='Gsco', aggfunc='count').reset_index()
del(dfc_agg_wdl[''])

# 5. add number of wins to standings..
dfc_tot_pts = pd.merge(dfc_tot_pts, dfc_agg_wdl, on=['Competition','Season','Team'], how='left')

# 6. store standings..
dfc_tot_pts.to_pickle('./pro_data/major_standings.pkl')

# show example table..
dfc_tot_pts['Competition'].unique()
dfc_tot_pts['Season'].unique()
tbl_ill = dfc_tot_pts[(dfc_tot_pts.Competition=='England Premier League') & (dfc_tot_pts.Season=='2019-2020')]
tbl_ill2 = tbl_ill.sort_values('Points', ascending=False)
tbl_ill2['Rank'] = np.array(range(1, len(tbl_ill2) + 1))



