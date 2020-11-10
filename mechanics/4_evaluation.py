# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.evaluation as se
from fooStrat.modelling import est_prob
from fooStrat.response import con_res

# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
flib = pd.read_pickle('data/pro_data/flib_e0.pkl')
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')
game_day = pd.read_pickle('data/pro_data/game_day.pkl')
results = con_res(data=source_core, obj=['wdl', 'gd'])

a = flib.query("team=='liverpool' & season=='2019' & field=='uncertainty_composite'")
pwin.query("team=='liverpool' & season=='2019'")
a = pe.query("season=='2019'").reset_index(drop=True)
a.agg({"max", "min"})
source_core['div'].unique()


# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------
# 1. Is the hit ratio higher for teams that have a higher score?
# 2. Is the factor predictive (ic analysis)?
# 3. Would the factor on itself make money?

flib['field'].unique()
fesel = "goal_superiority"
# feature evaluation analysis
fe = se.eval_feature(data=flib, results=results, feature=fesel, categorical=True)
# estimate probability & evaluate (only non-categorical)
pe, fme = est_prob(factors=flib,
                   results=results['wdl'][results['wdl']['field']=='win'],
                   feature=fesel)
fe['summary']
fe['edge_div']


def est_prob_multi(factors, results, feature):
    """Estimate probability by seperate estimation of win, draw & lose events and normalisation."""
    b = results['wdl'][results['wdl']['field'] == 'win'].query("season=='2010'").reset_index(drop=True)
    flib.query("field==@fesel").agg({'max', 'min', 'mean'})
    from sklearn.preprocessing import MinMaxScaler
    features = X.columns.values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(X)
    X = pd.DataFrame(scaler.transform(X))


    pwin = est_prob(factors=flib,
                    results=results['wdl'][results['wdl']['field'] == 'win'],
                    feature=fesel)[0]
    pdraw = est_prob(factors=flib,
                     results=results['wdl'][results['wdl']['field'] == 'draw'],
                     feature=fesel)[0]
    plose = est_prob(factors=flib,
                     results=results['wdl'][results['wdl']['field'] == 'lose'],
                     feature=fesel)[0]
    pall = pd.concat([pwin, pdraw, plose], axis=0)
    pall = pall.pivot_table(index=['date', 'div', 'season', 'team'],
                            columns='field',
                            values='val').reset_index()
    pall['val'] = pall['win'] + pall['lose'] + pall['draw']









# best features: avg_goal_scored, goal_superiority, not_failed_scoring,
# points_per_game, form_home, form_away, form_all, points_advantage, rank_position, turnaround_ability_last,
# h2h_next_opponent_advantage, h2h_next_opponent_chance, turnaround_ability_trend, odds_volatility,
# odds_accuracy, uncertainty_composite, home











