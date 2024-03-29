import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from scipy.stats import zscore
from fooStrat.helpers import jitter, anti_join

def comp_league_standing(data,
                         season=None,
                         home_goals='FTHG',
                         away_goals='FTAG',
                         result='FTR'):
    """Computes the standings, ranks, goals etc. for a single or multiple divisions by
    season. The input table therefore needs to have the following columns:
    div, season, date, home_team, away_team, field, val

    Note that an adjustment for newcomers / demoted teams is not required here since no observations
    from previous seasons are taken into account.

    Parameters:
    -----------
        data:       pandas dataframe
                    a dataframe with columns div, season, date, home_team, away_team, field, val
        season:     list
                    a list of values in season for which to calculate standings (defaults to None in which case
                    standings for all seasons are calculated)
        home_goals: str
                    home goals field in data
        away_goals: str
                    away goals field in data
        result:     str
                    results field in data

    Returns:
    --------
        tbl (dataframe): a table with team rankings by division and season and the following
        columns: div | season | team | points | goals_scored | goals_received | d | l | w | rank

    """
    if season is not None:
        data = data[data['season'].isin(season)]

    # extract relevant fields..
    df_fw = data.pivot_table(index=['season', 'div', 'date', 'home_team', 'away_team'],
                             columns='field',
                             values='val',
                             aggfunc='sum').reset_index()

    # home team stats..
    df_h = df_fw.loc[:, ['season', 'div', 'date', 'home_team', away_goals, home_goals, result]]
    df_h['points'] = df_h[result].apply(lambda x: 3 if x == 'H' else (1 if x == 'D' else 0))
    df_h['res'] = df_h[result].apply(lambda x: 'w' if x == 'H' else ('d' if x == 'D' else ('l' if x=='A' else np.nan)))
    df_h.rename(columns={'home_team': 'team',
                         away_goals: 'goals_received',
                         home_goals: 'goals_scored'}, inplace=True)
    df_h = df_h.drop([result], axis=1)

    # away team stats..
    df_a = df_fw.loc[:, ['season', 'div', 'date', 'away_team', away_goals, home_goals, result]]
    df_a['points'] = df_a[result].apply(lambda x: 3 if x == 'A' else (1 if x == 'D' else 0))
    df_a['res'] = df_a[result].apply(lambda x: 'w' if x == 'A' else ('d' if x == 'D' else ('l' if x=='H' else np.nan)))
    df_a.rename(columns={'away_team': 'team',
                         away_goals: 'goals_scored',
                         home_goals: 'goals_received'}, inplace=True)
    df_a = df_a.drop([result], axis=1)

    # consolidate
    dfc = pd.concat([df_h, df_a], axis=0, sort=True)
    dfc[['goals_scored', 'goals_received']] = dfc[['goals_scored', 'goals_received']].apply(pd.to_numeric,
                                                                                            errors='coerce')

    # a = res.query("div=='E2' & team in ['shrewsbury']").sort_values(['team', 'date'])

    # over time
    dfc_tot_pts = dfc.sort_values(['date']).reset_index(drop=True)
    metr = dfc_tot_pts.groupby(by=['div', 'season', 'team'])[['points', 'goals_scored', 'goals_received']]. \
        cumsum().reset_index(level=0, drop=True)
    dfc_tot_pts_ed = pd.concat([dfc_tot_pts[['date', 'div', 'season', 'team']], metr], axis=1)

    # number of wins, losses, draws
    df_wdl = dfc.loc[:, ['season', 'div', 'date', 'team', 'res']]
    df_wdl['dummy'] = 1
    df_wdl = df_wdl.sort_values(['date']).reset_index(drop=True)
    dfc_agg_wdl = df_wdl.pivot_table(index=['div', 'season', 'date', 'team'],
                                     columns='res',
                                     values='dummy').reset_index()
    dfc_agg_wdl = dfc_agg_wdl.fillna(0)
    dfc_agg_wdlc = dfc_agg_wdl.groupby(['div', 'season', 'team'])[['d', 'l', 'w']]. \
        cumsum(skipna=True).reset_index(level=0, drop=True)
    dfc_agg_wdl = pd.concat([dfc_agg_wdl[['date', 'div', 'season', 'team']], dfc_agg_wdlc], axis=1)

    # rename columns
    dfc_agg_wdl.rename(columns={'w': 'wins', 'l': 'losses', 'd': 'draws'}, inplace=True)

    # add number of wins, draws & losses to standings
    res_0 = pd.merge(dfc_tot_pts_ed, dfc_agg_wdl,
                     on=['div', 'season', 'team', 'date'],
                     how='left')

    # need to expand to have a representation of every team at each date
    res_1 = expand_event_sphere(data=res_0[['div', 'season', 'date', 'team']])
    res_1.reset_index(drop=True, inplace=True)
    res_2 = pd.merge(res_0, res_1, on = ['div', 'season', 'date', 'team'], how='outer')
    # fill missing
    res = res_2.sort_values(['div', 'season', 'team', 'date']).reset_index(drop=True)
    res = res.fillna(method='ffill')
    # a = res.query("div=='E2' & date in ['2050-01-01', '2020-12-19']")

    # rankings
    res['rank'] = res.groupby(['div', 'season', 'date'])['points'].rank(ascending=False,
                                                                        method='first').reset_index(drop=True)

    return res




def neutralise_field(data, field, field_name=None, field_numeric=True, column_field=True, na_fill=None):
    """
    Reshapes the data from a pairwise column-based format (eg. home_team, away_team) where fields are relative
    to either one column or another to a wide format neutralised for this column dependency.

    Parameters:
    -----------
        data (dataframe):   a dataframe with columns div, date, season, home_team, away_team, field, val
        field (list):       a list specifying the field(s) of interest (eg. ['FTHG', 'FTAG'])
        field_name (list):  optional, a list with new field name for fields (eg. ['g_scored', 'g_received'])
        field_numeric (boolean): whether the field to transpose is numeric (True) or not (False)
        column_field (boolean):  whether to have the fields in columns or in wide-format
        na_fill (double or str):  fill na values where fields are not present (eg. FTHG - `na_fill=0`)

    Details:
    --------
        Note that a field can be symmetric, meaning that the field needs to be taken into account for both,
        the home- & away team. An example of a symmetric field is FTHG, where the goals need to be reflected in both
        the home field as well as away field. If the field is asymmetric, the field is only applicable to either
        home- or away team. An example of an asymmetric field could be the field shots.

    Returns:
    --------
        A dataframe with team-neutralised data.

    Example:
    --------
    data:
              div       date      home_team    away_team     season field val
            0  E0 2004-08-14    aston_villa  southampton  2004-2005  FTHG   2
            1  E0 2004-08-14      blackburn    west_brom  2004-2005  FTHG   1
            2  E0 2004-08-14         bolton     charlton  2004-2005  FTHG   4
            3  E0 2004-08-14       man_city       fulham  2004-2005  FTHG   1
            4  E0 2004-08-14  middlesbrough    newcastle  2004-2005  FTHG   2

    neutralise_field(data, field=['FTHG', 'FTAG'], field_name=['g_scored', 'g_received'],
                     field_numeric=True, column_field=False)

                                  div     season  date team g_received g_scored
            0      Argentina Superliga  2012/2013  ...          0        1
            1      Argentina Superliga  2012/2013  ...          0        1
            2      Argentina Superliga  2012/2013  ...          0        3
            3      Argentina Superliga  2012/2013  ...          1        1
            4      Argentina Superliga  2012/2013  ...          0        3

    """

    # filter relevant fields..
    data_ed = data[(data['field'].isin(field))].reset_index(drop=True)
    # sometimes, the field does not exist, so return empty df
    if len(data_ed) < 1:
        return pd.DataFrame(columns=['div', 'season', 'date', 'team'] + field_name)

    if field_numeric == True:
        data_ed['val'] = data_ed['val'].apply(lambda x: pd.to_numeric(x, errors='coerce'))

    # fill na values (mostly supposed to be predictions)
    if na_fill != None:
        data_ed = data_ed.fillna(na_fill)

    # put the fields in wide format
    tmp = pd.pivot_table(data_ed,
                         index=['div', 'season', 'date', 'home_team', 'away_team'],
                         columns='field',
                         values='val').reset_index()

    # home team..
    tmp1 = tmp.drop('away_team', axis=1)
    tmp1.rename(columns={'home_team': 'team'}, inplace=True)
    if field_name != None:
        tmp1.rename(columns=dict(zip(tmp1.loc[:, field], field_name)), inplace=True)

    # away team (note that fields are reversed here!)..
    tmp2 = tmp.drop('home_team', axis=1)
    tmp2.rename(columns={'away_team': 'team'}, inplace=True)
    if field_name != None:
        tmp2.rename(columns=dict(zip(tmp2.loc[:, field[::-1]], field_name)), inplace=True)

    # put together..
    data_ed_co = pd.concat([tmp1, tmp2], axis=0, sort=False, ignore_index=True)

    if column_field == False:
        data_ed_co = pd.melt(data_ed_co,
                             id_vars=['div', 'season', 'date', 'team'],
                             var_name='field',
                             value_name='val')

    return data_ed_co



def neutralise_field_multi(data, field, field_map, field_numeric=True, column_field=True):
    """
    Same as `neutralise_field` but with multiple field functionality.
    """

    # filter relevant fields
    arf = field.get('odds_home_win') + field.get('odds_away_win') + field.get('odds_draw_win')
    data_ed = data[data['field'].isin(arf)].reset_index(drop=True)

    if field_numeric == True:
        data_ed['val'] = data_ed['val'].apply(lambda x: pd.to_numeric(x, errors='coerce'))

    # home team..
    rfh = field.get('odds_home_win') + field.get('odds_draw_win')
    tmp1 = pd.pivot_table(data_ed[data_ed['field'].isin(rfh)],
                          index=['div', 'season', 'date', 'home_team', 'away_team'],
                          columns='field',
                          values='val').reset_index()
    tmp1 = tmp1.drop('away_team', axis=1)
    tmp1.rename(columns={'home_team': 'team'}, inplace=True)
    rfh_m = field_map[field_map['field'].isin(rfh)]
    tmp1.rename(columns=dict(zip(tmp1.loc[:, rfh_m['field']], rfh_m['field_neutral'])), inplace=True)


    # away team (note that fields are reversed here!)..
    rfa = field.get('odds_away_win') + field.get('odds_draw_win')
    tmp2 = pd.pivot_table(data_ed[data_ed['field'].isin(rfa)],
                          index=['div', 'season', 'date', 'home_team', 'away_team'],
                          columns='field',
                          values='val').reset_index()
    tmp2 = tmp2.drop('home_team', axis=1)
    tmp2.rename(columns={'away_team': 'team'}, inplace=True)
    rfa_m = field_map[field_map['field'].isin(rfa)]
    tmp2.rename(columns=dict(zip(tmp2.loc[:, rfa_m['field']], rfa_m['field_neutral'])), inplace=True)

    # put together..
    data_ed_co = pd.concat([tmp1, tmp2], axis=0, sort=False, ignore_index=True)

    if column_field == False:
        data_ed_co = pd.melt(data_ed_co,
                             id_vars=['div', 'season', 'date', 'team'],
                             var_name='field',
                             value_name='val')
        data_ed_co = data_ed_co[data_ed_co['val'].isnull() == False]

    return data_ed_co





def con_h2h_set(data, field, field_name=None):
    """Constructs a head-to-head dataset.

    Parameters:
    -----------
        data:       pandas dataframe
                    a dataframe with columns div, season, date, home_team, away_team, field, val
        field:      list
                    a list with 2 relevant fields for each side (home_team, away_team) in `data` (eg. ['FTHG', 'FTAG'])
        field_name: list
                    optional, a list with names for the home_team field and away_team field (in this order)

    """
    data_ed = data[data['field'].isin(field)].reset_index(drop=True)
    data_ed['val'] = data_ed['val'].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    tmp = pd.pivot_table(data_ed,
                         index=['div', 'season', 'date', 'home_team', 'away_team'],
                         columns='field',
                         values='val').reset_index()

    if field_name is None:
        field_name = field

    # home team..
    tmp1 = tmp.copy()
    tmp1.rename(columns={'home_team': 'team',
                         'away_team': 'opponent',
                         field[1]: field_name[1],
                         field[0]: field_name[0]}, inplace=True)

    # away team..
    tmp2 = tmp.copy()
    tmp2.rename(columns={'home_team': 'opponent',
                         'away_team': 'team',
                         field[1]: field_name[0],
                         field[0]: field_name[1]}, inplace=True)

    dfc = pd.concat([tmp1, tmp2], axis=0, sort=False)

    return dfc



def con_h2h_set_upcoming(data):
    """Constructs the head-to-head upcoming games dataset."""
    pds = data.query("field=='FTR'")[['div', 'season', 'date', 'home_team', 'away_team']]
    pds = pds[pds['date'] == pds['date'].max()].reset_index(drop=True)
    pds_1 = pds.rename(columns={'home_team': 'team',
                                'away_team': 'opponent'})
    pds_2 = pds.rename(columns={'home_team': 'opponent',
                                'away_team': 'team'})
    pds = pd.concat([pds_1, pds_2], axis=0, sort=False)
    pds = pds.assign(val = np.nan)
    return pds



def newcomers(data):
    """Identify newcomers (promoted/demoted teams) in each season. This is used to neutralise scores for these
    teams at the start of each season.

    Parameters:
    -----------
        data (dataframe):   a dataframe with columns div, date, season, team

    Details:
    --------
        It is assumed that each league has a continuous data series for each year in the history provided. If
        this is not the case, the resulting teams will not be accurate.

    """
    # assemble all teams by season, div
    U = data.groupby(['season', 'div'])['team'].unique().reset_index()
    Ue = U.apply(lambda x: pd.Series(x['team']), axis=1).stack().reset_index(level=1, drop=True)
    Ue.name = 'team'
    Ue = U.drop('team', axis=1).join(Ue)
    # identify promoted & demoted teams
    Ue_0 = Ue.copy()
    Ue_0['season'] = Ue_0['season'] + 1
    # identify teams that where there the season before..
    Ue_1 = pd.merge(Ue_0, Ue, on=["season", "div", "team"], how="inner")
    # identify teams that are new in each season..
    res = anti_join(Ue_1, Ue, on=["season", "div", "team"])

    return res



def neutralise_scores(data, teams, n):
    """Neutralises first n scores for teams by season and division. This is required where
    rolling figures are calculated. Provided that some teams are promoted or demoted, the
    numbers will not reflect the performance in the new league. Therefore, the first n observations
    need to be neutralised (eg. set to zero).

    Parameters:
    -----------
        data (dataframe):   a dataframe of factor scores with columns div, date, season, team, field, val
        teams (dataframe):  a dataframe of newcoming teams with columns div, season, team
        n (int):            the first n observations by div, season, team to replace by zero

    Details:
    --------
    In cases where the data is not available for previous years (eg. Japan J1 League), factors for all teams
    but not only newcomers will be neutralised.

    """
    # retrieve factor scores for the relevant teams..
    Rt = pd.merge(data, teams, on=['div', 'season', 'team'], how='inner')
    Rt.sort_values(['div', 'team', 'date'], inplace=True)
    Rt = Rt.groupby(['div', 'season', 'team']).head(n)
    # set values to zero for these fields..
    Rt['val'] = 0
    # remove the adjusted values and add back the new values..
    data_ed = anti_join(data, Rt[['div', 'date', 'team']], on=['div', 'team', 'date'])
    res = pd.concat([data_ed, Rt], axis=0, sort=False, ignore_index=True)
    res = res.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)
    return res


def norm_factor(data, neutralise=True):
    """Normalise factor data by expanding observations across the date spectrum and imputing missing data by
    comptetition.

    Parameters:
    -----------
        data:           pandas dataframe
                        data with columns div, season, date, team, field, val
        neutralise:     boolean, True
                        whether to calculate z-scores from the input signal

    """
    # expand across time (and impute by division)
    res = expand_field(data=data, impute=True)
    if neutralise == True:
        # calculate cross-sectional signal
        res = comp_score(data=res, metric='z-score')

    return res


def expand_event_sphere(data, dates=None):
    """Expands the data universe to build a cross-sectional event dataset for each league so that
    each relevant team has a presence on each match day.

    Parameters:
    -----------
        data:   pandas dataframe
                a dataframe with columns div, date, season, team, field, val
        dates:  pandas dataframe
                optional, if not all dates are represented in `data`, provide
                all relevant dates with columns div, season, date

    """
    # all game days by season and league
    if dates is None:
        agdg = data.groupby(['div', 'season'])['date'].unique().reset_index()
    else:
        agdg = dates.groupby(['div', 'season'])['date'].unique().reset_index()

    # teams by season for each league
    team_univ = pd.DataFrame(data.loc[:, 'team'].unique(), columns={'team'})
    team_univ = data.groupby(['div', 'season'])['team'].unique().reset_index()
    team_univ_tmp = team_univ.apply(lambda x:
                                    pd.Series(x['team']), axis=1).stack().reset_index(level=1, drop=True)
    team_univ_tmp.name = 'team'
    team_univ = team_univ.drop('team', axis=1).join(team_univ_tmp)
    team_univ.reset_index(drop=True, inplace=True)

    # cross-sectional expansion
    res = pd.merge(agdg, team_univ,
                   on=['div', 'season'],
                   how='inner')
    tmp = res.apply(lambda x:
                    pd.Series(x['date']), axis=1).stack().reset_index(level=1, drop=True)
    tmp.name = 'date'
    res = res.drop('date', axis=1).join(tmp)

    return res



def expand_field(data, dates=None, keys=['div', 'season', 'date', 'team', 'field']):
    """
    Expands factors across the entire date spectrum so that cross-sectional analysis
    on the factor can be performed. This ensures that for every competition (eg. Premier League),
    on each play-day there is a factor for all teams.

    Parameters:
    -----------
        data:       pandas dataframe
                    a dataframe of historical factor scores (eg. goal superiority) with
                    columns div, season, team, date, field, val
        dates:      pandas dataframe
                    optional, if not all dates are represented in `data`, provide
                    all relevant dates with columns div, season, date
        keys:       list
                    keys in data & dates on which dates will be expanded (defaults to
                    ['div', 'season', 'date', 'team', 'field'])

    Details:
    --------
    - Note that the date expansion happens for each available date by league in data enabling
      cross-sectional factor building by competition

    """
    data_ed = expand_event_sphere(data=data, dates=dates)
    res = pd.DataFrame()
    for k in data['field'].unique():
        tmp = data_ed.copy()
        tmp['field'] = k
        tmp = pd.merge(tmp, data[data['field'] == k],
                       on=keys,
                       how='outer').sort_values(by='date')
        tmp = tmp.sort_values(['div', 'season', 'team', 'field', 'date']).reset_index(drop=True)
        tmp = tmp.fillna(method='ffill')
        res = res.append(tmp, ignore_index=True, sort=False)

    return res



def insert_tp1_vals(data, date_tp1='2050-01-01', by='field', append=True):
    """Inserts t+1 values so that latest observations can be used for predictions. Note
    that sometimes upcoming games are included in the source file `data` and hence only
    unique events are returned."""
    dst = np.datetime64(date_tp1)
    # for latest season get all the relevant teams
    tmp_1 = data.groupby(['div'], as_index=False)['season'].max()
    tmp_2 = data.groupby(['div', 'team'], as_index=False)['season'].max()
    # take into account all relevant keys
    if isinstance(by, str):
        byf = ['div', by]
    elif isinstance(by, list):
        byf = [i for i in by]
        byf.append('div')
    else:
        byf = 'div'

    tmp_3 = data.groupby(byf, as_index=False)['season'].max()
    # put together a synthetic df
    c0 = pd.merge(tmp_1, tmp_2, on=['div', 'season'], how='left')
    c1 = pd.merge(c0, tmp_3, on=['div', 'season'], how='inner')
    c1['date'] = dst
    c1['val'] = np.nan
    if append is True:
        # make sure no duplicates
        dfz_0 = anti_join(c1, data.drop('val', axis=1),
                          on=['div', 'season', 'team', 'field', 'date'])
        # sometimes unexpectedly there are still some leftovers on the x dataset, so make sure no duplicates
        dfz_0 = pd.merge(dfz_0, c1.drop('val', axis=1),
                         how='inner',
                         on=['div', 'season', 'team', 'field', 'date'])
        c1 = pd.concat([data, dfz_0], sort=True, axis=0)

    return(c1)



def max_event_odds_asym(data, field, team, new_field):
    """Retrieves the maximum odds for a certain event with asymmetric odds (eg. home-team win).

            Parameters:
            -----------
                data (dataframe): a dataframe with columns div, season, date, home_team, away_team, field, val
                field (list): a list with all relevant odds for the event
                team (string): home_team or away_team perspective
                new_field (string): the name to assign to the retrieved field

            Returns:
            --------
                A dataframe with all processed data is returned with the following columns:
                season | div | date | team | field | val

            """
    # filter relevant fields..
    data_ed = data.loc[data['field'].isin(field), ['date', 'div', 'season', team, 'field', 'val']]
    data_ed.rename(columns={team: 'team'}, inplace=True)
    data_ed['val'] = data_ed['val'].apply(pd.to_numeric, errors='coerce')
    # retrieve the best odds..
    max_odds = data_ed.groupby(['season', 'div', 'date', 'team']).max()['val'].reset_index()
    max_odds['field'] = new_field
    return max_odds



def max_event_odds_sym(data, field, new_field):
    """Retrieves the maximum odds for a certain event with symmetric odds (eg. home-team draw).

            Parameters:
            -----------
                data (dataframe): a dataframe with columns div, season, date, home_team, away_team, field, val
                field (list): a list with all relevant odds for the event
                new_field (string): the name to assign to the retrieved field

            Returns:
            --------
                A dataframe with all processed data is returned with the following columns:
                season | div | date | team | field | val

            """
    data_ed = data[(data['field'].isin(field))]
    data_ed['val'] = data_ed['val'].apply(pd.to_numeric, errors='coerce')
    max_odds = data_ed.groupby(['season', 'div', 'date', 'home_team', 'away_team']).max()['val'].reset_index()
    # home numbers
    max_odds_dh = max_odds.loc[:, max_odds.columns != 'away_team']
    max_odds_dh.rename(columns={'home_team': 'team'}, inplace=True)
    max_odds_dh['field'] = new_field
    # away numbers
    max_odds_da = max_odds.loc[:, max_odds.columns != 'home_team']
    max_odds_da.rename(columns={'away_team': 'team'}, inplace=True)
    max_odds_da['field'] = new_field
    max_odds_draw = pd.concat([max_odds_dh, max_odds_da], axis=0, sort=False, ignore_index=True)
    return max_odds_draw




def get_odds(data, field_home, field_away, field_draw, field_25g):
    """Retrieves the maximum odds for every game and event in an easy to handle
    and scalable long format. Certain odds are implied (losing).

    Parameters:
    -----------
        data (dataframe): a dataframe with columns div, season, date, home_team, away_team, field, val
        field_home (list): list of all odds-fields for home win
        field_away (list): list of all odds-fields for away win
        field_draw (list): list of all odds-fields for draw win
        field_25g (list): list of all odds-fields for above / below 2.5 goals win

    Returns:
    --------
        A dataframe with all processed data is returned with the following columns:
        season | div | date | team | field | val

    """

    # get the highest odds for each event type
    # -- win odds
    moh = max_event_odds_asym(data, field = field_home, team = 'home_team', new_field = 'odds_win')
    moa = max_event_odds_asym(data, field = field_away, team = 'away_team', new_field = 'odds_win')

    # -- draw odds
    mod = max_event_odds_sym(data, field = field_draw, new_field = 'odds_draw')

    # -- above / below 2.5 goals
    mog = max_event_odds_sym(data, field=field_25g, new_field='odds_25g')

    # bind all together
    moc = pd.concat([moh, moa, mod, mog], axis=0, sort=False, ignore_index=True)
    moc = moc.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)

    # # -- implied losing odds
    moc_ed = moc.pivot_table(index=['season', 'div', 'date', 'team'],
                             columns='field',
                             values='val').reset_index()
    moc_ed["odds_lose"] = 1 / (1 - (1 / moc_ed["odds_draw"] + 1 / moc_ed["odds_win"]))

    res = pd.melt(moc_ed,
                  id_vars=['div', 'season', 'date', 'team'],
                  value_name="val")

    return res



def con_gameday(data):
    """Compute the game day for every team.
    Parameters:
    -----------
        data:   pd dataframe
                a dataframe with columns div, season, date, team, field, val

    """
    data_ed = neutralise_field(data=data, field=['FTHG', 'FTAG'], na_fill=0)
    data_ed = data_ed.loc[:, ['div', 'season', 'date', 'team']]
    data_ed = data_ed.sort_values('date').reset_index(level=0, drop=True)
    data_ed['val'] = data_ed.groupby(['div', 'season', 'team']).cumcount() + 1

    return data_ed



def con_est_dates(data, k, map_date=False, div=None):
    """Compute the model re-estimation dates for each division and season. The model estimation
    dates are calculated so that every team has at least k games in between two estimation dates.

    Parameters:
    -----------
        data:       pd dataframe
                    game day data with columns season, div, date, team, val
        k:          int
                    the time lag in periods between estimation dates (eg. k=5)
        map_date:   boolean (False)
                    whether to map to original dates
        div:        string, None
                    optional, the division/league to construct the estimation dates for
    """
    if div is not None:
        data = data[data['div'].isin(div)].reset_index(drop=True)
    # retrieve game day for each team
    game_day = con_gameday(data=data)
    # calculate when teams have played k games
    data_ed = game_day.groupby(['div', 'season', 'team'])['date'].cumcount() % k
    res = game_day[data_ed == k - 1]
    res.reset_index(drop=True, inplace=True)
    # retrieve the max date after n games
    res = res.groupby(['div', 'season', 'val'])['date'].max()
    res = res.reset_index().loc[:, ['div', 'season', 'date']]
    res.rename(columns={'date': 'est_date'}, inplace=True)

    if map_date:
        res['date'] = res['est_date']
        ugd = game_day.groupby(['div', 'season'])['date'].unique().reset_index()
        ugd = ugd.explode('date').reset_index(drop=True)
        res = pd.merge(ugd, res, on=['div', 'season', 'date'], how='left')
        res['est_date'] = res.groupby('div')['est_date'].fillna(method='ffill', axis=0)

    return res






def con_date_univ(data):
    """Constructs the date universe (dates at which games are played) for every league and season.
    """
    x = data.groupby(['div', 'season'])['date'].unique().reset_index()
    y = x.apply(lambda x: pd.Series(x['date']), axis=1).stack().reset_index(level=1, drop=True)
    y.name = 'date'
    y = x.drop('date', axis=1).join(y)
    y = y.reset_index(level=0, drop=True)
    return y


def comp_score(data, metric):
    """
    Computes a cross-sectional score by league (div) at any point in time.

    Parameters:
    -----------
        data (dataframe): A dataframe with factors and columns div, season, date, team, field, val
        metric (string): Which metric to calculate (options: z-score, percentile)

    Returns:
    --------
        A dataframe with cross-sectional scores.

    """

    if metric == 'z-score':
        # calculate cross-sectional z-score
        data['val'] = data.groupby(['date', 'div'])['val'].transform(lambda x: zscore(x))
    elif metric == 'percentile':
        data['val'] = data.groupby(['date', 'div'])['val'].rank(pct=True)
    else:
        data

    return data




def comp_bucket(data, bucket_method, bucket):
    """Calculates the bucket given a cross-sectional score. Note that higher buckets are preferred.

    Parameters:
    -----------
        data (dataframe):   A dataframe with factor scores and columns div, season, date, team, field, val
        bucket_method (string): Define which construction approach to use when returning buckets. Options
                                are noise or first (default).
        bucket (int):       How many buckets to group the observations into (in ascending order)

    Details:
    --------
    Bucket:
    Equal values cannot be put into different buckets, but the # buckets are required to be
    of equal size in pd.cut. A solution is to rank first, reduce # buckets (not practical) or
    introduce a noise element. This is why the bucket_method parameter is provided.

    """

    # filter out where limited data (error when bucketing otherwise)
    lim_dt = data.groupby(['date'])['val'].count().reset_index()
    lim_dt.rename(columns={'val': 'obs'}, inplace=True)
    lim_dt2 = lim_dt.query('obs >= @bucket')
    data = pd.merge(data, lim_dt2, on='date', how='inner')
    del data['obs']

    if bucket_method == 'noise':
        data['bucket'] = data.groupby(['date'])['val']. \
            transform(lambda x: pd.qcut(x + jitter(x), q=bucket, labels=range(1, bucket + 1)))
    else:
        data['bucket'] = data.groupby(['date'])['val'].rank(method='first')
        data['bucket'] = data.groupby(['date'])['bucket']. \
            transform(lambda x: pd.qcut(x, q=bucket, labels=range(1, bucket + 1), duplicates='drop'))

    return data



def est_odds_accuracy(data, y, x):
    """Estimates odds accuracy for each team and season. Accuracy is defined here
    as F1 score to take into account unbalanced outcomes.

    Parameters:
    -----------
        data:   pd dataframe
                data with columns odds_win, odds_draw, odds_lose & val (the outcome decoded in 0/1)
    Details:
    --------
        If there is not a single event for a class, 0.5 is returned (event 50% likely).
    """
    Y = data[y].values
    X = data[x].values
    mod = LogisticRegression()
    try:
        mod.fit(X, Y)
        y_h = mod.predict(X)
        z = f1_score(Y, y_h)
    except ValueError:
        z = 0.5
    return z


def append_custom_window(data, k):
    """Appends a custom window based on the season."""
        # estimation window (k-year non-overlapping)
    ewi = pd.DataFrame(data['season'].unique())
    ewi.rename(columns={0: 'season'}, inplace=True)
    ewi['window'] = custom_window(k=k, l=len(ewi))
    data_ed = pd.merge(data, ewi, on='season', how='left')
    return data_ed


def custom_window(k, l):
    """Constructs a custom window of k non-overlapping groups given a length."""
    nper = np.int(np.ceil(l / k))
    nper = np.sort([i + 1 for i in range(0, nper, 1)] * k)
    nper = nper[::-1]
    nper = nper[(len(nper) - l):]
    return nper


def flib_list(data):
    """Retrieve a list of all feature librariies."""
    l = data['div'].unique()
    x = [i.lower().replace(" ", "_").replace("-", "_") for i in l]
    return x



def elim_na_features(data, min=0.70):
    """Eliminates features where the majority of observations are missing."""
    # fix = ['div', 'season', 'date', 'field', 'team', 'result']
    fix = ['div', 'season', 'date', 'team', 'result']
    voi = data.columns[~data.columns.isin(fix)]
    data_ = data.groupby('div')[voi].apply(lambda x: x.notna().sum() / len(x)).reset_index()
    # eliminate features that don't fullfill the minimum requirement
    rc = data_[voi] > min
    rc = fix + list(voi[rc.values[0]])
    res = data[rc]
    # eliminate features that are no longer active as of latest
    inact = res.tail(100).isna().sum(axis=0)
    inact = inact[inact >= 50].index.to_list()
    res = res.drop(inact, axis=1)
    # drop any other na's
    res = res.dropna().reset_index(level=0, drop=True)
    return res



