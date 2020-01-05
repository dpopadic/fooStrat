# ----------------------------------------------------
# --- LEAGUE STANDINGS
# ----------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import comp_league_standing
# useful packages: TensorFlow, Theano, PyTorch, Keras, Scikit-Learn, NumPy, SciPy, Pandas, statsmodels

df = pd.read_pickle('pro_data/data_prc.pkl')
df.head()

# calculate standings..
df_f = df[(df.field == 'FTR') | (df.field == 'FTHG') | (df.field == 'FTAG')]
tbl = comp_league_standing(df_f, home_goals='FTHG', away_goals='FTAG', result='FTR')
# tbl = comp_league_standing(df_f, season=['2019-2020'])

# store standings..
tbl.to_pickle('./pro_data/league_standings.pkl')

# show example table..
tbl.columns
tbl['div'].unique()
tbl['season'].unique()
tbl_ill = tbl[(tbl['div']=='Argentina Superliga') & (tbl['season']=='2017/2018')]
tbl_ill.sort_values('points', ascending=False, inplace=True)





















