# FACTOR CALCULATION ----------------------------------------------------
import pandas as pd
import numpy as np

# goal superiority rating -----------------------------------------------
# - hypothesis: Goal difference provides one measure of the dominance of one football side over another in a match. The
# assumption for a goals superiority rating system, then, is that teams who score more goals and concede fewer over
# the course of a number of matches are more likely to win their next game. Typically, recent form means the last 4,
# 5 or 6 matches. For example, In their last 6 games, Tottenham have scored 6 goals and conceded 9. Meanwhile, Leeds
# have scored 8 times and conceded 11 goals. Tottenham's goal superiority rating for the last 6 games is -3; for
# Leeds it is also -3.

# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals

data_prc = pd.read_pickle('pro_data/data_prc.pkl')
data_prc.head()

data_goals = data_prc[(data_prc['field'].isin(['FTAG', 'FTHG']))]
data_goals['val'] = data_goals['val'].apply(pd.to_numeric)
tmp = pd.pivot_table(data_goals, index=['div','season','date','home_team','away_team'], columns='field', values='val').reset_index()

# home team..
tmp1 = tmp[['div','season','date','home_team','FTHG','FTAG']]
tmp1.rename(columns={'home_team':'team', 'FTHG':'g_scored', 'FTAG':'g_received'}, inplace=True)
# away team..
tmp2 = tmp[['div','season','date','away_team','FTHG','FTAG']]
tmp2.rename(columns={'away_team':'team', 'FTAG':'g_scored', 'FTHG':'g_received'}, inplace=True)
# put together..
data_goals_co = pd.concat([tmp1, tmp2], axis=0, sort=False, ignore_index=True)

# compute stat..
data_goals_co_i = data_goals_co.set_index('date')
data_goals_co1 = data_goals_co_i.sort_values('date').groupby(['team'])[['g_scored', 'g_received']].rolling(3, min_periods=1).sum().reset_index()
data_goals_co1['val'] = data_goals_co1['g_scored'] - data_goals_co1['g_received']
data_goals_co1.drop(['g_scored', 'g_received'], axis=1, inplace=True)
data_fct = pd.merge(data_goals_co[['div','date','season','team']], data_goals_co1, on=['team','date'], how='left')
data_fct['field'] = 'goal_superiority'

# store..
data_fct.to_pickle('./pro_data/data_fct.pkl')

# verifying..
# a = data_fct[data_fct['team']=='Tigre']
# b = tmp[(tmp['home_team']=='Tigre') | (tmp['away_team']=='Tigre')]




