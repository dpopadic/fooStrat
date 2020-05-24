# FACTOR CALCULATION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, fhome, fform, odds_fields, fodds, expand_field, jitter, comp_score

# load source data..
source_core = pd.read_pickle('pro_data/source_core.pkl')
league_standings = pd.read_pickle('pro_data/league_standings.pkl')

# odds retrieval ------------------------------------------------------------------------------------------------------
# get relevant odds
match_odds = fodds(data=source_core,
                   field_home=list(odds_fields.get('odds_home_win')),
                   field_away=list(odds_fields.get('odds_away_win')),
                   field_both=list(odds_fields.get('odds_draw_win')))
match_odds.to_pickle('./pro_data/match_odds.pkl')


# goal superiority rating ---------------------------------------------------------------------------------------------
# compute factor
data_gsf_0 = fgoalsup(data=source_core, field=['FTHG', 'FTAG'], field_name=['g_scored', 'g_received'], k=5)
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


# next factors: points difference, last 3 games points, autocorrelation of outcomes by team,
# head to head, chances (shots, wood hits, corner), volatility of odds (the bigger the better),
# cheap (value, this might be implement at a
# later stage), game importance (top, bottom), clean sheets (no goal), home-away strength, home-away, minutes per
# goal scored, corners, possesion, shots, avg goals per match (scoring rate), league position, failed to score %,
# points per game, scored both halves, conceded/won both halves, lost to nil, losing half-time & winning/draw full-time,
# form (last 5), league


# factor library ------------------------------------------------------------------------------------------------------
factor_library = pd.concat([data_gsf_ed, data_fh_ed, data_fa_ed, data_ftot_ed, data_hf],
                           axis=0,
                           sort=False,
                           ignore_index=True)
factor_library.to_pickle('./pro_data/factor_library.pkl')







