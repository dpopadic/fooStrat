import pandas as pd
import numpy as np
import os

# FUNCTIONS TO SUPPORT THE RUNNING OF THE PROJECT ------------------------------------

def ret_xl_cols(file_names, id_col):
    """Returns all available columns across all tabs and multiple excel files.

    Parameters:
    -----------
        file_names (list): a list with file names to examine (eg.
                           ['all-euro-data-2002-2003.xls', 'all-euro-data-2017-2018.xlsx'])
        id_col (string): the key column in each tab (eg. 'Div')

    Returns:
    --------
    A list of all available columns.

    """
    df_cols = pd.DataFrame()
    for f in file_names:
        df0 = pd.read_excel(f, sheet_name=None)
        for key, i in df0.items():
            seas = f[23:32]
            if (i.shape[0] == 0):
                val = np.nan
            else:
                val = i.loc[1, id_col]
            df_tmp = pd.DataFrame({"field": i.columns.values, id_col: val, "season": seas})
            df_cols = df_cols.append(df_tmp, ignore_index=True, sort=False)
    return(df_cols)


def comp_league_standing(data, season=None, home_goals='FTHG', away_goals='FTAG', result='FTR'):
    """Computes the standings, ranks, goals etc. for a single or multiple divisions by
    season. The input table therefore needs to have the following columns:
    div, season, date, home_team, away_team, field, val

    Parameters:
    -----------
    data (dataframe): a dataframe with columns div, season, date, home_team, away_team, field, val
    season (list): a list of values in season for which to calculate standings (defaults to None in which case
    standings for all seasons are calculated)

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
    df_fw[['season', 'div', 'home_team', 'away_team']] = \
        df_fw[['season', 'div', 'home_team', 'away_team']].astype(str, errors='ignore')

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

    # consolidate..
    dfc = pd.concat([df_h, df_a], axis=0, sort=True)
    dfc[['goals_scored', 'goals_received']] = dfc[['goals_scored', 'goals_received']].apply(pd.to_numeric,
                                                                                            errors='coerce')
    dfc_tot_pts = dfc.groupby(by=['div', 'season', 'team'])[['points', 'goals_scored', 'goals_received']].sum()
    dfc_tot_pts = dfc_tot_pts.reset_index()

    # number of wins..
    df_wdl = dfc.loc[:, ['season', 'div', 'date', 'team', 'res', 'points']]
    dfc_agg_wdl = df_wdl.pivot_table(index=['div', 'season', 'team'],
                                     columns='res',
                                     values='points',
                                     aggfunc='count').reset_index()

    # add number of wins to standings..
    tbl = pd.merge(dfc_tot_pts, dfc_agg_wdl, on=['div', 'season', 'team'], how='left')

    # rankings..
    tbl['rank'] = tbl.groupby(['div', 'season'])['points'].rank(ascending=False,
                                                                method='first').reset_index(drop=True)
    return(tbl)



def process_data_major(fi_nm, extra_key, key_cols, key_cols_map):
    """Processes the structured data that is stored in tabs in multiple excel files and puts them together tidied up.
    The excel files need not to have the same fields/columns but they do need to have the key columns present. Key
    columns are: Div | Date | HomeTeam | AwayTeam

    Parameters:
    -----------
        fi_nm (list): a list with names of all excel files that should be processed
        extra_key (dataframe): a dataframe with columns fi_nm, season that assigns a key to each excel file name so
        that later on one knows from which source the data came from
        key_cols (dict): a dictionary specifying the key columns and the output names of these keys
        key_cols_map (dict): in case that key columns can have 2 different names for a single key column across
        multiple files, specify the key column mapping here (see Details for more)

    Returns:
    --------
        A dataframe with all processed data is returned with the following columns:
        season | div | date | home_team | away_team | field | val

    Example:
    --------
    fi_nm = ['src_data/all-euro-data-2017-2018.xlsx', 'src_data/all-euro-data-1999-2000.xls']
    extra_key = pd.DataFrame({'fi_nm':fi_nm, 'season':[i[23:32] for i in fi_nm]})
    print(extra_key)
                                       fi_nm     season
    0  src_data/all-euro-data-2017-2018.xlsx  2017-2018
    1   src_data/all-euro-data-1999-2000.xls  1999-2000

    df = process_data_major(fi_nm, extra_key,
                                    key_cols = {'Div': 'div',
                                                'Date': 'date',
                                                'HomeTeam': 'home_team',
                                                'AwayTeam': 'away_team'},
                                    key_cols_map = {'HT': 'HomeTeam', 'AT': 'AwayTeam'})
    print(df)

               season div       date       home_team      away_team field val
    0       2017-2018  E0 2017-08-11         Arsenal      Leicester  FTHG   4
    1       2017-2018  E0 2017-08-12        Brighton       Man City  FTHG   0
    2       2017-2018  E0 2017-08-12         Chelsea        Burnley  FTHG   2
    3       2017-2018  E0 2017-08-12  Crystal Palace   Huddersfield  FTHG   0
    4       2017-2018  E0 2017-08-12         Everton          Stoke  FTHG   1

    Details:
    --------
    It can happen that the key columns have two different names for the same thing across multiple files (eg.
    HomeTeam in one file and HT in another). This is dealt with in the function, although hardcoded for now.
    The following key columns name differences are covered:
        HT and HomeTeam
        AT and AwayTeam

    """
    # add season as additional key variable..
    key_cols_l = list(key_cols.keys())
    extra_key_nm = extra_key.columns[1]
    key_cols_l.append(extra_key_nm)

    # key_cols = ['season', 'Div', 'Date', 'HomeTeam', 'AwayTeam']
    # the key columns can have 2 different symbologies..
    # key_cols_map = {'HT': 'HomeTeam', 'AT': 'AwayTeam'}
    df = pd.DataFrame()
    for f in fi_nm:
        df0 = pd.read_excel(f, sheet_name=None)
        for key, i in df0.items():
            si = extra_key[extra_key['fi_nm'] == f].iloc[0, 1]
            i[extra_key_nm] = si
            if i.shape[0] == 0:
                continue
            else:
                if sum(s in key_cols_l for s in i.columns) != len(key_cols_l):
                    i = i.rename(columns=key_cols_map)
                else:
                    df_lf = pd.melt(i,
                                    id_vars=key_cols_l,
                                    var_name='field',
                                    value_name='val').dropna()
                    df = df.append(df_lf, ignore_index=True, sort=False)
            print(si + ' league: ' + i['Div'][0])

    # rename columns to lower case..
    df = df.rename(columns=key_cols)
    return(df)



def process_data_minor(data, key_cols):
    """Processes the structured data that is stored in a single file and processes it in a tidied up way. The excel
     file does not need to have the same fields/columns but it needs to have the key columns present. Key
     columns are: Country | League | Date | Season | Home | Away

    Parameters:
    -----------
        data (ordered dict): a ordered dictionary with dataframe's with all data to be processed and at least all key
        columns
        key_cols (dict): a dictionary specifying all key columns which are:
        Country | League | Date | Season | Home | Away

    Returns:
    --------
    A dataframe with all processed data is returned with the following columns:
        season | div | date | home_team | away_team | field | val

                date  season       home_team  ... field       val             div
    0     2012-05-19    2012       Palmeiras  ...  Time  22:30:00  Brazil Serie A
    1     2012-05-19    2012    Sport Recife  ...  Time  22:30:00  Brazil Serie A
    2     2012-05-20    2012     Figueirense  ...  Time  01:00:00  Brazil Serie A
    3     2012-05-20    2012     Botafogo RJ  ...  Time  20:00:00  Brazil Serie A
    4     2012-05-20    2012     Corinthians  ...  Time  20:00:00  Brazil Serie A

    """

    # add season as additional key variable..
    key_cols_l = list(key_cols.keys())

    df = pd.DataFrame()
    for key, i in data.items():
        if i.shape[0] == 0:
            # in case of no data skip to next..
            continue
        else:
            df_lf = pd.melt(i,
                            id_vars=key_cols_l,
                            var_name='field',
                            value_name='val').dropna()
            df = df.append(df_lf, ignore_index=True, sort=False)

    # transform to appropriate shape..
    df['div'] = df['Country'] + ' ' + df['League']
    # edit due to varying whitespace..
    df['div'] = df['div'].str.strip()
    df['div'] = df['div'].replace('\s+', ' ', regex=True)
    del (df['Country'])
    del (df['League'])
    # rename existing columns..
    cmn_cols = list(set(df.columns) & set(key_cols_l))
    key_cols_av = {k: v for k, v in key_cols.items() if k in cmn_cols}
    df = df.rename(columns=key_cols_av)
    return(df)


def synchronise_data(data):
    """Synchronises the data so that all relevant fields have the same definition and
    the data is in a format that is more suited for data analysis. See details for more
    information.
    Parameters:
    -----------
        data (dataframe): a dataframe with consolidated data from various sources with columns season,
                          div, date, home_team, away_team, field, val

    Returns:
    --------
        A dataframe with synchonised data is returned with the following columns:
        season | div | date | home_team | away_team | field | val

    Details:
    --------
        The following synchronisation is performed:

        - Field Mapping
        At the moment, two different data sources are being handled by the function. The synchronisation
        involves translating fields (FTR | RES, FTHG | HG, FTAG | AG) that represent the same things but are
        named differently in those data sources.
        - Team Naming
        The team names are transformed to lower-case and whitespaces are replaced by "_".

    """
    data['field'] = data['field'].replace({'FTR': 'FTR',
                                            'Res': 'FTR',
                                            'FTHG': 'FTHG',
                                            'HG': 'FTHG',
                                            'FTAG': 'FTAG',
                                            'AG': 'FTAG'})
    data['home_team'] = data.loc[:, 'home_team'].str.replace(' ', '_').str.lower()
    data['away_team'] = data.loc[:, 'away_team'].str.replace(' ', '_').str.lower()
    return(data)



def update_data_latest(ex, new_1, new_2, season, path):
    """Updates the data with latest games. Only latest season results are updated and history is
    not changed from previous seasons.

    Parameters:
    -----------
        ex (dataframe): existing data
        new_1 (string): new latest data major leagues name
        new_2 (string): new latest data minor leagues name
        season (string): latest season for which the data is being updated (eg. '2019-2020')
        path (string): path to the data folder

    Returns:
    --------
        A message that the data has been updated. The respective data file is 'source_core.pkl'.

    """

    # major leagues recent data
    new_file = [path + new_1]
    new_key = pd.DataFrame({'fi_nm': new_file, 'season': season})
    major_latest = process_data_major(fi_nm=new_file,
                                      extra_key=new_key,
                                      key_cols={'Div': 'div',
                                                'Date': 'date',
                                                'HomeTeam': 'home_team',
                                                'AwayTeam': 'away_team'},
                                      key_cols_map={'HT': 'HomeTeam', 'AT': 'AwayTeam'})

    # minor leagues recent data
    minor_latest = pd.read_excel(path + new_2, sheet_name=None)
    minor_latest = process_data_minor(minor_latest,
                                      key_cols={'Country': 'country',
                                                'League': 'league',
                                                'Date': 'date',
                                                'Season': 'season',
                                                'Home': 'home_team',
                                                'Away': 'away_team'})

    # add major
    data = pd.merge(ex, major_latest,
                    on=['div', 'season', 'date', 'home_team', 'away_team', 'field', 'val'],
                    how='outer')
    # add minor
    data = pd.merge(data, minor_latest,
                    on=['div', 'season', 'date', 'home_team', 'away_team', 'field', 'val'],
                    how='outer')

    # data synchronisation: renaming fields so that they have the same names to make it easier
    # to process the data later in a concise way..
    data = synchronise_data(data=data)
    # store
    data.to_pickle('./pro_data/source_core.pkl')
    print("Source Data has been updated.")


def update_data_historic(path, file_desc, file_key, file_key_name, file_desc_2, file_key_name_2):
    """Updates historical data across major and minor leagues.

    Parameters:
    -----------
        path (string): source path to all the underlying data within the project (eg. where
                       'all-euro-data-2004-2005.xls' is located)
        file_desc (string): a string that is part of each file that will be examined (eg. 'all-euro_data'
                            for files that have the same structure:
                            'all-euro-data-2002-2003.xls', 'all-euro-data-2017-2018.xlsx')
        file_key (list): the range of the file name that will be used as key to describe from which file the
                         data came from. For example, in  'src_data/all-euro-data-1993-1994.xls' 1993-1994 will
                         be used as key and file_key = [23, 32]
        file_key_name (string): a string with the column name of file_key in the resulting dataframe (eg. 'season')
        file_desc_2 (string): a string for an additional file that has the same structure as the files in file_desc
                              but where all data is stored in a single file (eg. 'new_leagues_data.xlsx')
        file_key_name_2 (string): a column in the file that describes the same key that is used in file_key_name to
                                  be able to merge the different data sources by this key (eg. 'Season')

    """
    # MAJOR LEAGUES ------
    # retrieve source data full path
    src_dat_path = os.path.join(os.getcwd(), path[:-1], '')
    # all the relevant files names
    # iterate through source folder and determine which files should be loaded
    fi_nm = [path + f for f in os.listdir(src_dat_path) if f[:len(file_desc)] == file_desc]
    # map file key
    extra_key = pd.DataFrame({'fi_nm': fi_nm,
                              file_key_name: [i[file_key[0]:file_key[1]] for i in fi_nm]})
    # process data
    major = process_data_major(fi_nm, extra_key,
                               key_cols={'Div': 'div',
                                         'Date': 'date',
                                         'HomeTeam': 'home_team',
                                         'AwayTeam': 'away_team'},
                               key_cols_map={'HT': 'HomeTeam',
                                             'AT': 'AwayTeam'})

    # MINOR LEAGUES ------
    minor = pd.read_excel(path + file_desc_2, sheet_name=None)
    # process data..
    minor = process_data_minor(minor,
                               key_cols={'Country': 'country',
                                         'League': 'league',
                                         'Date': 'date',
                                         file_key_name_2: file_key_name,
                                         'Home': 'home_team',
                                         'Away': 'away_team'})

    # MERGE -------
    data_prc = pd.concat([major, minor], axis=0, sort=False)
    # data synchronisation: renaming fields so that they have the same names to make it easier
    # to process the data later in a concise way..
    data_prc = synchronise_data(data=data_prc)
    data_prc.to_pickle('./pro_data/source_core.pkl')
    print("Source Data History has been updated.")



# FACTOR CONSTRUCTION ------------------------------------------------------------------

def fgoalsup(data, field, k):
    """Calculates the goal superiority factor across divisions and seasons for each team on a
    rolling basis. Note that the factor is adjusted for lookahead bias.

    Parameters:
    -----------
        data (dataframe): a dataframe with columns div, date, season, home_team, away_team, field, val
        field (list): a list specifying the field name for home- & away-goals (eg. ['FTHG', 'FTAG'])
        k (integer): the lookback window to be used

    Returns:
    --------
        A dataframe with calculated goal-superiority factor and columns div, season, date, team, field, val

    Details:
    --------
    Goal difference provides one measure of the dominance of one football side over another in a match. The
    assumption for a goals superiority rating system, then, is that teams who score more goals and concede fewer over
    the course of a number of matches are more likely to win their next game. Typically, recent form means the last 4,
    5 or 6 matches. For example, In their last 6 games, Tottenham have scored 6 goals and conceded 9. Meanwhile, Leeds
    have scored 8 times and conceded 11 goals. Tottenham's goal superiority rating for the last 6 games is +3; for
    Leeds it is -3.

    """
    # filter relevant fields..
    data_goals = data[(data['field'].isin(field))]
    data_goals['val'] = pd.to_numeric(data_goals.loc[:, 'val'])
    # put the fields in wide format
    tmp = pd.pivot_table(data_goals,
                         index=['div', 'season', 'date', 'home_team', 'away_team'],
                         columns='field',
                         values='val').reset_index()

    # home team..
    tmp1 = tmp.loc[:, ['div', 'season', 'date', 'home_team', field[0], field[1]]]
    tmp1.rename(columns={'home_team': 'team',
                         field[0]: 'g_scored',
                         field[1]: 'g_received'}, inplace=True)
    # away team..
    tmp2 = tmp.loc[:, ['div', 'season', 'date', 'away_team', field[0], field[1]]]
    tmp2.rename(columns={'away_team': 'team',
                         field[1]: 'g_scored',
                         field[0]: 'g_received'}, inplace=True)
    # put together..
    data_goals_co = pd.concat([tmp1, tmp2], axis=0, sort=False, ignore_index=True)

    # compute stat..
    data_goals_co_i = data_goals_co.set_index('date')
    data_goals_co1 = data_goals_co_i.sort_values('date').groupby(['team'])[['g_scored', 'g_received']]. \
                    rolling(k, min_periods=1).sum().reset_index()

    data_goals_co1['val'] = data_goals_co1['g_scored'] - data_goals_co1['g_received']
    data_goals_co1.drop(['g_scored', 'g_received'], axis=1, inplace=True)
    data_fct = pd.merge(data_goals_co[['div', 'date', 'season', 'team']],
                        data_goals_co1, on=['team', 'date'],
                        how='left')
    data_fct['field'] = 'goal_superiority'
    # lag factor..
    data_fct['val'] = data_fct.groupby(['div', 'season', 'team', 'field'])['val'].shift(1)
    data_fct.dropna(inplace=True)
    return(data_fct)


def expand_field(data, group):
    """Expands factors across the entire date spectrum so that cross-sectional analysis
    on the factor can be performed.
    Parameters:
    -----------
        data (dataframe): a dataframe of historical factor scores (eg. goal superiority) with
                          columns div, season, team, date, field, val
        group (string): a string indicating for which group to expand (eg. season)

    """
    data_f = data.query('div==@group')
    data_ed = data_f.pivot_table(index=['div', 'date', 'season', 'field'],
                                 columns='team',
                                 values='val').reset_index()
    # date universe
    date_univ = pd.DataFrame(data.loc[:, 'date'].unique(), columns={'date'}).sort_values(by='date')
    # copy forward all factors
    data_ed = pd.merge(date_univ, data_ed, on='date', how='outer').sort_values(by='date')
    data_ed = data_ed.fillna(method='ffill')
    # need to filter only teams playing in the season otherwise duplicates issue
    data_ed = pd.melt(data_ed, id_vars=['div', 'season', 'date', 'field'], var_name='team', value_name='val')
    # all teams played in each  season
    tmp = data_f.groupby(['div', 'season'])['team'].unique().reset_index()
    team_seas = tmp.apply(lambda x: pd.Series(x['team']), axis=1).stack().reset_index(level=1, drop=True)
    team_seas.name = 'team'
    team_seas = tmp.drop('team', axis=1).join(team_seas)
    # expanded factors
    fexp = pd.merge(team_seas, data_ed,
                    on=['div', 'season', 'team'],
                    how='inner').sort_values(by='date').reset_index(drop=True)
    return(fexp)


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
    data_ed['val'] = pd.to_numeric(data_ed.loc[:, 'val'], errors='coerce')
    # retrieve the best odds..
    max_odds = data_ed.groupby(['season', 'div', 'date', 'team']).max()['val'].reset_index()
    max_odds['field'] = new_field
    return (max_odds)



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
    data_ed['val'] = pd.to_numeric(data_ed.loc[:, 'val'], errors='coerce')
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
    return (max_odds_draw)


# STRATEGY TESTING ------------------------------------------------------------------


def fodds(data, field_home, field_away, field_both):
    """Retrieves the maximum odds for every game and event in an easy to handle
    and scalable long format.

    Parameters:
    -----------
        data (dataframe): a dataframe with columns div, season, date, home_team, away_team, field, val
        field_asym (dict): a dictionary specifying all odds-fields for an asymmetric event (eg. home-team win)
        field_sym (dict): a dictionary specifying all odds-fields for a symmetric event (eg. draw)

    Returns:
    --------
        A dataframe with all processed data is returned with the following columns:
        season | div | date | team | field | val

    """
    # get the highest odds for each event type
    moh = max_event_odds_asym(data, field = field_home, team = 'home_team', new_field = 'odds_win')
    moa = max_event_odds_asym(data, field = field_away, team = 'away_team', new_field = 'odds_win')
    mod = max_event_odds_sym(data, field = field_both, new_field = 'odds_draw')
    # bind all together..
    moc = pd.concat([moh, moa, mod], axis=0, sort=False, ignore_index=True)
    return(moc)


def con_res(data, field):
    """
    Constructs the event result data in a manner that is readily available for back-testing.

    :param data: a dataframe with columns season, date, div, home_team, away_team, field, val
    :param field: a string that defines the event (eg. 'FTR' for full-time results)
    :return: a dataframe with results

    """
    # query relevant field
    rel_field = field
    res_tmp = data.query('field == @rel_field')
    # home team
    home = res_tmp.loc[:, ['div', 'season', 'date', 'home_team', 'val']]
    home['val'] = home.loc[:, 'val'].apply(lambda x: 1 if x == 'H' else 0)
    home['field'] = "win"
    home.rename(columns={'home_team': 'team'}, inplace=True)
    # away team
    away = res_tmp.loc[:, ['div', 'season', 'date', 'away_team', 'val']]
    away['val'] = away.loc[:, 'val'].apply(lambda x: 1 if x == 'A' else 0)
    away['field'] = "win"
    away.rename(columns={'away_team': 'team'}, inplace=True)
    # draws
    draw = res_tmp
    draw['val'] = res_tmp.loc[:, 'val'].apply(lambda x: 1 if x == 'D' else 0)
    draw['field'] = 'draw'
    draw = pd.melt(draw, id_vars=['div', 'season', 'date', 'field', 'val'], value_name='team')
    draw.drop(['variable'], axis=1, inplace=True)
    # bring together
    res = pd.concat([home, away, draw], axis=0, sort=True)
    return (res)


def comp_pnl(positions, odds, results, event, stake):
    """Calculates the PnL of a factor. Note that the factor needs to be adjusted for lookahead bias.

    Parameters:
    -----------
        positions (dataframe): a dataframe with intended positions with season, div, date, team
        odds (dataframe): a dataframe with odds data and columns season, div, date, team, field, val
        results (dataframe): a dataframe with results and columns season, div, date, team, field, val
        event (string): a string defining the event (eg. 'win')
        stake (double): the stake for each bet (eg. 10)

    Returns:
    --------
        A dataframe with profit and loss data is returned with the following columns:
        season | div | date | team | field | val | res | payoff | payoff_cum

    """

    # define helper function
    def f0(x, stake):
        if x[1] == 0:
            if np.isnan(x[0]):
                z = np.nan
            else:
                z = -1 * stake
        elif x[1] == 1:
            z = (x[0] - 1) * stake
        else:
            z = 0
        return z

    # add odds to positions
    pay = pd.merge(positions, odds, on=['div', 'season', 'date', 'team'], how='left')
    # retrieve the right odds
    res_0 = results.query('field == @event')
    res_0.drop(['field'], axis=1, inplace=True)
    res_0.rename(columns={'val': 'res'}, inplace=True)
    # add the actual result
    payres = pd.merge(pay, res_0, on=['div', 'season', 'date', 'team'], how='left')
    # calculate pnl
    payres['payoff'] = payres.loc[:, ['val', 'res']].apply(f0, stake=stake, axis=1)
    # cumulative pnl
    payres['payoff_cum'] = payres.loc[:, 'payoff'].cumsum(skipna=True)
    return (payres)



# MAPPING TABLES ---------------------------------------------------------------------------
# division mapping
competition = {'E0':'England Premier League',
               'E1':'England Championship League',
               'E2':'England Football League One',
               'E3':'England Football League Two',
               'EC':'England National League',
               'SC0':'Scottish Premiership',
               'SC1':'Scottish Championship',
               'SC2':'Scottish League One',
               'SC3':'Scottish League Two',
               'D1':'German Bundesliga',
               'D2':'German 2. Bundesliga',
               'SP1':'Spain La Liga',
               'SP2':'Spain Segunda Division',
               'I1':'Italy Serie A',
               'I2':'Italy Serie B',
               'F1':'France Ligue 1',
               'F2':'France Ligue 2',
               'N1':'Dutch Eredivisie',
               'B1':'Belgian First Division A',
               'P1':'Portugal',
               'T1':'Turkey Süper Lig',
               'G1':'Greek Super League',
               'Argentina Superliga':'Argentina Superliga',
               'Austria Tipico Bundesliga':'Austria Tipico Bundesliga',
               'Brazil Serie A':'Brazil Serie A',
               'China Super League':'China Super League',
               'Denmark Superliga':'Denmark Superliga',
               'Finland Veikkausliiga':'Finland Veikkausliiga',
               'Ireland Premier Division':'Ireland Premier Division',
               'Japan J-League':'Japan J-League',
               'Japan J1 League':'Japan J1 League',
               'Mexico Liga MX':'Mexico Liga MX',
               'Norway Eliteserien':'Norway Eliteserien',
               'Poland Ekstraklasa':'Poland Ekstraklasa',
               'Romania Liga 1':'Romania Liga 1',
               'Russia Premier League':'Russia Premier League',
               'Sweden Allsvenskan':'Sweden Allsvenskan',
               'Switzerland Super League':'Switzerland Super League',
               'USA MLS':'USA MLS'}
ml_map = pd.DataFrame(list(competition.items()), columns=['Div', 'Competition'])

# odds mapping
# home win
oh = ['B365H', 'BSH', 'BWH', 'GBH', 'IWH', 'LBH', 'PSH', 'PH', 'SOH', 'SBH', 'SJH', 'SYH',
      'VCH', 'WHH', 'BbMxH', 'BbAvH', 'MaxH', 'AvgH']
# away win
oa = ['B365A', 'BSA', 'BWA', 'GBA', 'IWA', 'LBA', 'PSA', 'PA', 'SOA', 'SBA', 'SJA', 'SYA',
      'VCA', 'WHA', 'BbMxA', 'BbAvA', 'MaxA', 'AvgA']
# draw
od = ['B365D', 'BSD', 'BWD', 'GBD', 'IWD', 'LBD', 'PSD', 'PD', 'SOD', 'SBD', 'SJD', 'SYD',
      'VCD', 'WHD', 'BbMxD', 'BbAvD', 'MaxD', 'AvgD']
# above 2.5
atp5 = ['BbMx>2.5', 'BbAv>2.5', 'GB>2.5', 'B365>2.5', 'P>2.5', 'Max>2.5', 'Avg>2.5']
# below 2.5
btp5 = ['BbMx<2.5', 'BbAv<2.5', 'GB<2.5', 'B365<2.5', 'P<2.5', 'Max<2.5', 'Avg<2.5']
odds_fields = {'odds_home_win':oh,
               'odds_away_win':oa,
               'odds_draw_win':od,
               'odds_under_25_goal':btp5,
               'odds_above_25_goal': atp5}

