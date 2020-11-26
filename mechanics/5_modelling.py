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
mest_dates = con_est_dates(data=source_core, k=5, map_date=True, div=flib['div'].iloc[0])

dasetmod_fi = dasetmod[['date', 'div', 'season', 'team', 'result', 'rank_position', 'home']]
# simplistic naive bayes estimation
pe = sm.est_hist_proba_nb(data=dasetmod_fi, est_dates=mest_dates, start_date=np.datetime64('2010-01-01'), lookback='312W')
# derive mispriced events
oe = match_odds.query("field=='odds_win'").reset_index(drop=True).drop('field', axis=1)
mo = sm.comp_mispriced(prob=pe,
                       odds=oe,
                       prob_threshold=0.5,
                       res_threshold=0.2)
# compute pnl
fpnl = se.comp_pnl(positions=mo,
                   odds=oe,
                   results=results,
                   event="win",
                   stake=10)






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
        # make no predictions if only 1 class (eg. win) is present in training set (revisit this later)
        try:
            z = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
            est_proba = pd.concat([meta_test, pd.DataFrame(z, columns=['val'])], axis=1)
        except:
            est_proba = pd.DataFrame()

    print(ik)





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





