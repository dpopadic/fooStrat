# -----------------------------------------------
# --- STATIC ID TABLES
# -----------------------------------------------
import pandas as pd
import numpy as np
df = pd.read_pickle('pro_data/niche_leagues.pkl')
# tables: teams (team_id, val), fields (team_id, date, field_id, val, league)
# .. write functions for the key tables

# --- teams-id table
teams_tmp = pd.DataFrame(df[['Home', 'Away']].melt().value.unique(), columns=['val']).sort_values(by='val')
teams_tmp2 = pd.DataFrame(np.array(range(1, len(teams_tmp)+1)) + 1000, columns=['team_id'])
teams = pd.concat([teams_tmp, teams_tmp2], axis=1)
teams.to_pickle('./pro_data/teams.pkl')
teams.head()
teams.shape

