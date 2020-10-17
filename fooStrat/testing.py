


df0 = res.query("field=='goal_superiority'").reset_index(drop=True)
df1 = expand_field_single(data=df0)


def expand_field(data):
    """
    Expands factors across the entire date spectrum so that cross-sectional analysis
    on the factor can be performed. This means that for every competition (eg. Premier League),
    on each play-day there is a factor for all teams.

    Parameters:
    -----------
        data:       pandas dataframe
                    A dataframe of historical factor scores (eg. goal superiority) with
                    columns div, season, team, date, field, val
        date_univ:  pandas dataframe
                    Optional, a dataframe with date universe by div & season. Used when
                    the date universe in data does not contain all actual game dates

    Details:
    --------
    - Note that the date expansion happens for each available date in data enabling cross-sectional factor
    building by competition

    """
    data_ed = ss.expand_event_sphere(data=data)
    res = pd.DataFrame()
    for k in data['field'].unique():
        tmp = data_ed.copy()
        tmp['field'] = k
        tmp = pd.merge(data, tmp,
                       on=['div', 'season', 'date', 'team', 'field'],
                       how='outer').sort_values(by='date')
        tmp = tmp.sort_values(['div', 'season', 'team', 'field', 'date']).reset_index(drop=True)
        tmp = tmp.fillna(method='ffill')
        res = res.append(tmp, ignore_index=True, sort=False)

    return res




tmp6_1 = df1.query("div=='E0' & season=='2005'")
tmp6_1.team.unique()


