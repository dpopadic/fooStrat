import pandas as pd
import numpy as np

df = pd.read_pickle('pro_data/niche_leagues.pkl')

# id: team, league, date
# factor families: team x (# wins, momentum ..), game (opponent, home-away, odds ..)
#
# tables: teams (team_id, val), fields (team_id, date, field_id, val, league)
# .. write functions for the key tables

# teams..
teams_tmp = pd.DataFrame(df[['Home', 'Away']].melt().value.unique(), columns=['val']).sort_values(by='val')
teams_tmp2 = pd.DataFrame(np.array(range(1, len(teams_tmp)+1)) + 1000, columns=['team_id'])
teams = pd.concat([teams_tmp, teams_tmp2], axis=1)
teams.to_pickle('./pro_data/teams.pkl')
teams.head()
teams.shape

# league tables..
# target: season, league, team, rank, points, gs, gr
# create col of unique leagues..
df['Competition'] = df['Country'] + ' ' + df['League']

# home team stats..
df_h = df[['Competition','Season', 'Home','Res','HG','AG']]
# df_nar['Res2'] = df_nar['Res'].fillna('N')
# df_nar["Res2"].unique()
df_h["Points"] = df_h["Res"].apply(comp_pts)
df_h['Team'] = df_h['Home']
del(df_h['Home'])

# away team stats..
df_a = df[['Competition','Season', 'Away','Res','HG','AG']]
df_a["Points"] = df_a["Res"].apply(comp_pts)
df_a['Team'] = df_a['Away']
del(df_a['Away'])

# consolidate..
df_ha = df_h.groupby(by=['Competition','Season','Team'])['Points'].sum()

df_ha2 = df_ha.unstack(level='Season')

df_ha.keys()







