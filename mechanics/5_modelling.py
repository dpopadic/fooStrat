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
    # approach 1: estimation by team -> team as dummy variables - not working
    # approach 2: con_mod_datset_1 and estimation in a single function & output predictions only
    a = dasetmod.query("team=='liverpool'").reset_index(drop=True)
    X_train, X_test, y_train, meta_test = con_mod_datset_1(data=a,
                                                           per_ind=per_ind,
                                                           t_fit=t_fit,
                                                           t_pred=t_pred,
                                                           per='156W')
    if len(X_test) < 1:
        continue
    else:
        z = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
        est_proba = pd.concat([meta_test, pd.DataFrame(z, columns=['val'])], axis=1)
        res = pd.concat([res, est_proba])
    print(t)


t=1
df = dasetmod.query("team in ['liverpool', 'arsenal']").reset_index(drop=True)
res = pd.DataFrame()
for t in range(1, len(per_iter)):
    t_fit = per_iter[t - 1]
    t_pred = per_iter[t]
    dfz = dasetmod.groupby(['team'],
                           as_index=False,
                           group_keys=False).apply(lambda x: est_proba_nb(data=x, per_ind=per_ind, t_fit=t_fit, t_pred=t_pred))
    res = pd.concat([res, dfz])
    print(t)

a = dasetmod.query("date <= @t_pred").set_index('date').last('156W').reset_index()
d = a.team.unique()
b = a.query("team=='bournemouth'").reset_index(drop=True)

for i in range(0, len(d)):
    ik = d[i]
    b = a.query("team==@ik").reset_index(drop=True)
    X_train, X_test, y_train, meta_test = con_mod_datset_1(data=b,
                                                           per_ind=per_ind,
                                                           t_fit=t_fit,
                                                           t_pred=t_pred,
                                                           per='156W')
    if len(X_train) < 1 or len(X_test) < 1:
        est_proba = pd.DataFrame()
    else:
        z = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
        est_proba = pd.concat([meta_test, pd.DataFrame(z, columns=['val'])], axis=1)

    print(ik)


def est_proba_nb(data, per_ind, t_fit, t_pred):
    """Estimate historical probabilities."""
    X_train, X_test, y_train, meta_test = con_mod_datset_1(data=data,
                                                           per_ind=per_ind,
                                                           t_fit=t_fit,
                                                           t_pred=t_pred,
                                                           per='156W')
    if len(X_train) < 1 or len(X_test) < 1:
        est_proba = pd.DataFrame()
    else:
        z = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
        est_proba = pd.concat([meta_test, pd.DataFrame(z, columns=['val'])], axis=1)

    return est_proba



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





