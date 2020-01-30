# FACTOR CALCULATION ----------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, odds_home

# load plain field data..
data_prc = pd.read_pickle('pro_data/data_prc.pkl')
f = data_prc['field'].unique()

# goal superiority rating -----------------------------------------------
data_fct = fgoalsup(data_prc, field=['FTHG', 'FTAG'], k=5)
# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals
# compute information coefficient (..lagged + odds/payoff required)
data = data_prc
field = list(odds_home.keys())

# write a function to check whether a field is in all tables and how many times..

# which odds to take for tests?
# get odds in right format.. -> div | date | season | team | field | val
def fodds(data, field, k):
    """Calculates the goal superiority factor across divisions and seasons for each team on a
    rolling basis.

    Parameters:
    -----------
        data (dataframe): a dataframe with columns div, date, season, home_team, away_team, field, val
        field (list): a list specifying the field name for home- & away-goals (eg. ['FTHG', 'FTAG'])
        k (integer): the lookback window to be used

    Returns:
    --------
        A dataframe with calculated goal-superiority factor and columns div, season, date, team, field, val

    Details:
    --------
    Goal difference provides one measure of the dominance of one football side over another in a match. The
    assumption for a goals superiority rating system, then, is that teams who score more goals and concede fewer over
    the course of a number of matches are more likely to win their next game. Typically, recent form means the last 4,
    5 or 6 matches. For example, In their last 6 games, Tottenham have scored 6 goals and conceded 9. Meanwhile, Leeds
    have scored 8 times and conceded 11 goals. Tottenham's goal superiority rating for the last 6 games is +3; for
    Leeds it is -3.

    """
    # filter relevant fields..
    data_ed = data[(data['field'].isin(field))]
    data_ed['val'] = data_ed.loc[:, 'val'].apply(pd.to_numeric)
    data_ed.groupy(['div','season','date','home_team'])










# store..
data_fct.to_pickle('./pro_data/data_fct.pkl')

data_fct = pd.read_pickle('pro_data/data_fct.pkl')
# verifying..
# a = data_fct[data_fct['team']=='Liverpool']
# a[a['date']>='2019-08-17']
# looks good comparing to premier league results. next step is to include international
# competitions (eg. champions league) and define it as a function..







