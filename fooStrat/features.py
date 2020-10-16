import pandas as pd
import numpy as np
from scipy.stats import zscore
from itertools import chain
import fooStrat.servicers as fose

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
    data_goals_co = fose.neutralise_field(data,
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

    # ----- feature: not failed to score (last 5)
    feat_fts = data_goals_co_i.copy()
    feat_fts['val'] = feat_fts['g_scored'].apply(lambda x: 1 if x > 0 else 0)
    feat_fts = feat_fts.sort_values('date').groupby(['team'])['val'].rolling(k, min_periods=1).sum().reset_index()
    feat_fts['field'] = 'not_failed_scoring'

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

    # lag factor
    data_fct.sort_values(['team', 'date', 'field'], inplace=True)
    data_fct['val'] = data_fct.groupby(['team', 'field'])['val'].shift(1)

    # identify promoted/demoted teams & neutralise score for them..
    team_chng = fose.newcomers(data=data_fct)
    res = fose.neutralise_scores(data=data_fct, teams=team_chng, n=k - 1)
    # check: a = res.query("div=='E0' & season=='2019' & team=='sheffield_united'").sort_values(['date'])
    # expand factors
    res = fose.norm_factor(data=res)
    # z-score (1 degree of freedom to reflect sample stdev)
    res['val'] = res.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))

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
    team_chng = fose.newcomers(data=ha_fin)
    res = fose.neutralise_scores(data=ha_fin, teams=team_chng, n=k-1)
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
    # expand factors
    feat_all = fose.norm_factor(data=feat_all)

    return feat_all


def feat_stanbased(data):
    """Calculates standings based factors. These are:
        - position residual
        - points residual
        - team quality cluster (cluster, consistency)

    Parameters:
    -----------
        data:   pandas dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val

    Details:
    --------

    """

    df_0 = data[(data.field == 'FTR') | (data.field == 'FTHG') | (data.field == 'FTAG')]
    # compute rolling league standings
    df_1 = fose.comp_league_standing(data=df_0, home_goals='FTHG', away_goals='FTAG', result='FTR')

    # --- points advantage
    tmp_1 = df_1.loc[:, ['div', 'season', 'date', 'team', 'points']]
    tmp_1['field'] = "points_advantage"
    tmp_1.rename(columns={'points': 'val'}, inplace=True)

    # --- rank position
    tmp_2 = df_1.loc[:, ['div', 'season', 'date', 'team', 'rank']]
    tmp_2['field'] = "rank_position"
    tmp_2.rename(columns={'rank': 'val'}, inplace=True)

    rppa = pd.concat([tmp_1, tmp_2],
                     axis=0,
                     sort=False,
                     ignore_index=True)
    # lag factor
    rppa = rppa.sort_values(['team', 'date']).reset_index(drop=True)
    rppa['val'] = rppa.groupby(['team', 'field'])['val'].shift(1)
    rppa = fose.expand_field(data=rppa, date_univ=None)

    # --- team quality cluster (no lag required here)
    tqc = team_quality_cluster(data=df_1)
    # normalise
    date_univ = fose.con_date_univ(data=data)
    # a = tqc.query("div=='E0' & field=='team_quality_consistency' & season=='2018'")
    tqc = fose.expand_field(data=tqc, date_univ=date_univ)

    # consolidate
    res = pd.concat([rppa, tqc],
                    axis=0,
                    sort=False,
                    ignore_index=True)

    return res


def team_quality_cluster(data):
    """Calculates the team quality cluster features.

    Parameters:
    -----------
        data:   pandas dataframe
                an object retrieved from comp_league_standing

    Details:
    --------
        Note that these features are unusual in a sense that there is only a single
        value for each team and season.

    """

    # last game of season
    data_ed = data.groupby(['div', 'season']).apply(lambda x: x[x['date'] == x['date'].max()]).reset_index(drop=True)

    # -- team quality cluster
    tqual = data_ed.copy()
    tqual['val'] = tqual.groupby(['div', 'season'])['rank']. \
        transform(lambda x: pd.qcut(x, q=3, labels=range(1, 3 + 1), duplicates='drop'))
    tqual = tqual[['div', 'season', 'date', 'team', 'val']]
    tqual['field'] = 'team_quality_cluster'

    # -- autocorrelation last 5y
    acf = data_ed.copy()
    tmp = acf.groupby('team', as_index=False)['points'].rolling(window=5, min_periods=1). \
        apply(lambda x: pd.Series(x).autocorr(lag=1), raw=True)
    acf['val'] = tmp.reset_index(level=0, drop=True)
    acf = acf[['div', 'season', 'date', 'team', 'val']]
    acf['field'] = 'team_quality_consistency'
    acf = acf[acf['val'].notna()].reset_index(level=0, drop=True)

    # combine
    res = pd.concat([tqual, acf], axis=0, sort=False, ignore_index=True)
    return res



def feat_strength(data, k):
    """Compute team strength features:
        - shots attempted / conceded
        - shots on target attempted / conceded
        - hit / conceded wood
        - corners hit / conceded
        - attack strength
        - defense strength
        - attack + defense strength

    These features are calculated using the last 5 games.

    Details:
    --------
        Note that normalisation is performed internally inside this function.

    """

    fm = {'shots': ['shots_attempted', 'shots_conceded'],
          'target': ['shots_attempted_tgt', 'shots_conceded_tgt'],
          'wood': ['wood_hit', 'wood_conceded'],
          'corners': ['corners_hit', 'corners_conceded']}

    # neutralise relevant fields
    x0 = fose.neutralise_field(data, field=['HS', 'AS'], field_name=fm['shots'], field_numeric=True, column_field=True)
    x1 = fose.neutralise_field(data, field=['HST', 'AST'], field_name=fm['target'], field_numeric=True, column_field=True)
    x2 = fose.neutralise_field(data, field=['HHW', 'AHW'], field_name=fm['wood'], field_numeric=True, column_field=True)
    x3 = fose.neutralise_field(data, field=['HC', 'AC'], field_name=fm['corners'], field_numeric=True, column_field=True)

    # bring all features together
    xm1 = pd.merge(x0, x1, on=['div', 'season', 'date', 'team'], how='outer')
    xm1 = pd.merge(xm1, x2, on=['div', 'season', 'date', 'team'], how='outer')
    xm1 = pd.merge(xm1, x3, on=['div', 'season', 'date', 'team'], how='outer')

    # rolling average over n periods
    xm1 = xm1.sort_values('date').reset_index(drop=True)
    xm2 = xm1.groupby(['team'])[list(chain(*fm.values()))].rolling(3, min_periods=1).mean().reset_index(drop=True)
    xm2 = pd.concat([xm1[['div', 'season', 'team', 'date']], xm2], axis=1, sort=True)

    # calculate cross-sectional z-score for attack & defense strength
    # - attack strength
    xm1_as = xm2.loc[:,
             ['div', 'season', 'team', 'date', fm['shots'][0], fm['target'][0], fm['wood'][0], fm['corners'][0]]]
    xm1_as = pd.melt(xm1_as,
                     id_vars=['div', 'season', 'team', 'date'],
                     var_name='field',
                     value_name='val').dropna()

    xm1_as_ed = fose.norm_factor(data=xm1_as, neutralise=True)
    xm1_as_cf = xm1_as_ed.groupby(['div', 'season', 'team', 'date'])['val'].mean().reset_index()
    xm1_as_cf['field'] = "attack_strength"
    xm1_as_ed = pd.concat([xm1_as_ed, xm1_as_cf], axis=0, sort=True)

    # - defence strength
    xm1_ds = xm2.loc[:,
             ['div', 'season', 'team', 'date', fm['shots'][1], fm['target'][1], fm['wood'][1], fm['corners'][1]]]
    xm1_ds = pd.melt(xm1_ds,
                     id_vars=['div', 'season', 'team', 'date'],
                     var_name='field',
                     value_name='val').dropna()

    xm1_ds_ed = fose.norm_factor(data=xm1_ds, neutralise=True)
    xm1_ds_cf = xm1_ds_ed.groupby(['div', 'season', 'team', 'date'])['val'].mean().reset_index()
    xm1_ds_cf['field'] = "defense_strength"
    xm1_ds_ed = pd.concat([xm1_ds_ed, xm1_ds_cf], axis=0, sort=True)
    xm1_ds_ed['val'] = -1 * xm1_ds_ed['val']

    # - attack - defense composite: sum-up all features & compute z-score
    xm2_ed = pd.concat([xm1_as_ed, xm1_ds_ed], axis=0)
    xm2_edc = xm2_ed.query("field in ['attack_strength', 'defense_strength']"). \
        groupby(['div', 'season', 'date', 'team'])['val'].sum().reset_index()
    xm2_edc['val'] = xm2_edc.groupby(['div', 'season', 'date'])['val'].transform(lambda x: zscore(x))
    xm2_edc['field'] = "atadef_composite"

    # get all together
    tmp = pd.concat([xm2_ed, xm2_edc], axis=0, sort=True)

    # lag factor
    tmp_lag = tmp.sort_values(['team', 'date']).reset_index(drop=True)
    tmp_lag['val'] = tmp_lag.groupby(['team', 'field'])['val'].shift(1)

    # neutralise for new entrants
    team_chng = fose.newcomers(data=tmp_lag)
    res = fose.neutralise_scores(data=tmp_lag, teams=team_chng, n=k - 1)
    return res


