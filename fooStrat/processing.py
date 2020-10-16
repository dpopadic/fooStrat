import pandas as pd
import numpy as np
import os
import glob
from fooStrat.helpers import anti_join

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
    fi_nm = ['data/src_data/all-euro-data-2017-2018.xlsx', 'data/src_data/all-euro-data-1999-2000.xls']
    extra_key = pd.DataFrame({'fi_nm':fi_nm, 'season':[i[23:32] for i in fi_nm]})
    print(extra_key)
                                       fi_nm        season
    0  data/src_data/all-euro-data-2017-2018.xlsx  2017-2018
    1  data/src_data/all-euro-data-1999-2000.xls   1999-2000

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
    data.to_pickle('./data/pro_data/source_core.pkl')
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
                         data came from. For example, in  'data/src_data/all-euro-data-1993-1994.xls' 1993-1994 will
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
    data_prc.to_pickle('./data/pro_data/source_core.pkl')
    print("Source Data History has been updated.")



def update_flib(data, dir='./data/pro_data/', update = True):
    """Builds or updates the factor library.

    Parameters:
    -----------
        data:   list
                a list of pandas dataframe's with factors across leagues
        dir:    str, default data/pro_data
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



def delete_flib(field, path='data/pro_data/'):
    """Delete fields from the factor library.

    Parameters:
    -----------
        field:  str
                the field(s) to be deleted from the factor library
        dir:    str, default data/pro_data
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


def consol_flib():
    """Consolidate all feature libraries.

    Details:
    --------
        Note that factor libraries are assumed to be stored as flib_-prefix.

    """
    # read relevant files
    l = []
    for p in glob.glob('pro_data/flib_*'):
        if p != 'data/pro_data/flib.pkl':
            l.append(p)

    res = pd.concat([pd.read_pickle(i) for i in l], axis=0, sort=False)
    res.reset_index(drop=True, inplace=True)
    res.to_pickle("data/pro_data/flib.pkl")

    print("Factor library is consolidated.")






