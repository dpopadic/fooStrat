# FACTOR CALCULATION ----------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, odds_fields

# load plain field data..
data_prc = pd.read_pickle('pro_data/data_prc.pkl')
field_all = data_prc['field'].unique()

# goal superiority rating -----------------------------------------------
data_fct = fgoalsup(data_prc, field=['FTHG', 'FTAG'], k=5)
# other approaches: find what kind of bets are the most mispriced
# factors: 3y h2h, last 10 matches in all competitions, average goals, moment of goals
# compute information coefficient (..lagged + odds/payoff required)
data = data_prc
field = list(odds_fields.get('odds_draw_win'))
odds_fields.keys()


# write a function to check whether a field is in all tables and how many times..

# odds decomposition ----------------------------------------------------
# which odds to take for tests?
# get odds in right format.. -> div | date | season | team | field | val

field_asym = dict((k, odds_fields[k]) for k in ['odds_home_win','odds_away_win'] if k in odds_fields)
field_sym = dict((k, odds_fields[k]) for k in ['odds_draw_win'] if k in odds_fields)
data_odds = fodds(data, field_asym = field_asym, field_sym = field_sym)

field_home = list(odds_fields.get('odds_home_win'))
field_away = list(odds_fields.get('odds_away_win'))
field_both = list(odds_fields.get('odds_draw_win'))

def fodds(data, field_home, field_away, field_both):
    """Retrieves the maximum odds for every game and event in an easy to handle
    and scalable long format.

    Parameters:
    -----------
        data (dataframe): a dataframe with columns div, season, date, home_team, away_team, field, val
        field_asym (dict): a dictionary specifying all odds-fields for an asymmetric event (eg. home-team win)
        field_sym (dict): a dictionary specifying all odds-fields for a symmetric event (eg. draw)

    Returns:
    --------
        A dataframe with all processed data is returned with the following columns:
        season | div | date | team | field | val

    """

    moh = max_event_odds_asym(data, field = o_h, team = 'home_team', new_field = 'odds_win')
    moa = max_event_odds_asym(data, field = o_a, team = 'away_team', new_field = 'odds_win')
    mod = max_event_odds_sym(data, field = o_d, new_field = 'odds_draw')
    # bind all together..
    moc = pd.concat([moh, moa, mod], axis=0, sort=False, ignore_index=True)
    return(moc)
    # mod[(mod['date']=='2012-05-19') & (mod['div']=='SP2')].sort_values('val')




# store..
data_fct.to_pickle('./pro_data/data_fct.pkl')

data_fct = pd.read_pickle('pro_data/data_fct.pkl')
# verifying..
# a = data_fct[data_fct['team']=='Liverpool']
# a[a['date']>='2019-08-17']
# looks good comparing to premier league results. next step is to include international
# competitions (eg. champions league) and define it as a function..







