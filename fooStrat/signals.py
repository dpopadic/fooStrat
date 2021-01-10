import pandas as pd
import numpy as np
from datetime import date, datetime
from fooStrat.modelling import mod_periods, est_proba_ensemble
from fooStrat.servicers import neutralise_field
from fooStrat.helpers import anti_join
from fooStrat.constants import fp_cloud


def use_features(data, foi=None):
    """Extract a list of wanted features from the dataset."""
    if foi is None:
        foi = ['rank_position', 'goal_superiority', 'home', 'avg_goal_scored', 'turnaround_ability_last',
               'form_all', 'atadef_composite', 'turnaround_ability_trend', 'odds_accuracy', 'attack_strength',
               'points_advantage', 'not_failed_scoring', 'points_per_game', 'shots_attempted_tgt',
               'h2h_next_opponent_advantage', 'h2h_next_opponent_chance']

    res = data.loc[:, data.columns.isin(['date', 'div', 'season', 'team', 'result'] + foi)]
    return res


def est_upcoming_proba(data,
                       est_dates,
                       lookback='156W',
                       categorical=None,
                       models=['nb', 'knn', 'lg', 'dt'],
                       by='team',
                       show_expired=True):
    """Estimate probability for upcoming games using various models. By default,
    four classification models are estimated: naive bayes, knn, logistic regression
    and a random forest tree model. Models are estimated for each team by default."""
    res_fin = pd.DataFrame()
    for d in data['div'].unique():
        # estimation & prediction window
        per_ind = est_dates[est_dates['div'] == d][['div', 'season', 'date']].reset_index(drop=True)
        data_div = data[data['div'] == d].reset_index(drop=True)
        t_fit = data_div[data_div['date'] != '2050-01-01']['date'].max()
        t_pred = data_div['date'].max()
        res = data_div.groupby(by,
                               as_index=False,
                               group_keys=False).apply(lambda x: est_proba_ensemble(data=x,
                                                                                    per_ind=per_ind,
                                                                                    t_fit=t_fit,
                                                                                    t_pred=t_pred,
                                                                                    lookback=lookback,
                                                                                    categorical=categorical,
                                                                                    models=models,
                                                                                    pred_mode=True))
        res_fin = pd.concat([res_fin, res], axis=0, sort=True)

    # only upcoming (ignore expired events since estimation window start)
    if show_expired is False:
        d0 = date.today().strftime('%Y-%m-%d')
        res_fin = res_fin[res_fin['date'] >= d0]

    res_fin.reset_index(drop=True, inplace=True)

    return res_fin


def add_upcoming_date(data, upcoming):
    """Add the upcoming game date info to predictions."""
    ucg_rel = neutralise_field(data=upcoming, field=['FTHG', 'FTAG'], na_fill=0)
    ucg_rel.rename(columns={'date': 'date_play'}, inplace=True)
    ucg_rel['date_pred'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ucg_rel = ucg_rel[['div', 'season', 'date_play', 'team', 'date_pred']]
    data_ed = pd.merge(data, ucg_rel, on=['div', 'season', 'team'], how='left')
    return data_ed



def register_predictions(data, path=fp_cloud, overwrite=False):
    """Updates the predictions log-file with latest predictions."""
    fp = path + 'log_data/predictions.xlsx'
    if overwrite is False:
        ex = pd.read_excel(fp,
                           sheet_name='data',
                           index_col=0)
        # make sure date objects are correct
        ex['date'] = ex['date'].apply(lambda x: np.datetime64(x))
        ex['date_play'] = ex['date_play'].apply(lambda x: np.datetime64(x))
        new = anti_join(x=data,
                        y=ex[['div', 'season', 'team', 'date_play']],
                        on=['div', 'season', 'team', 'date_play'])
        new = new[new['date'].notnull()]
        upd = pd.concat([ex, new], axis=0, sort=True)
        upd = upd.sort_values('date_play').reset_index(drop=True)
        upd.to_excel(fp, sheet_name='data', engine='openpyxl')

    else:
        data.to_excel(fp, sheet_name='data', engine='openpyxl')

    print("Latest predictions were registered.")



