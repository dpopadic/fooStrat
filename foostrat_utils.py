import pandas as pd
import numpy as np


# FUNCTIONS TO SUPPORT THE RUNNING OF THE PROJECT ------------------------------------

def ret_xl_cols(file_names, id_col):
    """Returns all available columns across all tabs and multiple excel files."""
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
    df_h.rename(columns={'home_team': 'team', away_goals: 'goals_received', home_goals: 'goals_scored'}, inplace=True)
    df_h = df_h.drop([result], axis=1)

    # away team stats..
    df_a = df_fw.loc[:, ['season', 'div', 'date', 'away_team', away_goals, home_goals, result]]
    df_a['points'] = df_a[result].apply(lambda x: 3 if x == 'A' else (1 if x == 'D' else 0))
    df_a['res'] = df_a[result].apply(lambda x: 'w' if x == 'A' else ('d' if x == 'D' else 'l'))
    df_a.rename(columns={'away_team': 'team', away_goals: 'goals_scored', home_goals: 'goals_received'}, inplace=True)
    df_a = df_a.drop([result], axis=1)

    # consolidate..
    dfc = pd.concat([df_h, df_a], axis=0, sort=True)
    dfc[['goals_scored', 'goals_received']] = dfc[['goals_scored', 'goals_received']].apply(pd.to_numeric,
                                                                                            errors='coerce')
    dfc_tot_pts = dfc.groupby(by=['div', 'season', 'team'])[['points', 'goals_scored', 'goals_received']].sum()
    dfc_tot_pts = dfc_tot_pts.reset_index()

    # number of wins..
    df_wdl = dfc.loc[:, ['season', 'div', 'date', 'team', 'res', 'points']]
    dfc_agg_wdl = df_wdl.pivot_table(index=['div', 'season', 'team'], columns='res', values='points',
                                     aggfunc='count').reset_index()

    # add number of wins to standings..
    tbl = pd.merge(dfc_tot_pts, dfc_agg_wdl, on=['div', 'season', 'team'], how='left')

    # rankings..
    tbl['rank'] = tbl.groupby(['div', 'season'])['points'].rank(ascending=False, method='first').reset_index(drop=True)
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


# FACTOR CONSTRUCTION ------------------------------------------------------------------

def fgoalsup(data, field, k):
    """Calculates the goal superiority factor across divisions and seasons for each team on a
    rolling basis.

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
    data_goals['val'] = data_goals.loc[:, 'val'].apply(pd.to_numeric)
    tmp = pd.pivot_table(data_goals,
                         index=['div', 'season', 'date', 'home_team', 'away_team'],
                         columns='field',
                         values='val').reset_index()

    # home team..
    tmp1 = tmp.loc[:, ['div', 'season', 'date', 'home_team', field[0], field[1]]]
    tmp1.rename(columns={'home_team': 'team', field[0]: 'g_scored', field[1]: 'g_received'}, inplace=True)
    # away team..
    tmp2 = tmp.loc[:, ['div', 'season', 'date', 'away_team', field[0], field[1]]]
    tmp2.rename(columns={'away_team': 'team', field[1]: 'g_scored', field[0]: 'g_received'}, inplace=True)
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
    return(data_fct)




# MAPPING DIVISION TABLE ------------------------------------------------------------------
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
               'N1':'Dutch Eredivisie ',
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









