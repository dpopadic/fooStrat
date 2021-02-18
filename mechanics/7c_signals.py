# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from fooStrat.constants import fp_cloud
import fooStrat.modelling as sm
import fooStrat.evaluation as se
from fooStrat.response import con_res
from fooStrat.servicers import con_est_dates, flib_list, elim_na_features
from fooStrat.signals import use_features

# DATA LOADING --------------------------------------------------------------------------------------------------------
# pre-processed
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
match_odds = pd.read_pickle(fp_cloud + 'pro_data/match_odds.pkl')
results = con_res(data=source_core, obj='25g')
leagues = flib_list(data=source_core)
# div_k = 'e0'


epnl_fin = pd.DataFrame()
for div_k in leagues:
    flib = pd.read_pickle(fp_cloud + 'pro_data/flib_' + div_k + '.pkl')
    # data reshaping for evaluation
    dasetmod = sm.con_mod_datset_0(factors=flib, results=results)
    dasetmod_fi = use_features(data=dasetmod,
                               foi=['goal_superiority', 'home', 'avg_goal_scored', 'form_all',
                                    'attack_strength', 'not_failed_scoring', 'points_per_game',
                                    'shots_attempted_tgt', 'h2h_next_opponent_chance'])
    dasetmod_fi = elim_na_features(data=dasetmod_fi)
    est_dates = con_est_dates(data=source_core, k=5, map_date=True, div=flib['div'].unique())

    # ensemble model estimation
    pe = sm.est_hist_proba(data=dasetmod_fi,
                           est_dates=est_dates,
                           start_date=np.datetime64('2015-01-01'),
                           lookback='364W',
                           categorical=['home'],
                           models=['nb', 'knn', 'lg', 'dt'])
    # note: p1 returns empty DF
    if len(pe) > 0:
        # derive mispriced events
        oe = match_odds.query("field=='odds_25g'").reset_index(drop=True).drop('field', axis=1)
        mo = sm.comp_mispriced(prob=pe,
                               odds=oe,
                               prob_threshold=0.5,
                               res_threshold=0.20)
        # compute pnl
        fpnl = se.comp_pnl(positions=mo,
                           odds=oe,
                           results=results,
                           stake=10,
                           size_naive=True)
        # summary of evaluation
        epnl = se.pnl_eval_summary(z=fpnl['payoff'].values)
        epnl['div'] = fpnl['div'][0]
        epnl_fin = pd.concat([epnl_fin, epnl], axis=0, sort=True)

    print(div_k)







