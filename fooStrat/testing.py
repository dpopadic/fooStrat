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
    df1 = feat_odds_volatility(data=data,
                               odds_fields=odds_fields,
                               odds_fields_neutral=odds_fields_neutral)

    return data



# --- historical odds prediction uncertainty (hit ratio)
# 1st approach: determine the lowest odds which define the most likely outcome
# which odds? take max's -> as input since it takes a long time to retrieve
event_wdl = con_res_wd(data=data, field='FTR', encoding=True)
# merge results with odds
mo = match_odds.pivot_table(index=['div', 'season', 'date', 'team'], columns='field', values='val').reset_index()
rndo = pd.merge(event_wdl, mo, on = ['div', 'season', 'date', 'team'], how='left')
# remove na's
rndo = rndo.dropna().reset_index(drop=True)

# remove observations where a team has never had a certain event
nd = rndo.groupby(['div', 'season', 'team', 'field', 'val'])['date'].agg('count').reset_index()
nd = nd[nd['date'] > 1]
nd.drop('date', axis=1, inplace=True)
rndo_ed = pd.merge(rndo, nd, on=['div', 'season', 'team', 'field', 'val'], how='inner')

rndo_ed = rndo.query("div=='E0'").reset_index(drop=True)

# estimate accuracy
rndo_est = rndo.groupby(['div', 'season', 'team', 'field']).apply(ss.est_odds_accuracy, y='val', x=['odds_win', 'odds_draw', 'odds_lose']).reset_index()
rndo_est
rndo_est.query("team=='liverpool'")


# fit logit model
a = rndo.query("div=='E0' & season=='2019' & team=='chelsea' & field=='draw'").sort_values('date')
a = rndo.query("div=='E0' & season=='2019' & team in ['chelsea', 'arsenal'] & field=='win'").sort_values('date').reset_index(drop=True)
a = rndo.query("div=='E0' & season in ['1995', '2000']").reset_index(drop=True)

a = a.dropna().reset_index(drop=True)
b = a.groupby(['div', 'season', 'team', 'field']).apply(ss.est_odds_accuracy, y='val', x=['odds_win', 'odds_draw', 'odds_lose']).reset_index()
b

est_odds_accuracy(data=a, y='val', x=['odds_win', 'odds_draw', 'odds_lose'])



















