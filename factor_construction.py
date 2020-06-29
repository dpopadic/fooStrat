# FACTOR CALCULATION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fhome, odds_fields, fodds, expand_field, \
    comp_score, update_flib, norm_factor, feat_goalbased, feat_resbased, \
    comp_league_standing, feat_stanbased, delete_flib

# load source data..
source_core = pd.read_pickle('pro_data/source_core.pkl')

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


# goal based factors --------------------------------------------------------------------------------------------------
fgb = feat_goalbased(data=source_core, k=5)
fgb = norm_factor(data=fgb)

# result based factors ------------------------------------------------------------------------------------------------
frb = feat_resbased(data=source_core)
frb = norm_factor(data=frb)

# standings based factors ---------------------------------------------------------------------------------------------
fsb = feat_stanbased(data=source_core)
fsb = norm_factor(data=fsb, neutralise=False)

# home factor ---------------------------------------------------------------------------------------------------------
# no need for expansion for boolean factors!
hf = fhome(data=source_core)

# factor library ------------------------------------------------------------------------------------------------------
fsb.field.unique()
delete_flib(field=["points_advantage", "rank_position"])

update_flib(data=[fgb, frb, fsb, hf], update=False)

# verify..
flib_x = pd.read_pickle('pro_data/flib_d1.pkl')
flib_x.field.unique()



















