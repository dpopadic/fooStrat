# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import random as rn
from scipy import stats
from scipy.stats import randint
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score
from foostrat_utils import con_res, con_res_wd, con_est_dates, con_mod_datset_0, \
    con_mod_datset_1, comp_mispriced, comp_pnl, est_hist_prob_rf

factor_library = pd.read_pickle('pro_data/flib_e0.pkl')
source_core = pd.read_pickle('pro_data/source_core.pkl')
match_odds = pd.read_pickle('pro_data/match_odds.pkl')
game_day = pd.read_pickle('pro_data/game_day.pkl')

# datasets for evaluation
results = con_res_wd(data=source_core, field=['FTR'], encoding=False)
arcon = con_mod_datset_0(scores=factor_library, results=results)
res_wd = con_res(data=source_core, obj='wdl', field='FTR')
mest_dates = con_est_dates(data=game_day, k=5)

# estimate event probabilities
est_probs = est_hist_prob_rf(arcon=arcon, est_dates=mest_dates, start_date="2010-01-01")


# calculate pnl
event = "win"
event_of =  "odds_" + event
event_opps = est_probs.loc[:, ['date', 'div', 'season', 'team', event]]
event_opps.rename(columns={event: 'val'}, inplace=True)

odds_event = match_odds.query('field == @event_of')
gsf_pos = comp_mispriced(prob=event_opps, odds=odds_event, prob_threshold=0.5, res_threshold=0.10)
gsf_pnl = comp_pnl(positions=gsf_pos, odds=odds_event, results=res_wd, event=event, stake=10)





