import pandas as pd
import numpy as np
from fooStrat.constants import fp_cloud
from fooStrat.response import con_res
from fooStrat.features import feat_odds_accuracy

source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
match_odds = pd.read_pickle(fp_cloud + 'pro_data/match_odds.pkl')
wins = con_res(data=source_core, obj='win')


match_odds.query("div == 'E0' & season == '2020' & field == 'odds_win'")

ho = feat_odds_accuracy(data=source_core, odds=match_odds)



