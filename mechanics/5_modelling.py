# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
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
a = mest_dates.query("div=='E0'").reset_index(drop=True)
a['period'] = a.groupby('div')['date'].cumcount() + 1
a['period_2'] = a['period'] % 15

# add estimation points
df_ext = pd.merge(dasetmod, mest_dates, on=['div', 'season', 'date'], how='left')
df_ext = df_ext.sort_values(['season', 'est_date']).reset_index(drop=True)



# start with simple naive bayes model with 3y model fitting
from sklearn.naive_bayes import GaussianNB
from fooStrat.modelling import con_mod_datset_1


# simplistic naive bayes estimation
start_date = np.datetime64('2015-01-01')

# construct date universe
per_ind = mest_dates[(mest_dates['div'] == dasetmod['div'].iloc[0])].reset_index(drop=True)
if start_date is not None:
    tmp = per_ind.loc[per_ind['date'] >= start_date, 'est_date']
    per_iter = pd.DataFrame(tmp.unique(), columns=['date'])
else:
    per_iter = per_ind['est_date']
    per_iter = pd.DataFrame(per_iter.unique(), columns=['date'])

per_iter = per_iter[per_iter['date'].notnull()].date
per_ind = per_ind[['div', 'season', 'date']]

t=1
res = pd.DataFrame()
for t in range(1, len(per_iter)):
    t_fit = per_iter[t - 1]
    t_pred = per_iter[t]
    a = dasetmod.query("team=='liverpool'").reset_index(drop=True)
    X_train, X_test, y_train, meta_test = con_mod_datset_1(data=a,
                                                           per_ind=per_ind,
                                                           t_fit=t_fit,
                                                           t_pred=t_pred,
                                                           per='156W')
    if len(X_test) < 1:
        continue
    else:
        # todo: estimation by team -> team as dummy variables
        z = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
        est_proba = pd.concat([meta_test, pd.DataFrame(z, columns=['val'])], axis=1)
        res.query("team=='liverpool'")
        res = pd.concat([res, est_proba])
    print(t)






# estimate event probabilities
est_probs = sm.est_hist_prob_rf(arcon=dasetmod, est_dates=mest_dates, start_date="2010-01-01")


# calculate pnl
event = "win"
event_of =  "odds_" + event
event_opps = est_probs.loc[:, ['date', 'div', 'season', 'team', event]]
event_opps.rename(columns={event: 'val'}, inplace=True)

odds_event = match_odds.query('field == @event_of')
gsf_pos = sm.comp_mispriced(prob=event_opps, odds=odds_event, prob_threshold=0.5, res_threshold=0.10)
gsf_pnl = se.comp_pnl(positions=gsf_pos, odds=odds_event, results=res_wd, event=event, stake=10)





