# STRATEGY TESTING ----------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from fooStrat.processing import fp_cloud
import fooStrat.evaluation as se
from fooStrat.modelling import est_prob, comp_mispriced
from fooStrat.response import con_res

# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
flib = pd.read_pickle(fp_cloud + 'pro_data/flib_e0.pkl')
match_odds = pd.read_pickle(fp_cloud + 'pro_data/match_odds.pkl')
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
results = con_res(data=source_core, obj=['wdl', 'gd'], event='win')

# not working at season start with insufficient data
flib = flib.query("season not in ['2020']").reset_index(drop=True)


# SIGNAL EFFICACY -----------------------------------------------------------------------------------------------------
# 1. Is the hit ratio higher for teams that have a higher score?
# 2. Is the factor predictive (ic analysis)?
# 3. Would the factor on itself make money?
# -- noticable features: wood_hit, rank_position, odds_volatility

flib['field'].unique()
fesel = "goal_superiority"
# feature evaluation analysis
fe = se.eval_feature(data=flib, results=results, feature=fesel, categorical=False)
# estimate probability & evaluate (only non-categorical) -> 3y rolling by team seems to work quite well
pe, fme = est_prob(factors=flib,
                   results=results['wdl'],
                   feature=fesel)
# derive mispriced events
oe = match_odds.query("field=='odds_win'").reset_index(drop=True).drop('field', axis=1)
mo = comp_mispriced(prob=pe,
                    odds=oe,
                    prob_threshold=0.5,
                    res_threshold=0.2)
# compute pnl
fpnl = se.comp_pnl(positions=mo,
                   odds=oe,
                   results=results['wdl'],
                   event="win",
                   stake=10)


# best features: avg_goal_scored, goal_superiority, not_failed_scoring,
# points_per_game, form_home, form_away, form_all, points_advantage, rank_position, turnaround_ability_last,
# h2h_next_opponent_advantage, h2h_next_opponent_chance, turnaround_ability_trend, odds_volatility,
# odds_accuracy, uncertainty_composite, home











