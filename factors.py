import pandas as pd
# --- goal superiority rating
# - hypothesis: Goal difference provides one measure of the dominance of one football side over another in a match. The
# assumption for a goals superiority rating system, then, is that teams who score more goals and concede fewer over
# the course of a number of matches are more likely to win their next game. Typically, recent form means the last 4,
# 5 or 6 matches. For example, In their last 6 games, Tottenham have scored 6 goals and conceded 9. Meanwhile, Leeds
# have scored 8 times and conceded 11 goals. Tottenham's goal superiority rating for the last 6 games is -3; for
# Leeds it is also -3.

# other approaches: find what kind of bets are the most mispriced

df_stand = pd.read_pickle('pro_data/major_standings.pkl')
df_stand.head()


df = pd.read_pickle('pro_data/major_leagues.pkl')
# home..
dfh = df.loc[:,['Div','Date','HomeTeam','FTHG','FTAG']]
dfh['Home'] = True
dfh = dfh.rename(columns={'HomeTeam':'Team',  'FTHG':'Gsco', 'FTAG':'Grec'})
# away..
dfa = df.loc[:,['Div','Date','AwayTeam','FTHG','FTAG']]
dfa['Home'] = False
dfa = dfa.rename(columns={'AwayTeam':'Team', 'FTHG':'Grec', 'FTAG':'Gsco'})
# consolidated..
df_con = pd.concat([dfh, dfa], axis=0).sort_values(by='Date', ascending=False)
# compute factor..
df_con = df_con.dropna()
df_gsr = df_con.sort_values('Date').groupby(by=['Div','Team'])['Gsco','Grec'].rolling(3, min_periods=1).sum().reset_index()

df_con.dtypes
df_gsr.dtypes
df_gsr.describe()
a = df_con.loc[:,['Gsco','Grec']].rolling(3).sum()








