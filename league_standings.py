# ----------------------------------------------------
# --- LEAGUE STANDINGS
# ----------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import comp_league_standing

# read source data..
df = pd.read_pickle('pro_data/source_core.pkl')
# filter relevant fields & calculate standings..
df_f = df[(df.field == 'FTR') | (df.field == 'FTHG') | (df.field == 'FTAG')]
tbl = comp_league_standing(df_f, home_goals='FTHG', away_goals='FTAG', result='FTR')
# tbl = comp_league_standing(df_f, season=['2019-2020'])
# store standings..
tbl.to_pickle('./pro_data/league_standings.pkl')
# tbl.query('div=="E0" & season=="2019-2020"').sort_values(["points"], ascending=False)
























