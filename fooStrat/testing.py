


df0 = res.query("field=='goal_superiority'").reset_index(drop=True)

gf = df0['div'].unique()
res_tmp = pd.DataFrame()
for i in gf:
    data_f = df0.query('div==@i')
    data_ed = data_f.pivot_table(index=['div', 'date', 'season', 'field'],
                                 columns='team',
                                 values='val').reset_index()

    if date_univ is None:
        # date universe
        date_univ_rel = pd.DataFrame(df0.loc[:, 'date'].unique(), columns={'date'}).sort_values(by='date')
        # copy forward all factors
        data_edm = pd.merge(date_univ_rel,
                            data_ed,
                            on='date',
                            how='outer').sort_values(by='date')
    else:
        data_edm = pd.merge(date_univ,
                            data_ed,
                            on=['date', 'season', 'div'],
                            how='outer').sort_values(by='date')

    # data_ed.reset_index(drop=True, inplace=True)
    data_edm = data_edm.sort_values('date')
    data_edm = data_edm.fillna(method='ffill')  # note that all teams ever played are included
    # data_edm.query("div=='E0' & season=='2019' & field=='team_quality_consistency'")

    # need to filter only teams playing in the season otherwise duplicates issue
    data_edm = pd.melt(data_edm,
                       id_vars=['div', 'season', 'date', 'field'],
                       var_name='team',
                       value_name='val')
    # drop na in fields
    data_edm = data_edm[data_edm['field'].notna()]

    # all teams played in each  season
    tmp = data_f.groupby(['div', 'season'])['team'].unique().reset_index()
    team_seas = tmp.apply(lambda x: pd.Series(x['team']), axis=1).stack().reset_index(level=1, drop=True)
    team_seas.name = 'team'
    team_seas = tmp.drop('team', axis=1).join(team_seas)
    # expanded factors
    fexp = pd.merge(team_seas, data_edm,
                    on=['div', 'season', 'team'],
                    how='inner').sort_values(by='date').reset_index(drop=True)
    res_tmp = res_tmp.append(fexp, ignore_index=True, sort=False)



data_f = df0.query('div==@i')
tmp = data_f.groupby(['div', 'season'])['date'].unique().reset_index()
tmp['key'] = 1
team_univ = pd.DataFrame(data_f.loc[:, 'team'].unique(), columns={'team'})
team_univ['key'] = 1
tmp2 = pd.merge(tmp, team_univ, on = 'key', how='inner').drop('key', axis=1)
tmp3 = tmp2.apply(lambda x: pd.Series(x['date']), axis=1).stack().reset_index(level=1, drop=True)
tmp3.name = 'date'
tmp4 = tmp2.drop('date', axis=1).join(tmp3)






tmp4.query("div=='E0' & season=='2019' & team=='liverpool'")







