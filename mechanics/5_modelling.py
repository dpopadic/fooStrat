# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
import fooStrat.modelling as sm
import fooStrat.evaluation as se
from fooStrat.response import con_res
from fooStrat.servicers import con_est_dates

# DATA LOADING --------------------------------------------------------------------------------------------------------
# pre-processed
flib = pd.read_pickle('data/pro_data/flib_e0.pkl')
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')



# data reshaping for evaluation
results = con_res(data=source_core, obj=['wdl'], event='win')
dasetmod = sm.con_mod_datset_0(factors=flib, results=results)
mest_dates = con_est_dates(data=source_core, k=5, map_date=True)
# declare estimation window: mest_window -> based on est_date (rolling last 3 year)

a = mest_dates.query("div=='E0'")

# start with simple naive bayes model with 3y model fitting
from sklearn.naive_bayes import GaussianNB


# add estimation points
df_ext = pd.merge(dasetmod, mest_dates, on=['div', 'season', 'date'], how='left')
df_ext = df_ext.sort_values(['season', 'est_date']).reset_index(drop=True)

b = df_ext.query("team == 'liverpool' & est_date in ['2020-06-22', '2020-02-02', '2020-01-02', '2019-12-05']")
b = b.reset_index(drop=True)
corem = [x for x in b.columns if x not in  ['date', 'div', 'season', 'team', 'est_date']]
d = b[corem]
xed = d.drop('result', axis=1).values.reshape(len(d), -1)
y = d['result'].values
# note: that output is 2d array with 1st (2nd) column probability for 0 (1) with 0.5 threshold
z = GaussianNB().fit(xed, y).predict_proba(xed)[:, 1]
# need to predict the next k probabilities


df_ext.query("est_date=='2020-06-22'")



# estimate event probabilities
est_probs = sm.est_hist_prob_rf(arcon=arcon, est_dates=mest_dates, start_date="2010-01-01")


# calculate pnl
event = "win"
event_of =  "odds_" + event
event_opps = est_probs.loc[:, ['date', 'div', 'season', 'team', event]]
event_opps.rename(columns={event: 'val'}, inplace=True)

odds_event = match_odds.query('field == @event_of')
gsf_pos = sm.comp_mispriced(prob=event_opps, odds=odds_event, prob_threshold=0.5, res_threshold=0.10)
gsf_pnl = se.comp_pnl(positions=gsf_pos, odds=odds_event, results=res_wd, event=event, stake=10)





