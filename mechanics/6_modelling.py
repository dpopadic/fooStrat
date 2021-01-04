# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from fooStrat.constants import fp_cloud
import fooStrat.modelling as sm
import fooStrat.evaluation as se
from fooStrat.response import con_res
from fooStrat.servicers import con_est_dates, flib_list

# DATA LOADING --------------------------------------------------------------------------------------------------------
# pre-processed
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
match_odds = pd.read_pickle(fp_cloud + 'pro_data/match_odds.pkl')
leagues = flib_list(data=source_core)
flib = pd.read_pickle(fp_cloud + 'pro_data/flib_e2.pkl')
# flib = pd.read_pickle(fp_cloud + 'pro_data/flib.pkl')

# data reshaping for evaluation
results = con_res(data=source_core, obj=['wdl'], event='win')
dasetmod = sm.con_mod_datset_0(factors=flib, results=results)
est_dates = con_est_dates(data=source_core, k=5, map_date=True, div=flib['div'].iloc[0])


# reducing profit: odds_volatility, h2h_next_opponent_advantage, h2h_next_opponent_chance
# leagues working: e0, e2, e3, i1, n1, sc0, sc2, sc3, sp1
foi = ['rank_position', 'goal_superiority', 'home', 'avg_goal_scored', 'turnaround_ability_last',
       'form_all', 'atadef_composite', 'turnaround_ability_trend', 'odds_accuracy', 'attack_strength',
       'points_advantage', 'not_failed_scoring', 'points_per_game', 'shots_attempted_tgt',
       'h2h_next_opponent_advantage', 'h2h_next_opponent_chance']

# foi = ['h2h_next_opponent_chance', 'home']

dasetmod_fi = dasetmod.loc[:, dasetmod.columns.isin(['date', 'div', 'season', 'team', 'result'] + foi)]
# data = dasetmod_fi.query('team=="liverpool"').reset_index(drop=True)

# ensemble model estimation
pe = sm.est_hist_proba(data=dasetmod_fi,
                       est_dates=est_dates,
                       start_date=np.datetime64('2015-01-01'),
                       lookback='520W',
                       categorical=['home'],
                       models=['nb', 'knn'])
# derive mispriced events
oe = match_odds.query("field=='odds_win'").reset_index(drop=True).drop('field', axis=1)
mo = sm.comp_mispriced(prob=pe,
                       odds=oe,
                       prob_threshold=0.3,
                       res_threshold=0.2)
# compute pnl
fpnl = se.comp_pnl(positions=mo,
                   odds=oe,
                   results=results,
                   event="win",
                   stake=10,
                   size_naive=True)
# summary of evaluation
epnl = se.pnl_eval_summary(z=fpnl['payoff'].values)
epnl



# source_core.query("div=='E0' & away_team=='southampton' & date=='2015-01-11' & field=='PSCA'")
# issue: not all odds are in mapping file: eg. PSCA







