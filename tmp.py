# -----------------------------------------------
# --- LEAGUE STANDINGS: MAJOR LEAGUES
# -----------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import comp_league_standing

# useful packages: TensorFlow, Theano, PyTorch, Keras, Scikit-Learn, NumPy, SciPy, Pandas, statsmodels

df = pd.read_pickle('pro_data/data_major_leagues.pkl')
df.head()

# extract relevant fields..
df_f = df[(df.field == 'FTR') | (df.field == 'FTHG') | (df.field == 'FTAG')]

# calculate standings..
tbl = comp_league_standing(df_f, season=['2019-2020'])
# store standings..
tbl.to_pickle('./pro_data/major_standings.pkl')
# tmp = pd.read_pickle('pro_data/major_standings.pkl')

# show example table..
tbl.columns
tbl['div'].unique()
tbl['season'].unique()
tbl_ill = tbl[(tbl['div']=='E0') & (tbl['season']=='2019-2020')]
tbl_ill.sort_values('points', ascending=False, inplace=True)





















