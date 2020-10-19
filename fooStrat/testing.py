
fstre.field.unique()
game_day.query("div=='E0' & season=='2019' & team=='liverpool'")
# fields: HTAG, HTHG, FTAG, FTHG
res.query("div=='E0' & season=='2019' & team=='liverpool' & date=='2020-07-22' & field=='goal_superiority'")

# h2h measured by goals difference of last 5 games against each other
# approach:
# 1. at each point in time, calculate h2h against all teams: h2h_all_opponents
# 2. identify upcoming opponent and fill with relevant h2h number: h2h_next_opponent

data_ed.query("div=='E0' & season=='2019' & (home_team=='liverpool' | away_team=='liverpool')")



data_ed = data[data['field'].isin(['FTHG', 'FTAG'])]
# temporarily for testing:
data_ed = data_ed[data_ed['div'] == 'E0']
data_ed['val'] = data_ed['val'].apply(lambda x: pd.to_numeric(x, errors='coerce'))
tmp = pd.pivot_table(data_ed,
                     index=['div', 'season', 'date', 'home_team', 'away_team'],
                     columns='field',
                     values='val').reset_index()

# home team..
tmp1 = tmp.copy()
tmp1.rename(columns={'home_team': 'team',
                     'away_team': 'opponent',
                     'FTAG': 'g_received',
                     'FTHG': 'g_scored'}, inplace=True)

# away team..
tmp2 = tmp.copy()
tmp2.rename(columns={'home_team': 'opponent',
                     'away_team': 'team',
                     'FTAG': 'g_scored',
                     'FTHG': 'g_received'}, inplace=True)

dfc = pd.concat([tmp1, tmp2], axis=0, sort=False)
dfc_ed = dfc.set_index('date').sort_values('date').groupby(['team', 'opponent'])[['g_scored', 'g_received']].rolling(window=5, min_periods=1).sum().reset_index()
dfc_ed['val'] = dfc_ed['g_scored'] - dfc_ed['g_received']

# add back other information
dfc_fi = pd.merge(dfc[['div', 'season', 'date', 'team', 'opponent']],
                  dfc_ed[['date', 'team', 'opponent', 'val']],
                  on = ['date', 'team', 'opponent'],
                  how='left')


a = dfc.query("div=='E0' & team=='liverpool' & opponent=='arsenal'").sort_values('date')
a1 = dfc_fi.query("date>='2018-01-01' & team=='liverpool'")


