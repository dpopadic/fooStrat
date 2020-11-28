# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.modelling as sm
import fooStrat.evaluation as se
from fooStrat.response import con_res
from fooStrat.servicers import con_est_dates

# DATA LOADING --------------------------------------------------------------------------------------------------------
# pre-processed
flib = pd.read_pickle('data/pro_data/flib_switzerland_super_league.pkl')
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')

# data reshaping for evaluation
results = con_res(data=source_core, obj=['wdl'], event='win')
dasetmod = sm.con_mod_datset_0(factors=flib, results=results)
mest_dates = con_est_dates(data=source_core, k=5, map_date=True, div=flib['div'].iloc[0])
flib['field'].unique()


# reducing profit: odds_volatility, h2h_next_opponent_advantage, h2h_next_opponent_chance
# leagues working: e0, e2, e3, i1, n1, sc0, sc2, sc3, sp1
foi = ['rank_position', 'goal_superiority', 'home', 'avg_goal_scored', 'turnaround_ability_last',
       'form_all', 'atadef_composite', 'turnaround_ability_trend', 'odds_accuracy', 'attack_strength',
       'points_advantage', 'not_failed_scoring', 'points_per_game', 'shots_attempted_tgt']
dasetmod_fi = dasetmod.loc[:, dasetmod.columns.isin(['date', 'div', 'season', 'team', 'result'] + foi)]


# simplistic naive bayes estimation
pe = sm.est_hist_proba_nb(data=dasetmod_fi,
                          est_dates=mest_dates,
                          start_date=np.datetime64('2010-01-01'),
                          lookback='520W',
                          categorical=['home'])
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
                   stake=10)
# summary of evaluation
epnl = se.pnl_eval_summary(z=fpnl['payoff'].values)
epnl












