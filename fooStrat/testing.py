
fstre.field.unique()
game_day.query("div=='E0' & season=='2019' & team=='liverpool'")
# fields: HTAG, HTHG, FTAG, FTHG
data_neu.query("div=='E0' & season=='2019' & team=='liverpool' & date=='2020-07-22'")
data_neu.query("div=='E0' & season=='2019' & team=='chelsea' & date=='2020-07-22'")
data_neu.query("div=='D1' & season=='2019' & team=='dortmund' & date=='2020-06-20' & event=='draw'")
data_neu.query("div=='G1' & team=='olympiakos' & event=='win' & date == '2005-08-28'").sort_values('date')

a = rndo.query("div=='E0' & season=='2019' & team=='liverpool'").sort_values('date')
a1 = data.query("div=='E0' & season=='2019' & home_team=='liverpool' & away_team=='man_city' & field in ['B365H', 'B365A', 'B365D']")
1/5.4 + 1/7.99 + 1/1.45
1/26

i = odds_fields_neutral['field']
ik = data.query("div=='E0' & season=='2019' & date=='2020-07-22' & home_team=='liverpool' & field in @i")
ik = data.query("div=='E0' & season=='2019' & date=='2019-08-09' & home_team=='liverpool' & field=='FTR'")

from fooStrat.evaluation import reshape_wdl
from fooStrat.evaluation import con_res_wd

def feat_odds_uncertainty(data, odds):
    """Derives the prediction/odds uncertainty features.
        - volatility of odds (the higher, the better)
        - odds prediction uncertainty (the less accurate, the better)
        - pricing spread (the higher, the better)
    """
    return data




data_neu = fose.neutralise_field_multi(data=data,
                                       field=odds_fields,
                                       field_map = odds_fields_neutral,
                                       field_numeric=True,
                                       column_field=False)
# unique fields
ofn = odds_fields_neutral.groupby('event')['field_neutral'].unique().reset_index()
ofn = ofn.explode('field_neutral').reset_index(drop=True).rename(columns={'field_neutral': 'field'})
# add event
data_neu = pd.merge(data_neu,
                    ofn,
                    how = 'left',
                    on = 'field')
# --- odds volatility
# calculate vol of draw/win and derive average
df1 = data_neu.groupby(['season', 'div', 'date', 'team', 'event'])['val'].std().reset_index()
df1 = df1.groupby(['season', 'div', 'date', 'team'])['val'].mean().reset_index()
df1['field'] = 'odds_volatility'

# --- historical odds prediction uncertainty (hit ratio)
# 1st approach: determine the lowest odds which define the most likely outcome
# which odds? take max's -> as input since it takes a long time to retrieve
event_wdl = con_res_wd(data=data, field='FTR', encoding=True)

# merge results with odds
mo = match_odds.pivot_table(index=['div', 'season', 'date', 'team'], columns='field', values='val').reset_index()
rndo = pd.merge(event_wdl, mo, on = ['div', 'season', 'date', 'team'], how='left')



# fit logit model
a = rndo.query("div=='E0' & season=='2019' & team=='chelsea' & field=='win'").sort_values('date')
a = rndo.query("div=='E0' & season=='2019' & team in ['chelsea', 'arsenal'] & field=='win'").sort_values('date')
a = rndo.query("div=='E0' & season=='2019'").reset_index(drop=True)

b = a.groupby(['div', 'season', 'team', 'field']).apply(est_odds_accuracy).reset_index()
b = a.groupby(['div', 'season', 'team', 'field']).agg(np.mean)


est_odds_accuracy(data=a.groupby(['div', 'season', 'team', 'field']))


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


















