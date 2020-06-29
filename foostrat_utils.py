import pandas as pd
import numpy as np
from scipy.stats import zscore
import os
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression

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
    return df_cols


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
    return df


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
    return df


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
        - Season Mapping
        The seasons are defined differently depending which league you look at (eg. 2019 for Brasil Serie A vs
        2019-2020 for England Premier League (E0)). Season synchronisation is performed to bring all leagues and
        seasons on the same denominator.

    """
    # fields ---------------------
    data['field'] = data['field'].replace({'FTR': 'FTR',
                                            'Res': 'FTR',
                                            'FTHG': 'FTHG',
                                            'HG': 'FTHG',
                                            'FTAG': 'FTAG',
                                            'AG': 'FTAG'})

    # teams ----------------------
    data['home_team'] = data.loc[:, 'home_team'].str.replace(' ', '_').str.lower()
    data['away_team'] = data.loc[:, 'away_team'].str.replace(' ', '_').str.lower()

    # seasons --------------------
    # unique seasons
    Se = pd.DataFrame(data.loc[:, 'season'].unique(), columns=['season'])
    # make sure it's a string
    Se["season_new"] = Se["season"].astype("|S")
    # 2-year season description to 1st-year season description..
    Se['season_new'] = Se.loc[:, 'season_new'].apply(lambda x: x[:4] if len(x) > 4 else x)
    Se['season_new'] = Se['season_new'].apply(pd.to_numeric, errors='coerce')

    # add new season definition to the data..
    res = pd.merge(data, Se, on='season', how='left')
    res.drop(['season'], axis=1, inplace=True)
    res.rename(columns={'season_new': 'season'}, inplace=True)

    # exception alterations: there're some leagues where the 4-digit season description is forward-looking
    div_season_spec = 'Ireland Premier Division'
    res.loc[(res['div'] == div_season_spec), 'season'] = res.loc[(res['div'] == div_season_spec), 'season'].values - 1
    res = res.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)

    return res



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
    # data synchronisation: renaming fields so that they have the same names to make it easier
    # to process the data later in a concise way..
    major_latest = synchronise_data(data=major_latest)

    # minor leagues recent data
    minor_latest = pd.read_excel(path + new_2, sheet_name=None)
    minor_latest = process_data_minor(minor_latest,
                                      key_cols={'Country': 'country',
                                                'League': 'league',
                                                'Date': 'date',
                                                'Season': 'season',
                                                'Home': 'home_team',
                                                'Away': 'away_team'})
    minor_latest = synchronise_data(data=minor_latest)

    # add major
    data = pd.merge(ex, major_latest,
                    on=['div', 'season', 'date', 'home_team', 'away_team', 'field', 'val'],
                    how='outer')
    # add minor
    data = pd.merge(data, minor_latest,
                    on=['div', 'season', 'date', 'home_team', 'away_team', 'field', 'val'],
                    how='outer')
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
    major = process_data_major(fi_nm=fi_nm, extra_key=extra_key,
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



def update_flib(data, dir='./pro_data/', update = True):
    """Builds or updates the factor library.

    Parameters:
    -----------
        data:   list
                a list of pandas dataframe's with factors across leagues
        dir:    str, default pro_data
                a directory where to store the factor library
        update: boolean, default True
                Whether to update or create new factor library

    Details:
    --------
    Note that when update is True, it's assumed that there is a factor library
    present by league.

    """
    data_ed = pd.concat(data, axis=0, sort=False, ignore_index=True)
    # i = 'F1'
    for i in data_ed.loc[:, 'div'].unique():

        data_new = data_ed.query("div==@i")
        ik = i.lower().replace(" ", "_").replace("-", "_")

        if update is False:
            data_new.to_pickle(dir + 'flib_' + ik + '.pkl')
        else:
            data_ex = pd.read_pickle(dir + 'flib_' + ik + '.pkl')
            # find what is new
            # 1st identify mutual observations
            data_mut = pd.merge(data_new.loc[:, ['div', 'season', 'team', 'date', 'field']],
                                data_ex.loc[:, ['div', 'season', 'team', 'date', 'field']],
                                on=['div', 'season', 'team', 'date', 'field'],
                                how="inner")
            # remove already existing from source
            data_res = anti_join(x=data_ex,
                                 y=data_mut,
                                 on=['div', 'season', 'team', 'date', 'field'])
            # add new data
            res = pd.concat([data_res, data_new], axis=0, sort=True, ignore_index=True)
            res = res.reset_index(drop=True)
            res.to_pickle(dir + 'flib_' + ik + '.pkl')

        print("Factor library for " + i + " is updated.")



def delete_flib(field, path='pro_data/'):
    """Delete fields from the factor library.

    Parameters:
    -----------
        field:  str
                the field(s) to be deleted from the factor library
        dir:    str, default pro_data
                a directory where to store the factor library

    """
    # retrieve source path
    dat_path = os.path.join(os.getcwd(), path[:-1], '')
    files = [path + f for f in os.listdir(dat_path) if f[:5] == "flib_"]
    # i = 0
    for i in range(len(files)):
        data_ex = pd.read_pickle(files[i])
        res = data_ex.query("field not in @field")
        res.to_pickle(files[i])

    print("Factor library is updated.")


# FACTOR CONSTRUCTION ------------------------------------------------------------------


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


def fhome(data):
    """
    Reshapes the data where columns define whether it is a home match or away match to a home/away neutralised
    object so that the data can be used in a more scalable way.

    Parameters:
    -----------
        data(dataframe): a dataframe with columns div, date, season, home_team, away_team, field, val

    Returns:
    --------
        A data.frame identifying the home- & away-teams.

    Example:
    --------
    fhome(data)
                            div     season       date      team     home
        0                      F1  1993-1994 1993-07-23    nantes     1
        1                      F1  1993-1994 1993-07-23    monaco     0
        2                      F1  1993-1994 1993-07-24  bordeaux     1
        3                      F1  1993-1994 1993-07-24      caen     1
        4                      F1  1993-1994 1993-07-24     lille     1

    """
    data_cf = data.query('field=="FTR"').loc[:, ['div', 'season', 'date', 'home_team', 'away_team']]

    # home
    tmp1 = data_cf.drop('away_team', axis=1)
    tmp1.rename(columns={'home_team': 'team'}, inplace=True)
    tmp1['val'] = 1

    # away
    tmp2 = data_cf.drop('home_team', axis=1)
    tmp2.rename(columns={'away_team': 'team'}, inplace=True)
    tmp2['val'] = 0

    res = pd.concat([tmp1, tmp2], axis=0, sort=False, ignore_index=True)
    res['field'] = "home"
    res = res.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)

    return res


def feat_goalbased(data, k):
    """Compute goal based factors. Goal based factors are:

        - goal superiority rating
        - average goals per game
        - failed to score
        - points per game

    These statistics are calculated over the last 5 games for each team.

    Parameters:
    -----------
    data:       pandas dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val
    k:          integer
                the lookback window to be used

    """
    # neutralise data..
    data_goals_co = neutralise_field(data,
                                     field=['FTHG', 'FTAG'],
                                     field_name=['g_scored', 'g_received'],
                                     field_numeric=True,
                                     column_field=True)

    # compute stat..
    data_goals_co_i = data_goals_co.set_index('date')

    # ----- feature: goal superiority (last 5)
    feat_gsup = data_goals_co_i.sort_values('date').groupby(['team'])[['g_scored', 'g_received']]. \
        rolling(k, min_periods=1).sum().reset_index()
    feat_gsup['val'] = feat_gsup['g_scored'] - feat_gsup['g_received']
    feat_gsup.drop(['g_scored', 'g_received'], axis=1, inplace=True)
    feat_gsup['field'] = 'goal_superiority'

    # ----- feature: average goals per game (last 5)
    feat_agpg = data_goals_co_i.sort_values('date').groupby(['team'])['g_scored']. \
        rolling(k, min_periods=1).mean().reset_index()
    feat_agpg.rename(columns={'g_scored': 'val'}, inplace=True)
    feat_agpg['field'] = 'avg_goal_scored'

    # ----- feature: failed to score (last 5)
    feat_fts = data_goals_co_i.copy()
    feat_fts['val'] = feat_fts['g_scored'].apply(lambda x: 1 if x == 0 else 0)
    feat_fts = feat_fts.sort_values('date').groupby(['team'])['val'].rolling(k, min_periods=1).sum().reset_index()
    feat_fts['field'] = 'failed_scoring'

    # ----- feature: points per game (last 5)
    feat_ppg = data_goals_co_i.copy()
    feat_ppg['val'] = feat_ppg.loc[:, ['g_scored', 'g_received']]. \
        apply(lambda x: 3 if x[0] > x[1] else (1 if x[0] == x[1] else 0), axis=1)
    feat_ppg = feat_ppg.sort_values('date').groupby(['team'])['val']. \
        rolling(k, min_periods=1).sum().reset_index()
    feat_ppg['val'] = feat_ppg['val'] / k
    feat_ppg['field'] = 'points_per_game'

    # bind all together
    feat_all = pd.concat([feat_gsup, feat_agpg, feat_fts, feat_ppg], axis=0, sort=True)
    data_fct = pd.merge(data_goals_co[['div', 'date', 'season', 'team']],
                        feat_all, on=['team', 'date'],
                        how='left')

    # lag factor..
    data_fct.sort_values(['team', 'date', 'field'], inplace=True)
    data_fct['val'] = data_fct.groupby(['team', 'field'])['val'].shift(1)

    # identify promoted/demoted teams & neutralise score for them..
    team_chng = newcomers(data=data_fct)
    res = neutralise_scores(data=data_fct, teams=team_chng, n=k - 1)
    # check: a = res.query("div=='E0' & season=='2019' & team=='sheffield_united'").sort_values(['date'])
    # res['val'] = res.groupby(['div', 'season', 'team', 'field'])['val'].shift(1)
    # res.dropna(inplace=True)
    return res



def fgoalsup(data, field, field_name, k):
    """Calculates the goal superiority factor across divisions and seasons for each team on a
    rolling basis. Note that the factor is adjusted for lookahead bias.

    Parameters:
    -----------
        data (dataframe): a dataframe with columns div, date, season, home_team, away_team, field, val
        field (list): a list specifying the field name for home- & away-goals (eg. ['FTHG', 'FTAG']) in this order
        field_name (list): a list with new field name for fields (eg. ['g_scored', 'g_received'])
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
    # neutralise data..
    data_goals_co = neutralise_field(data,
                                     field=field,
                                     field_name=field_name,
                                     field_numeric=True,
                                     column_field=True)

    # compute stat..
    data_goals_co_i = data_goals_co.set_index('date')
    data_goals_co1 = data_goals_co_i.sort_values('date').groupby(['team'])[field_name]. \
                    rolling(k, min_periods=1).sum().reset_index()

    data_goals_co1['val'] = data_goals_co1[field_name[0]] - data_goals_co1[field_name[1]]
    data_goals_co1.drop(field_name, axis=1, inplace=True)
    data_fct = pd.merge(data_goals_co[['div', 'date', 'season', 'team']],
                        data_goals_co1, on=['team', 'date'],
                        how='left')
    data_fct['field'] = 'goal_superiority'
    # lag factor..
    data_fct.sort_values(['team', 'date'], inplace=True)
    data_fct['val'] = data_fct.groupby(['team', 'field'])['val'].shift(1)

    # identify promoted/demoted teams & neutralise score for them..
    team_chng = newcomers(data=data_fct)
    res = neutralise_scores(data=data_fct, teams=team_chng, n=k-1)
    # check: res.query("div=='E0' & season=='2019' & team=='sheffield_united'").sort_values(['date'])
    # res['val'] = res.groupby(['div', 'season', 'team', 'field'])['val'].shift(1)
    # res.dropna(inplace=True)
    return res



def fform(data, field, type, k=5):
    """Computes the form factor for each team. The form is derived by looking at the last 5 wins/losses
    for each team and calculating the number of points achieved over those games (3 for win, 1 for draw &
    0 for loss).

    Parameters:
    -----------
        data:   pandas dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val
        field:  str
                the relevant field in the field column of data to the calculate the factor
        type:   str
                whether to calculate factor for home, away or all matches
        k:      int, default 5
                the number of games to look at when calculating the form

    """

    data_ed = data.query('field==@field').loc[:, ['div',
                                                  'season',
                                                  'date',
                                                  'home_team',
                                                  'away_team',
                                                  'val']]

    h = data_ed.loc[:, 'val'].apply(lambda x: 3 if x == 'H' else (1 if x == 'D' else 0))
    h = pd.concat([data_ed.loc[:, ['div',
                                   'season',
                                   'date',
                                   'home_team']].rename(columns={'home_team': 'team'}), h], axis=1)

    a = data_ed.loc[:, 'val'].apply(lambda x: 3 if x == 'A' else (1 if x == 'D' else 0))
    a = pd.concat([data_ed.loc[:, ['div',
                                   'season',
                                   'date',
                                   'away_team']].rename(columns={'away_team': 'team'}), a], axis=1)

    if type=='home':
        ha = h.reset_index(drop=True)
    elif type=='away':
        ha = a.reset_index(drop=True)
    elif type=='all':
        ha = pd.concat([h, a], axis=0).reset_index(drop=True)

    ha_ed = ha.set_index('date')
    ha_ed = ha_ed.sort_values('date').groupby('team')['val'].rolling(k, min_periods=1).sum().reset_index()
    # add back the other data
    ha_fin = pd.merge(ha[['div', 'date', 'season', 'team']],
                      ha_ed, on=['team', 'date'],
                      how='left')

    ha_fin['field'] = 'form' + '_' + type
    # lag factor
    ha_fin = ha_fin.sort_values(['team', 'date']).reset_index(drop=True)
    ha_fin['val'] = ha_fin.groupby(['team', 'field'])['val'].shift(1)
    # neutralise for new entrants
    team_chng = newcomers(data=ha_fin)
    res = neutralise_scores(data=ha_fin, teams=team_chng, n=k-1)
    return res


def feat_resbased(data):
    """Calculates result based features. These are:
        - form home
        - form away
        - form overall

    Parameters:
    -----------
    data:       pandas dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val
    k:          integer
                the lookback window to be used

    """
    fh = fform(data=data, field="FTR", type="home")
    fa = fform(data=data, field="FTR", type="away")
    ftot = fform(data=data, field="FTR", type="all")
    feat_all = pd.concat([fh, fa, ftot], axis=0, sort=True)
    return feat_all


def feat_stanbased(data):
    """Calculates standings based factors. These are:
        - position residual
        - points residual

        Note that the normalisation takes place within the function here so that the
        standings based factors can be calculated.
    """

    df_0 = data[(data.field == 'FTR') | (data.field == 'FTHG') | (data.field == 'FTAG')]
    # compute rolling league standings
    df_1 = comp_league_standing(data=df_0, home_goals='FTHG', away_goals='FTAG', result='FTR')
    df_1.dtypes

    # points advantage
    tmp_1 = df_1.loc[:, ['div', 'season', 'date', 'team', 'points']]
    tmp_1['field'] = "points_advantage"
    tmp_1.rename(columns={'points': 'val'}, inplace=True)

    # rank position
    tmp_2 = df_1.loc[:, ['div', 'season', 'date', 'team', 'rank']]
    tmp_2['field'] = "rank_position"
    tmp_2.rename(columns={'rank': 'val'}, inplace=True)

    res = pd.concat([tmp_1, tmp_2],
                    axis=0,
                    sort=False,
                    ignore_index=True)

    # lag factor
    res = res.sort_values(['team', 'date']).reset_index(drop=True)
    res['val'] = res.groupby(['team', 'field'])['val'].shift(1)

    return res



def expand_field(data, impute=False):
    """Expands factors across the entire date spectrum so that cross-sectional analysis
    on the factor can be performed. This means that for every competition (eg. Premier League),
    on each play-day there is a factor for all teams.

    Parameters:
    -----------
        data:   pandas dataframe
                A dataframe of historical factor scores (eg. goal superiority) with
                columns div, season, team, date, field, val
        impute: boolean, default False
                Whether to impute values for each date for missing data

    Details:
    --------
    - Note that the date expansion happens for each available date in data enabling cross-sectional factor
    building by competition
    - Note that imputation is performed by competition

    """
    gf = data['div'].unique()
    res = pd.DataFrame()
    for i in gf:
        data_f = data.query('div==@i')
        data_ed = data_f.pivot_table(index=['div', 'date', 'season', 'field'],
                                     columns='team',
                                     values='val').reset_index()
        # date universe
        date_univ = pd.DataFrame(data.loc[:, 'date'].unique(), columns={'date'}).sort_values(by='date')
        # copy forward all factors
        data_ed = pd.merge(date_univ,
                           data_ed,
                           on='date',
                           how='outer').sort_values(by='date')
        data_ed = data_ed.fillna(method='ffill') # note that all teams ever played are included

        aa=data_ed.dropna()

        # need to filter only teams playing in the season otherwise duplicates issue
        data_ed = pd.melt(data_ed,
                          id_vars=['div', 'season', 'date', 'field'],
                          var_name='team',
                          value_name='val')
        # drop na in fields
        data_ed = data_ed[data_ed['field'].notna()]

        # all teams played in each  season
        tmp = data_f.groupby(['div', 'season'])['team'].unique().reset_index()
        team_seas = tmp.apply(lambda x: pd.Series(x['team']), axis=1).stack().reset_index(level=1, drop=True)
        team_seas.name = 'team'
        team_seas = tmp.drop('team', axis=1).join(team_seas)
        # expanded factors
        fexp = pd.merge(team_seas, data_ed,
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
    moc = moc.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)
    return moc



def con_res_gd(data, field):
    """Constructs the goals difference results object.

    Parameters:
    -----------
        data (dataframe):   a dataframe with columns season, date, div, home_team, away_team, field, val
        field (list):       a string that defines the goals scored & goals received fields in data from home team's
                            perspective (eg. ['FTHG', 'FTAG'])

    Returns:
    --------
        A dataframe of goal differences for each game and team.

    Example:
    --------
                                div  season       date                team  val
        0       Argentina Superliga    2012 2012-08-03     arsenal_sarandi  1.0
        1       Argentina Superliga    2012 2012-08-04      colon_santa_fe  1.0
        2       Argentina Superliga    2012 2012-08-04             quilmes  3.0
        3       Argentina Superliga    2012 2012-08-04         racing_club  0.0
        4       Argentina Superliga    2012 2012-08-04     velez_sarsfield  3.0

    """
    # neutralise field for teams
    field_name = ['g_scored', 'g_received']
    nf0 = neutralise_field(data=data, field=field, field_name=field_name, field_numeric=True, column_field=True)
    nf0['val'] = nf0[field_name[0]] - nf0[field_name[1]]
    del nf0[field_name[0]]
    del nf0[field_name[1]]
    return nf0



def con_res_wd(data, field):
    """
    Constructs the event result data in a manner that is readily available for back-testing.

    :param data: a dataframe with columns season, date, div, home_team, away_team, field, val
    :param field: a string that defines the event (eg. 'FTR' for full-time results)
    :return: a dataframe with results

    Parameters:
    -----------
        data (dataframe):       a dataframe with columns season, date, div, home_team, away_team, field, val
        field (string):         a string that defines the event (eg. 'FTR' for full-time results)

    Returns:
    --------
        A dataframe of results 0/1 with fields win, draw for each team.

    Example:
    --------
                      date  div field  season      team  val
        0       1993-07-23   F1   win    1993    nantes    1
        1       1993-07-23   F1   win    1993    monaco    0
        2       1993-07-23   F1  draw    1993    nantes    0
        3       1993-07-23   F1  draw    1993    monaco    0
        4       1993-07-24   F1   win    1993  bordeaux    1

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
    draw = res_tmp.copy()
    draw['val'] = res_tmp.loc[:, 'val'].apply(lambda x: 1 if x == 'D' else 0)
    draw['field'] = 'draw'
    draw = pd.melt(draw, id_vars=['div', 'season', 'date', 'field', 'val'], value_name='team')
    draw.drop(['variable'], axis=1, inplace=True)
    # bring together
    res = pd.concat([home, away, draw], axis=0, sort=True)
    res = res.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)
    return res



def con_res(data, obj, field):
    """Constructs results objects that are required for testing.

    Parameters:
    -----------
        data (dataframe):       a dataframe with columns season, date, div, home_team, away_team, field, val
        obj (string):           the object to construct:
                                    gd:     goals difference by game
                                    wd:     win or draw by game
        field (list or string): a string that defines the event for the object (eg. 'FTR' when wd or
                                ['FTHG', 'FTAG'] when gd)

    Returns:
    --------
        A dataframe with the results in optimal shape.

    """

    if obj == "wd":
        if type(field) is list:
            field = field[0]
        res = con_res_wd(data=data, field=field)
    elif obj == "gd":
        res = con_res_gd(data=data, field=field)

    return res



def comp_mispriced(prob, odds, prob_threshold, res_threshold):
    """
    Parameters
    ----------
    prob:   pandas dataframe
            implied probabilities from a model for each event with columns date, team
    odds:   pandas dataframe
            market odds from bookmaker
    prob_threshold: float
                    implied probability threshold for events to look at
    res_threshold:  float
                    magnitude of mispricing residual to look at
    Returns
    -------
    A pandas dataframe with mispriced events.

    """
    resi = pd.merge(odds.rename(columns={'val': 'odds'}),
                    prob.rename(columns={'val': 'implied'}),
                    on=["div", "season", "date", "team"],
                    how="left")
    resi["market"] = 1 / resi.loc[:, "odds"]
    resi["resid"] = resi["implied"] - resi["market"]
    pos = resi.query("resid>@res_threshold & implied>@prob_threshold").loc[:, ['season', 'div', 'date', 'team']]
    pos.reset_index(inplace=True, drop=True)
    return pos



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
    return payres


def jitter(x, noise_reduction=1000000):
    """Add noise to a series of observations. Useful for ranking functions.
    Parameters:
    -----------
        x (series): a series of numerical observations
        noise_reduction (int): magnitude of noise reduction (higher values mean less noise)
    Example:
    --------
        x = np.random.normal(0, 1, 100).transpose()
        y = jitter(x, noise_reduction=100)
        compare = pd.DataFrame([x, y])
    """
    l = len(x)
    stdev = x.std()
    z = (np.random.random(l) * stdev / noise_reduction) - (stdev / (2 * noise_reduction))
    return z



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




def comp_edge(factor_data, results, byf=['overall']):
    """Computes the hit ratio (edge) for low to high ranked signals captured in a
    bucket column in the input data.

    Parameters:
    -----------
        factor_data (dataframe): A signals dataframe with columns div, season, date, team, field, bucket
        results (dataframe): A event results datafrane with columns div, season, date, team, val
        byf (list): Whether the calculation should be performed overall (default) or additionally
                    by any group (column) in the factor_data input
    Returns:
    --------
        A dataframe with edge ratio's by bucket and any group specified in the by parameter.
        Example:
                bucket  val                field
                1.0   0.296861  Argentina Superliga
                2.0   0.315633  Argentina Superliga
                3.0   0.353865  Argentina Superliga
                4.0   0.392473  Argentina Superliga
                5.0   0.440255  Argentina Superliga
    """

    # rename
    results = results.rename(columns={'val': 'result'})
    # bring results & signals together
    er_ed = pd.merge(factor_data, results, on=['div', 'season', 'date', 'team'], how='left')

    # erase non-events..
    er_ed.dropna(subset=['result'], inplace=True)
    res = pd.DataFrame()
    for k in byf:
        if k == "overall":
            key_gr = 'bucket'
        else:
            key_gr = ['bucket', k]

        # calculate hits..
        res0 = er_ed.groupby(key_gr).agg(hits=pd.NamedAgg(column='result', aggfunc='sum'),
                                         n_obs=pd.NamedAgg(column='result', aggfunc='count')).reset_index()
        res0['val'] = res0['hits'] / res0['n_obs']

        if k == 'overall':
            res0['field'] = k
        else:
            res0.rename(columns={k: 'field'}, inplace=True)

        res0.drop(['hits', 'n_obs'], axis=1, inplace=True)
        res = res.append(res0, ignore_index=True, sort=False)

    res.sort_values(by=['field', 'bucket'], inplace=True)
    res.reset_index(drop=True, inplace=True)

    return res



def info_coef(data, results, byf=None):
    """Computes the information coefficient for a signal.

    Parameters:
    -----------
        data (dataframe):       A dataframe with factors and columns div, season, date, team, field, val
        results (dataframe):    A dataframe with results and columns season, div, date, team, val
        byf (list):             The groups by which to calculate the statistic (eg. ['div', 'season'])

    Returns:
    --------
        A dataframe of information coefficients.

    Example:
    --------
                             div  season       val
        0    Argentina Superliga    2012  0.117534
        1    Argentina Superliga    2013  0.018842
        2    Argentina Superliga    2014  0.012562
        3    Argentina Superliga    2015  0.118525
        4    Argentina Superliga    2016  0.136653

    """
    R = results.rename(columns={'val': 'gd'}).copy()
    A = pd.merge(R, data, on=['div', 'season', 'team', 'date'], how='left')
    # overall
    # r0 = A["gd"].corr(A["val"], method='spearman')
    # r0 = pd.DataFrame({'field': 'overall', 'val': [r0]})
    # res = pd.concat([r0, r1], axis=0, ignore_index=True)

    # by group
    r1 = A.groupby(byf)["gd"].corr(A["val"], method='spearman').reset_index()
    r1.rename(columns={'gd': 'val'}, inplace=True)
    return r1



def est_prob(scores, result, field):
    """Estimate probability of an event occuring (eg. win) for a factor using a logit-model.

    Parameters:
    -----------
        scores (dataframe):     a dataframe with at least columns date, team, field, val (eg. goal_superiority)
        result (dataframe):     a dataframe with results and columns date, team & val (eg. 0/1 for loss/win)
        field (string):         the field in scores to uses to fit the model (eg. "goal_superiority")

    Returns:
    --------
        A few objects are returned:
                1. A dataframe with probabilities for each event
                2. Evaluation statistics

    # Details:
    ----------
        Note that the probabilities are related to the 1-event (eg. win).

    """
    acon = scores.pivot_table(index=['season', 'div', 'date', 'team'],
                              columns='field',
                              values='val').reset_index()
    # merge with results
    prob = pd.merge(result, acon,
                    on=['div', 'season', 'date', 'team'],
                    how='left')
    prob.dropna(inplace=True)
    # fit logit model
    y = prob['val'].values.ravel()
    X = prob[field].values.reshape(-1, 1)
    mod = LogisticRegression()
    mod.fit(X, y)
    y_pred = mod.predict(X)
    # retrieve probability
    # note: that output is 2d array with 1st (2nd) column probability for 0 (1) with 0.5 threshold
    y_pp = mod.predict_proba(X)[:, 1]
    # accurary evaluation
    conf_mat = confusion_matrix(y, y_pred)
    stats = class_accuracy_stats(conf_mat)
    # reshape results
    prob["val"] = y_pp
    del prob[field]

    return prob, stats





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
# ml_map = pd.DataFrame(list(competition.items()), columns=['Div', 'Competition'])
ml_map = pd.read_csv('mapping/leagues.csv', encoding = "ISO-8859-1", delimiter=";")


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


# UTILS ---------------------------------------------------------------------------------------------------------------


def anti_join(x, y, on):
    """Anti-join function that returns rows from x not matching y."""
    oj = x.merge(y, on=on, how='outer', indicator=True)
    z = oj[~(oj._merge == 'both')].drop('_merge', axis=1)
    return z


def ver_type(data, field):
    """Make sure data types in a dataframe are as desired. Make adjustments if not.

    Parameters:
    -----------
        data:   pandas dataframe
                the data that needs to be checked
        field:  dict
                the fields with target data types. Options are:

                    str:        object
                    float:      float64
                    int:        int64
                    date:       datatime64

                For example, one wants an input field in data to be a string. In that case,
                you set field = {'my_column': 'str'} and the my_column field is checked whether
                it is a string (object) and converted to it if not.

    Example:
    --------


    """
    # the template to compare desired types to
    temp = {'str': 'object',
            'float': 'float64',
            'int': 'int64',
            'date': 'datetime'}

    for (key, value) in field.items():
        i = [key, value]
        if data[i[0]].dtypes == temp[i[1]]:
            pass
        else:
            data = data.copy()
            if i[1] == "int":
                data[i[0]] = pd.to_numeric(data[i[0]], downcast='signed', errors='coerce')
            elif i[1] == "float":
                data[i[0]] = pd.to_numeric(data[i[0]], errors='coerce')
            elif i[1] == "str":
                data[i[0]] = pd.to_string(data[i[0]])
            elif i[1] == "date":
                data[i[0]] = pd.to_datetime(data[i[0]], errors='coerce')

    return data



def class_accuracy_stats(conf_mat):
    """Calculate relevant ratio's from the confusion matrix with two classes.

    Parameters:
    -----------
        conf_mat (array):   a confusion matrix with two classes

    Returns:
    --------
        Summary statistics in ratio format.

    Details:
    --------
        The following stats are calculated:
            accuracy:   (tp + tn) / (tp + tn + fp + fn)
            precision:  tp / (tp + fp) (also called positive predictive value - PPV)
            recall:     tp / (tp + fn) (also called sensitivity, hit-rate, true-positive rate)
            F1 score:   2 * (precision * recall) / (precision + recall) -> harmonic mean of precision & recall

        Interpretation with spam-email classification:
            high precision:     not many real emails predicted as spam
            high recall:        predicted most spam emails correctly

    """
    TP = conf_mat[0, 0]
    FN = conf_mat[0, 1]
    FP = conf_mat[1, 0]
    TN = conf_mat[1, 1]
    pre = TP / (TP + FP)
    rec = TP / (TP + FN)
    x = {'accuracy': (TP + TN) / conf_mat.sum(),
         'precision': pre,
         'recall':  rec,
         'f1': 2 * pre * rec / (pre + rec)
         }
    x = pd.DataFrame.from_dict(x, orient="index", columns=["val"])
    return x






