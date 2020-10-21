
fstre.field.unique()
game_day.query("div=='E0' & season=='2019' & team=='liverpool'")
# fields: HTAG, HTHG, FTAG, FTHG
data_neu.query("div=='E0' & season=='2019' & team=='liverpool' & date=='2020-07-22' & event=='draw'")
data_neu.query("div=='E0' & season=='2019' & team=='chelsea' & date=='2020-07-22' & event=='draw'")

df1.query("div=='E0' & season=='2019' & team=='liverpool'")


i = odds_fields_neutral['field']
ik = data.query("div=='E0' & season=='2019' & date=='2020-07-22' & home_team=='liverpool' & field in @i")


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
# calculate vol of draw/win and derive average
df1 = data_neu.groupby(['season', 'div', 'date', 'team', 'event'])['val'].std().reset_index()
df1 = df1.groupby(['season', 'div', 'date', 'team'])['val'].mean().reset_index()
df1['field'] = 'odds_volatility'




