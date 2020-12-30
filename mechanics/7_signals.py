# SIGNALS / PREDICTIONS -----------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from fooStrat.constants import fp_cloud
import fooStrat.modelling as sm
import fooStrat.evaluation as se
import fooStrat.signals as si
from fooStrat.response import con_res
from fooStrat.servicers import con_est_dates, neutralise_field


# DATA LOADING --------------------------------------------------------------------------------------------------------
# pre-processed
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
match_odds = pd.read_pickle(fp_cloud + 'pro_data/match_odds.pkl')
ucg = pd.read_pickle(fp_cloud + 'pro_data/upcoming_games.pkl')
flib = pd.read_pickle(fp_cloud + 'pro_data/flib_e0.pkl')

# data reshaping for evaluation
results = con_res(data=source_core, obj=['wdl'], event='win')
dasetmod = sm.con_mod_datset_0(factors=flib, results=results)
dasetmod = si.use_features(data=dasetmod)
est_dates = con_est_dates(data=source_core, k=5, map_date=True, div=flib['div'].iloc[0])

# upcoming games predictions
pe = si.est_upcoming_proba(data=dasetmod,
                           est_dates=est_dates,
                           lookback='520W',
                           categorical=['home'],
                           models=['nb', 'knn'],
                           show_expired=True)
# derive mispriced events
oe = match_odds.query("field=='odds_win'").reset_index(drop=True).drop('field', axis=1)
mo = sm.comp_mispriced(prob=pe,
                       odds=oe,
                       prob_threshold=0.3,
                       res_threshold=0.2)
# real game date info
mo = si.add_upcoming_date(data=mo, upcoming=ucg)
si.register_predictions(data=mo, overwrite=False)









