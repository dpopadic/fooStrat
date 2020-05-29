# FACTOR CALCULATION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, fhome, fform, odds_fields, fodds, expand_field, jitter, comp_score

# load source data..
source_core = pd.read_pickle('pro_data/source_core.pkl')
league_standings = pd.read_pickle('pro_data/league_standings.pkl')

# FACTOR LIBRARY ------------------------------------------------------------------------------------------------------
# 1. goal superiority
# 2. form
# 2.1 home form
# 2.2 away form
# 2.3 total form
# 3. home advantage
# 4. consistence
# 4.1 avg goals per match / scoring rate
# 4.2 failed to score
# 4.3 points per game
# 5. leage position
# 5.1 position residual
# 5.2 points residual
# 6. head to head
# 6.1 direct points difference
# 6.2 team cluster points difference
# 7. attack strength
# 7.1 shots
# 7.2 shots on target
# 7.3 wood hits
# 7.4 corners
# 8. defense strength
# 8.1 clean sheets
# 8.2 goals conceded
# 9. prediction uncertainty
# 9.1 volatility of odds
# 9.2 historical prediction accuracy
# 9.3 pricing spread (eg. 1 - p(win) - p(loss) - p(draw), the higher the more uncertain)
# 10. game slippage
# 10.1 game relevance (points difference to top/bottom 5)
# 10.2 tiredness of team (days since last game played)
# 11. turnaround ability (losing half-time & winning/draw full-time)

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

# odds retrieval ------------------------------------------------------------------------------------------------------
# get relevant odds
match_odds = fodds(data=source_core,
                   field_home=list(odds_fields.get('odds_home_win')),
                   field_away=list(odds_fields.get('odds_away_win')),
                   field_both=list(odds_fields.get('odds_draw_win')))
match_odds.to_pickle('./pro_data/match_odds.pkl')


# goal superiority rating ---------------------------------------------------------------------------------------------
# compute factor
data_gsf_0 = fgoalsup(data=source_core, field=['FTHG', 'FTAG'], field_name=['g_scored', 'g_received'], k=3)
# expand across time (and impute across divisions)
data_gsf = expand_field(data=data_gsf_0, impute=True)
# calculate cross-sectional signal across divisions (enable by div)..
data_gsf_ed = comp_score(data=data_gsf, metric='z-score')


# form ----------------------------------------------------------------------------------------------------------------

data_fh = fform(data=source_core, field="FTR", type="home")
data_fh_ed = expand_field(data=data_fh, impute=True)
data_fh_ed = comp_score(data=data_fh_ed, metric='z-score')

data_fa = fform(data=source_core, field="FTR", type="away")
data_fa_ed = expand_field(data=data_fa, impute=True)
data_fa_ed = comp_score(data=data_fa_ed, metric='z-score')

data_ftot = fform(data=source_core, field="FTR", type="all")
data_ftot_ed = expand_field(data=data_ftot, impute=True)
data_ftot_ed = comp_score(data=data_ftot_ed, metric='z-score')


# home factor ---------------------------------------------------------------------------------------------------------
# no need for expansion for boolean factors!
data_hf = fhome(data=source_core)



# factor library ------------------------------------------------------------------------------------------------------

con_flib(data=[data_gsf_ed,
               data_fh_ed,
               data_fa_ed,
               data_ftot_ed,
               data_hf],
         update=False)

















