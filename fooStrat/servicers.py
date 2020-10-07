import pandas as pd
import numpy as np
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
    # df_fw[['season', 'div', 'home_team', 'away_team']] = \
    #     df_fw[['season', 'div', 'home_team', 'away_team']].astype(str, errors='ignore')

    # home team stats..
    df_h = df_fw.loc[:, ['season', 'div', 'date', 'home_team', away_goals, home_goals, result]]
    df_h['points'] = df_h[result].apply(lambda x: 3 if x == 'H' else (1 if x == 'D' else 0))
    df_h['res'] = df_h[result].apply(lambda x: 'w' if x == 'H' else ('d' if x == 'D' else 'l'))
    df_h.rename(columns={'home_team': 'team',
                         away_goals: 'goals_received',
                         home_goals: 'goals_scored'}, inplace=True)
    df_h = df_h.drop([result], axis=1)

    # away team stats..
    df_a = df_fw.loc[:, ['season', 'div', 'date', 'away_team', away_goals, home_goals, result]]
    df_a['points'] = df_a[result].apply(lambda x: 3 if x == 'A' else (1 if x == 'D' else 0))
    df_a['res'] = df_a[result].apply(lambda x: 'w' if x == 'A' else ('d' if x == 'D' else 'l'))
    df_a.rename(columns={'away_team': 'team',
                         away_goals: 'goals_scored',
                         home_goals: 'goals_received'}, inplace=True)
    df_a = df_a.drop([result], axis=1)

    # consolidate
    dfc = pd.concat([df_h, df_a], axis=0, sort=True)
    dfc[['goals_scored', 'goals_received']] = dfc[['goals_scored', 'goals_received']].apply(pd.to_numeric,
                                                                                            errors='coerce')

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
        cumsum().reset_index(level=0, drop=True)
    dfc_agg_wdl = pd.concat([dfc_agg_wdl[['date', 'div', 'season', 'team']], dfc_agg_wdlc], axis=1)

    # rename columns
    dfc_agg_wdl.rename(columns={'w': 'wins', 'l': 'losses', 'd': 'draws'}, inplace=True)

    # add number of wins, draws & losses to standings
    res = pd.merge(dfc_tot_pts_ed, dfc_agg_wdl, on=['div', 'season', 'team', 'date'], how='left')

    # rankings
    res['rank'] = res.groupby(['div', 'season', 'date'])['points'].rank(ascending=False,
                                                                        method='first').reset_index(drop=True)

    # verify
    # a = res.query("div=='E0' & season=='2019' & team=='liverpool'")

    return res




def neutralise_field(data, field, field_name=None, field_numeric=True, column_field=True):
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
    data_ed = data[(data['field'].isin(field))].copy()
    if field_numeric == True:
        data_ed['val'] = pd.to_numeric(data_ed.loc[:, 'val'], errors='coerce')

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


def expand_field(data, impute=False, date_univ=None):
    """
    Expands factors across the entire date spectrum so that cross-sectional analysis
    on the factor can be performed. This means that for every competition (eg. Premier League),
    on each play-day there is a factor for all teams.

    Parameters:
    -----------
        data:       pandas dataframe
                    A dataframe of historical factor scores (eg. goal superiority) with
                    columns div, season, team, date, field, val
        impute:     boolean, default False
                    Whether to impute values for each date for missing data
        date_univ:  pandas dataframe
                    Optional, a dataframe with date universe by div & season. Used when
                    the date universe in data does not contain all actual game dates

    Details:
    --------
    - Note that the date expansion happens for each available date in data enabling cross-sectional factor
    building by competition
    - Note that imputation is performed by competition

    """
    res = pd.DataFrame()
    fields = data['field'].unique()
    for k in fields:
        df = data.query("field==@k").reset_index(drop=True)
        dfe = expand_field_single(data=df, impute=impute, date_univ=date_univ)
        res = res.append(dfe, ignore_index=True, sort=False)
    return res



def expand_field_single(data, impute=False, date_univ=None):
    """Same as for `expand_field`"""
    gf = data['div'].unique()
    res = pd.DataFrame()
    for i in gf:
        data_f = data.query('div==@i')
        data_ed = data_f.pivot_table(index=['div', 'date', 'season', 'field'],
                                     columns='team',
                                     values='val').reset_index()

        if date_univ is None:
            # date universe
            date_univ_rel = pd.DataFrame(data.loc[:, 'date'].unique(), columns={'date'}).sort_values(by='date')
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
        data_edm = data_edm.fillna(method='ffill') # note that all teams ever played are included
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
        res = res.append(fexp, ignore_index=True, sort=False)

    if impute is True:
        res['val'] = res.groupby(['date', 'div'])['val'].transform(lambda x: x.fillna(x.mean()))

    # remove na where no data at all
    res = res[res['val'].notna()].sort_values('date').reset_index(drop=True)

    return res



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




def fodds(data, field_home, field_away, field_draw):
    """Retrieves the maximum odds for every game and event in an easy to handle
    and scalable long format.

    Parameters:
    -----------
        data (dataframe): a dataframe with columns div, season, date, home_team, away_team, field, val
        field_home (list): list of all odds-fields for home win
        field_away (list): list of all odds-fields for away win
        field_draw (list): list of all odds-fields for draw win

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

    # bind all together
    moc = pd.concat([moh, moa, mod], axis=0, sort=False, ignore_index=True)
    moc = moc.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)

    # -- implied losing odds
    moc_ed = moc.pivot_table(index=['season', 'div', 'date', 'team'],
                             columns='field',
                             values='val').reset_index()
    moc_ed["odds_lose"] = 1 / (1 - (1 / moc_ed["odds_draw"] + 1 / moc_ed["odds_win"]))

    res = pd.melt(moc_ed,
                  id_vars=['div', 'season', 'date', 'team'],
                  value_name="val")

    return res



def con_est_dates(data, k):
    """Compute the model estimation dates for each division and season. The model estimation
    dates are calculated so that every team has at least k games in between two estimation dates.

    Parameters:
    -----------
        data:   pd dataframe
                game day data with columns season, div, date, team, val
        k:      int
                the time lag in periods between estimation dates (eg. k=5)
    """

    data_ed = data.groupby(['season', 'team'])['date'].cumcount() % k
    res = data[data_ed == k - 1]
    res.reset_index(drop=True, inplace=True)
    # retrieve the max date after n games
    res = res.groupby(['div', 'season', 'val'])['date'].max()
    res = res.reset_index().loc[:, ['div', 'season', 'date']]
    return res


def con_gameday(data):
    """Compute the game day for every team.
    Parameters:
    -----------
        data:   pd dataframe
                a dataframe with columns div, season, date, team, field, val

    """
    data_ed = neutralise_field(data=data, field=['FTHG', 'FTAG'])
    data_ed = data_ed.loc[:, ['div', 'season', 'date', 'team']]
    data_ed = data_ed.sort_values('date').reset_index(level=0, drop=True)
    data_ed['val'] = data_ed.groupby(['div', 'season', 'team']).cumcount() + 1

    return data_ed


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
