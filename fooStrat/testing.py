
fstre.field.unique()
game_day.query("div=='E0' & season=='2019' & team=='liverpool'")
# fields: HTAG, HTHG, FTAG, FTHG
res.query("div=='E0' & season=='2019' & team=='liverpool' & date=='2020-07-22' & field=='goal_superiority'")
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
                                       column_field=True)











