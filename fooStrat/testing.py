
fstre.field.unique()
game_day.query("div=='E0' & season=='2019' & team=='liverpool'")
# fields: HTAG, HTHG, FTAG, FTHG
data_neu.query("div=='E0' & season=='2019' & team=='liverpool' & date=='2020-07-22'")
fh2h.query("div=='E0' & team=='liverpool'")


# prediction uncertainty
import fooStrat.mapping as foma





# all odds across bookies
ao = foma.oh + foma.oa + foma.od
aot = ['home_odds' for x in range(len(foma.oh))] + \
      ['away_odds' for x in range(len(foma.oa))] + \
      ['draw_odds' for x in range(len(foma.od))]
oma = pd.DataFrame({'field': ao,
                    'odds_type': aot})
data_ed = pd.merge(data_ed, oma, on='field', how='left')
data_ed.groupby(['div', 'season', 'date', ''])

ao = odds_fields.get('odds_home_win') + odds_fields.get('odds_away_win') + odds_fields.get('odds_draw_win')

data_neu = fose.neutralise_field_multi(data=data,
                                       field=odds_fields,
                                       field_map = odds_fields_neutral,
                                       field_numeric=True,
                                       column_field=False)

data_neu = pd.merge(data_neu,
                    odds_fields_neutral[['field_neutral', 'event']],
                    how = 'left',
                    left_on = 'field',
                    right_on='field_neutral')

data_neu[data_neu['val'].isnull()==True]





