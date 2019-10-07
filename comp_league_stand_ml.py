# -----------------------------------------------
# --- LEAGUE STANDINGS: MAJOR LEAGUES
# -----------------------------------------------
import pandas as pd
import numpy as np
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
df_h = df[['Competition','Date', 'HomeTeam','FTR','FTHG','FTAG']]
df_h.head()
df_h['Season'] = df_h.loc[:,'Date'].str.slice(start=2)
df_h.info()
df_h.loc[:,'Date']










