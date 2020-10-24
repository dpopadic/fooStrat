
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
data_ed = data[data['field'] == 'FTR'].reset_index(drop=True)
# data_ed = reshape_wdl(data=data_ed, event='wdl', as_numeric=True)
event_win = reshape_wdl(data=data_ed, event='win')
event_lose = reshape_wdl(data=data_ed, event='lose')
event_draw = reshape_wdl(data=data_ed, event='draw')
event_wdl = pd.concat([event_win, event_lose, event_draw],
                      axis=0,
                      sort=True,
                      ignore_index=True).reset_index(drop=True)

# merge results with odds
mo = match_odds.pivot_table(index=['div', 'season', 'date', 'team'], columns='field', values='val').reset_index()
rndo = pd.merge(event_wdl, mo, on = ['div', 'season', 'date', 'team'], how='left')

# fit logit model
a = rndo.query("div=='E0' & season=='2019' & team=='liverpool'").sort_values('date')








