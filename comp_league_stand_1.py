# -----------------------------------------------
# --- DATA PROCESSING & BASIC STATISTICS
# -----------------------------------------------
import pandas as pd
import numpy as np
df = pd.read_pickle('pro_data/niche_leagues.pkl')
# df = pd.read_pickle('pro_data/major_leagues.pkl')

# id: team, league, date
# factor families: team x (# wins, momentum ..), game (opponent, home-away, odds ..)

# --- league standings tables
# target: season, league, team, rank, points, gs, gr, l5
# create col of unique leagues..
df['Competition'] = df['Country'] + ' ' + df['League']

# 1. home team stats..
df_h = df[['Competition','Season', 'Home','Res','HG','AG']]
df_h.columns = ['Competition','Season', 'Home','Res','Gsco','Grec']
df_h["Res"] = df_h["Res"].apply(reconfig_res, persp='home')
# df_nar['Res2'] = df_nar['Res'].fillna('N')
# df_nar["Res2"].unique()
df_h["Points"] = df_h["Res"].apply(comp_pts)
df_h['Team'] = df_h['Home']
del(df_h['Home'])

# 2. away team stats..
df_a = df[['Competition','Season', 'Away','Res','HG','AG']]
df_a.columns = ['Competition','Season', 'Away','Res','Grec','Gsco']
df_a["Res"] = df_a["Res"].apply(reconfig_res, persp='away')
df_a["Points"] = df_a["Res"].apply(comp_pts)
df_a['Team'] = df_a['Away']
del(df_a['Away'])

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
dfc_tot_pts.to_pickle('./pro_data/niche_standings.pkl')


# show example table..
dfc_tot_pts['Competition'].unique()
tbl_ill = dfc_tot_pts[(dfc_tot_pts.Competition=='Switzerland Super League') & (dfc_tot_pts.Season=='2018/2019')]
tbl_ill2 = tbl_ill.sort_values('Points', ascending=False)
tbl_ill2['Rank'] = np.array(range(1, len(tbl_ill2) + 1))















