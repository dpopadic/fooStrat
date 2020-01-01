import pandas as pd
import numpy as np

def comp_pts(res):
    """Computes the points scored for each game given a string of W, D or L.

    Parameters:
    -----------
    res (str): a string W, D, L that represents a win, draw or loss event

    Returns:
    --------
    score (int): a score of 0, 1, 3 representing the points won from the event
    """
    if res=='W':
        score = 3
    elif res=='L':
        score = 0
    elif res=='D':
        score = 1
    else:
        score = 0
    return(score)


def reconfig_res(res, persp):
    """Returns W, D, L for each game given a string of H, D or A and
    the perspective (home / away).
    """
    if res=='H' and persp=='home':
        score = 'W'
    elif res=='H' and persp=='away':
        score = 'L'
    elif res=='A' and persp=='home':
        score = 'L'
    elif res=='A' and persp=='away':
        score = 'W'
    elif res=='D':
        score = 'D'
    else:
        score = ''
    return(score)


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


def comp_league_standing(data):
    """Computes the standings, ranks, goals etc. for a single or multiple divisions by
    season. The input table therefore needs to have the following columns:
    div, season, date, home_team, away_team, field, val

    Returns:
    --------
    tbl (dataframe): a table with team rankings by division and season and the following
    columns: div | season | team | points | goals_scored | goals_received | d | l | w | rank

    """

    # extract relevant fields..
    df_fw = data.pivot_table(index=['season', 'div', 'date', 'home_team', 'away_team'],
                             columns='field',
                             values='val',
                             aggfunc='sum').reset_index()
    df_fw[['season', 'div', 'home_team', 'away_team']] = \
        df_fw[['season', 'div', 'home_team', 'away_team']].astype(str, errors='ignore')

    # home team stats..
    df_h = df_fw.loc[:, ['season', 'div', 'date', 'home_team', 'FTAG', 'FTHG', 'FTR']]
    df_h['points'] = df_h['FTR'].apply(lambda x: 3 if x == 'H' else (1 if x == 'D' else 0))
    df_h['res'] = df_h['FTR'].apply(lambda x: 'w' if x == 'H' else ('d' if x == 'D' else 'l'))
    df_h.rename(columns={'home_team': 'team', 'FTAG': 'goals_received', 'FTHG': 'goals_scored'}, inplace=True)
    df_h = df_h.drop(['FTR'], axis=1)

    # away team stats..
    df_a = df_fw.loc[:, ['season', 'div', 'date', 'away_team', 'FTAG', 'FTHG', 'FTR']]
    df_a['points'] = df_a['FTR'].apply(lambda x: 3 if x == 'A' else (1 if x == 'D' else 0))
    df_a['res'] = df_a['FTR'].apply(lambda x: 'w' if x == 'A' else ('d' if x == 'D' else 'l'))
    df_a.rename(columns={'away_team': 'team', 'FTAG': 'goals_scored', 'FTHG': 'goals_received'}, inplace=True)
    df_a = df_a.drop(['FTR'], axis=1)

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


# MAPPING DIVISION TABLE -----------------------------------------------
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
               'G1':'Greek Super League'}
ml_map = pd.DataFrame(list(competition.items()), columns=['Div', 'Competition'])









