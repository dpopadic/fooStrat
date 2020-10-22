
fstre.field.unique()
game_day.query("div=='E0' & season=='2019' & team=='liverpool'")
# fields: HTAG, HTHG, FTAG, FTHG
data_neu.query("div=='E0' & season=='2019' & team=='liverpool' & date=='2020-07-22' & event=='win'")
data_neu.query("div=='E0' & season=='2019' & team=='chelsea' & date=='2020-07-22' & event=='win'")
data_neu.query("div=='D1' & season=='2019' & team=='dortmund' & date=='2020-06-20' & event=='draw'")
data_neu.query("div=='G1' & team=='olympiakos' & event=='win' & date == '2005-08-28'").sort_values('date')

a = rdf0.query("div=='E0' & season=='2019' & team=='liverpool'")


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
data_ed = reshape_wdl(data=data_ed, event='wdl')




