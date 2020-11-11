# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import fooStrat.evaluation as se
from fooStrat.modelling import est_prob, comp_mispriced
from fooStrat.response import con_res

# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
flib = pd.read_pickle('data/pro_data/flib_e0.pkl')
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')
game_day = pd.read_pickle('data/pro_data/game_day.pkl')
results = con_res(data=source_core, obj=['wdl', 'gd'])

a = flib.query("team=='liverpool' & season=='2019' & field=='uncertainty_composite'")
a = prob.query("season=='2019' & team=='liverpool' ").reset_index(drop=True)
a.agg({"max", "min"})


# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------
# 1. Is the hit ratio higher for teams that have a higher score?
# 2. Is the factor predictive (ic analysis)?
# 3. Would the factor on itself make money?

flib['field'].unique()
fesel = "points_advantage"
# feature evaluation analysis
fe = se.eval_feature(data=flib, results=results, feature=fesel, categorical=True)
# estimate probability & evaluate (only non-categorical)
pe, fme = est_prob(factors=flib,
                   results=results['wdl'][results['wdl']['field']=='win'],
                   feature=fesel)
fe['summary']
fe['edge_div']

oe = match_odds.query("field=='odds_win'").reset_index(drop=True).drop('field', axis=1)
a = comp_mispriced(prob=pe,
                   odds=oe,
                   prob_threshold=0.5,
                   res_threshold=0.1)

b = se.comp_pnl(positions=a,
                odds=oe,
                results=results['wdl'],
                event="win",
                stake=10)
b



def est_prob_multi(factors, results, feature):
    """Estimate probability by seperate estimation of win, draw & lose events and normalisation."""

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


ypp2 = pd.Series(y_pp)
ypp2.plot.hist(grid=True, bins=20, rwidth=0.9,color='#607c8e')





# best features: avg_goal_scored, goal_superiority, not_failed_scoring,
# points_per_game, form_home, form_away, form_all, points_advantage, rank_position, turnaround_ability_last,
# h2h_next_opponent_advantage, h2h_next_opponent_chance, turnaround_ability_trend, odds_volatility,
# odds_accuracy, uncertainty_composite, home











