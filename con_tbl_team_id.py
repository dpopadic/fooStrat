# -----------------------------------------------
# --- STATIC TEAM ID TABLES
# -----------------------------------------------
# this file usually needs to be executed only once every season..
import pandas as pd
import numpy as np
# tables: teams (team_id, val), fields (team_id, date, field_id, val, league)
# .. write functions for the key tables

# --- niche leagues:
df_n = pd.read_pickle('pro_data/niche_leagues.pkl')
teams_tmp_n = pd.DataFrame(df_n[['Home', 'Away']].melt().value.unique(), columns=['val']).sort_values(by='val')
teams_tmp2_n = pd.DataFrame(np.array(range(1, len(teams_tmp_n)+1)) + 1000, columns=['team_id'])
teams_n = pd.concat([teams_tmp_n, teams_tmp2_n], axis=1)

teams.to_pickle('./pro_data/teams.pkl')
teams.head()
teams.shape

# --- major leagues:
df_m = pd.read_pickle('pro_data/major_leagues.pkl')
teams_tmp_m = pd.DataFrame(df_m[['HomeTeam', 'AwayTeam']].melt().value.unique(), columns=['val']).sort_values(by='val')
teams_tmp2_m = pd.DataFrame(np.array(range(1, len(teams_tmp_m)+1)) + 10000, columns=['team_id'])
teams_m = pd.concat([teams_tmp_m, teams_tmp2_m], axis=1)

# manage double counting..
a = pd.merge(teams_n, teams_m, on=['val'], how='inner')



