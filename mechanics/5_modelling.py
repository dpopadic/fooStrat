# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------
import pandas as pd
import fooStrat.servicers as ss
import fooStrat.modelling as sm
import fooStrat.evaluation as se

factor_library = pd.read_pickle('data/pro_data/flib_e0.pkl')
source_core = pd.read_pickle('data/pro_data/source_core.pkl')
match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')
game_day = pd.read_pickle('data/pro_data/game_day.pkl')

# datasets for evaluation
results = ss.con_res_wd(data=source_core, field=['FTR'], encoding=False)
arcon = sm.con_mod_datset_0(scores=factor_library, results=results)
res_wd = se.con_res(data=source_core, obj='wdl', field='FTR')
mest_dates = ss.con_est_dates(data=game_day, k=5)

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





