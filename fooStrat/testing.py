from fooStrat.evaluation import reshape_wdl
from fooStrat.evaluation import con_res_wd
from fooStrat.features import feat_odds_volatility

def feat_odds_uncertainty(data, odds):
    """Derives the prediction/odds uncertainty features.
        - volatility of odds (the higher, the better)
        - odds prediction uncertainty (the less accurate, the better)
        - pricing spread (the higher, the better)
    """
    df1 = feat_odds_volatility(data=source_core,
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


# fit logit model
a = rndo.query("div=='E0' & season=='2019' & team=='chelsea' & field=='win'").sort_values('date')
a = rndo.query("div=='E0' & season=='2019' & team in ['chelsea', 'arsenal'] & field=='win'").sort_values('date').reset_index(drop=True)
a = rndo.query("div=='E0' & season=='2019'").reset_index(drop=True)

b = a.groupby(['div', 'season', 'team', 'field']).apply(est_odds_accuracy).reset_index()
b = a.groupby(['div', 'season', 'team', 'field']).agg(est_odds_accuracy)


est_odds_accuracy(data=a)


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from fooStrat.helpers import class_accuracy_stats


def est_odds_accuracy(data):
    """Estimates odds accuracy for each team and season. Accuracy is defined here
    as F1 score to take into account unbalanced outcomes.

    Parameters:
    -----------
        data:   pd dataframe
                data with columns odds_win, odds_draw, odds_lose & val (the outcome decoded in 0/1)
    """
    y = a['val'].values
    X = a[['odds_win', 'odds_draw', 'odds_lose']].values
    mod = LogisticRegression()
    mod.fit(X, y)
    y_h = mod.predict(X)
    cm = confusion_matrix(y, y_h)
    ca = class_accuracy_stats(cm).iloc[3,]
    return ca


















