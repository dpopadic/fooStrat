from fooStrat.evaluation import con_res_wd
from fooStrat.features import feat_odds_volatility
from fooStrat.mapping import odds_fields, odds_fields_neutral

match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')
data = source_core

def feat_odds_uncertainty(data, odds):
    """Derives the prediction/odds uncertainty features.
        - volatility of odds (the higher, the better)
        - odds prediction uncertainty (the less accurate, the better)
        - pricing spread (the higher, the better)
    """
    # --- odds volatility
    df1 = feat_odds_volatility(data=data,
                               odds_fields=odds_fields,
                               odds_fields_neutral=odds_fields_neutral)

    # --- historical odds prediction uncertainty (hit ratio)



    return data


def feat_odds_accuracy(data, odds):
    """Estimate odds accuracy using a logit model.

    # Parameters:
    -------------
        data:   pd dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val
        odds:   pd dataframe
                a dataframe with columns div, date, season, field, val

    """
    event_wdl = con_res_wd(data=data, field='FTR', encoding=True)
    # merge results with odds
    mo = match_odds.pivot_table(index=['div', 'season', 'date', 'team'], columns='field', values='val').reset_index()
    rndo = pd.merge(event_wdl, mo, on=['div', 'season', 'date', 'team'], how='left')
    # remove na's
    rndo = rndo.dropna().reset_index(drop=True)
    # estimate accuracy
    rndo_est = rndo.groupby(['div', 'season', 'team', 'field']).apply(ss.est_odds_accuracy,
                                                                      y='val',
                                                                      x=['odds_win', 'odds_draw',
                                                                         'odds_lose']).reset_index()
    return rndo_est






















