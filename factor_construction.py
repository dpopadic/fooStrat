# FACTOR CALCULATION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, fhome, fform, odds_fields, fodds, expand_field, comp_score, update_flib, norm_factor

# load source data..
source_core = pd.read_pickle('pro_data/source_core.pkl')
league_standings = pd.read_pickle('pro_data/league_standings.pkl')

# FACTOR LIBRARY ------------------------------------------------------------------------------------------------------
# note: all factors should be z-scores so it's easy to construct a composite signal if needed
# next factors: points difference, last 3 games points, autocorrelation of outcomes by team,
# head to head, chances (shots, wood hits, corner), volatility of odds (the bigger the better),
# cheap (value, this might be implement at a later stage), game importance (top, bottom), clean sheets (no goal),
# home-away strength, home-away, minutes per
# goal scored, corners, possesion, shots, avg goals per match (scoring rate), league position, failed to score %,
# points per game, scored both halves, conceded/won both halves, lost to nil, losing half-time & winning/draw full-time,
# form (last 5), league

# modelling:
# - explanatory variables:  factor library for a given competition
# - target variable:        win-draw-lose, >/< 2.5 goals, btts
# .. this means there're 3 models for each competition
# .. walk-forward model validation with 3 year initial window

# it's important to do it by league 1st because of data issues that can be present (see Japan J1 League & kobe team)
# see project factor library build-out fore more info on github

# odds retrieval ------------------------------------------------------------------------------------------------------
# store relevant odds
match_odds = fodds(data=source_core,
                   field_home=list(odds_fields.get('odds_home_win')),
                   field_away=list(odds_fields.get('odds_away_win')),
                   field_both=list(odds_fields.get('odds_draw_win')))
match_odds.to_pickle('./pro_data/match_odds.pkl')


# goal superiority rating ---------------------------------------------------------------------------------------------
gsf = fgoalsup(data=source_core, field=['FTHG', 'FTAG'], field_name=['g_scored', 'g_received'], k=3)
gsf = norm_factor(data=gsf)


# form ----------------------------------------------------------------------------------------------------------------
fh = fform(data=source_core, field="FTR", type="home")
fh = norm_factor(data=fh)

fa = fform(data=source_core, field="FTR", type="away")
fa = norm_factor(data=fa)

ftot = fform(data=source_core, field="FTR", type="all")
ftot = norm_factor(data=ftot)

# home factor ---------------------------------------------------------------------------------------------------------
# no need for expansion for boolean factors!
hf = fhome(data=source_core)


# consistence ---------------------------------------------------------------------------------------------------------

data = source_core
field = ['FTHG', 'FTAG']
field_name = ['g_scored', 'g_received']
k = 5
def fconsistency(data, field, field_name, k):
    """Compute consistency factor. The consistency factor is determined by the three features:
        1. average goals scored
        2. % of games failed to score
        3. average points per game
    These statistics are calculated over the last 5 games for each team.

    Parameters:
    -----------
    data:       pandas dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val
    field:      list
                a list specifying the field name for home- & away-goals (eg. ['FTHG', 'FTAG']) in this order
    field_name: list
                a list with new field name for fields (eg. ['g_scored', 'g_received'])
    k:          integer
                the lookback window to be used

    """
    # neutralise data..
    data_goals_co = neutralise_field(data,
                                     field=field,
                                     field_name=field_name,
                                     field_numeric=True,
                                     column_field=True)

    # compute stat..
    data_goals_co_i = data_goals_co.set_index('date')
    # feature 1 - average goals per game (last 5)
    data_goals_co1 = data_goals_co_i.sort_values('date').groupby(['team'])[field_name]. \
        rolling(k, min_periods=1).mean().reset_index()

    data_goals_co1['val'] = data_goals_co1[field_name[0]]
    data_goals_co1.drop(field_name, axis=1, inplace=True)
    data_fct = pd.merge(data_goals_co[['div', 'date', 'season', 'team']],
                        data_goals_co1, on=['team', 'date'],
                        how='left')
    data_fct['field'] = 'avg_goal_scored'
    # lag factor..
    data_fct.sort_values(['team', 'date'], inplace=True)
    data_fct['val'] = data_fct.groupby(['team', 'field'])['val'].shift(1)

    # identify promoted/demoted teams & neutralise score for them..
    team_chng = newcomers(data=data_fct)
    res = neutralise_scores(data=data_fct, teams=team_chng, n=k - 1)



# factor library ------------------------------------------------------------------------------------------------------
delete_flib(field="goal_superiority")
update_flib(data=[gsf, fh, fa, ftot, hf], update=True)

flib_x = pd.read_pickle('pro_data/flib_d1.pkl')
flib_x.field.unique()



















