# FACTOR CALCULATION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from foostrat_utils import fgoalsup, fhome, odds_fields, fodds, expand_field, jitter, comp_score

# load source data..
source_core = pd.read_pickle('pro_data/source_core.pkl')


# odds retrieval ------------------------------------------------------------------------------------------------------
# get relevant odds
match_odds = fodds(source_core,
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




# home factor ---------------------------------------------------------------------------------------------------------
# no need for expansion for boolean factors!
data_hf = fhome(data=source_core)


# next factors: points difference, last 3 games points, autocorrelation of outcomes by team,
# head to head, chances (shots, wood hits, corner), volatility of odds, cheap (value, this might be implement at a
# later stage), game importance (top, bottom)


# factor library ------------------------------------------------------------------------------------------------------
factor_library = pd.concat([data_gsf_ed, data_hf],
                           axis=0,
                           sort=False,
                           ignore_index=True)
factor_library.to_pickle('./pro_data/factor_library.pkl')







