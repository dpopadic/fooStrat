# SIGNALS / PREDICTIONS -----------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from fooStrat.processing import fp_cloud
import fooStrat.modelling as sm
import fooStrat.evaluation as se
from fooStrat.response import con_res
from fooStrat.servicers import con_est_dates


# DATA LOADING --------------------------------------------------------------------------------------------------------
# pre-processed
source_core = pd.read_pickle(fp_cloud + 'pro_data/source_core.pkl')
match_odds = pd.read_pickle(fp_cloud + 'pro_data/match_odds.pkl')
flib = pd.read_pickle(fp_cloud + 'pro_data/flib_e0.pkl')

# data reshaping for evaluation
results = con_res(data=source_core, obj=['wdl'], event='win')
dasetmod = sm.con_mod_datset_0(factors=flib, results=results)


from fooStrat.servicers import insert_tp1_vals
acon = factors.pivot_table(index=['season', 'div', 'date', 'team'],
                           columns='field',
                           values='val').reset_index()

rcon = results.drop(['field'], axis=1)
rcon_ed = insert_tp1_vals(data=rcon, by=None, append=True)
rcon_ed.rename(columns={'val': 'result'}, inplace=True)
# signals and results
arcon = pd.merge(rcon_ed, acon,
                 on=['div', 'season', 'date', 'team'],
                 how='inner')








