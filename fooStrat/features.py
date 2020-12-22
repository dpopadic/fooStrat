import pandas as pd
import numpy as np
from scipy.stats import zscore
from itertools import chain
import fooStrat.servicers as fose
import fooStrat.metrics as sfs
from fooStrat.mapping import odds_fields, odds_fields_neutral
from fooStrat.response import con_res_wd

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
    # 2 ways to identify games: 1) FTR and 2) AvgA
    # data_cf = data.query("field=='FTR' | field=='AvgA'")[['div', 'season', 'date', 'home_team', 'away_team']]
    data_cf = data.query("field=='FTR'")[['div', 'season', 'date', 'home_team', 'away_team']]
    data_cf.reset_index(drop=True, inplace=True)

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



def feat_goalbased(data, k=5):
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
        rolling(window=k, min_periods=1).sum().reset_index()
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

    # add dummy-date &  lag factor
    data_fct = fose.insert_tp1_vals(data=data_fct)
    data_fct.sort_values(['team', 'date', 'field'], inplace=True)
    data_fct['val'] = data_fct.groupby(['team', 'field'])['val'].shift(1)
    data_fct.reset_index(level=0, drop=True, inplace=True)

    # identify promoted/demoted teams & neutralise score for them..
    team_chng = fose.newcomers(data=data_fct)
    res = fose.neutralise_scores(data=data_fct, teams=team_chng, n=k - 1)
    # check: a = res.query("div=='E0' & season=='2020' & team=='liverpool'").sort_values(['date'])
    # expand factors
    res = fose.expand_field(data=res)

    # z-score (1 degree of freedom to reflect sample stdev)
    res['val'] = res.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))

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
    fh = sfs.fform(data=data, field="FTR", type="home")
    fa = sfs.fform(data=data, field="FTR", type="away")
    ftot = sfs.fform(data=data, field="FTR", type="all")
    feat_all = pd.concat([fh, fa, ftot], axis=0, sort=True)
    # expand factors
    feat_all = fose.expand_field(data=feat_all)
    # z-score
    feat_all['val'] = feat_all.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))

    return feat_all


def feat_turnaround(data):
    """Compute turnaround factors:
        - turnaround ability last
        - turnaround ability trend (past 3)

    Parameters:
    -----------
        data:   pandas dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val

    Details
    -------
        - for turnaround-ability, when there is no half-time data, full-time results are considered only

    """
    data_ed = data.query("field in ['HTAG', 'HTHG', 'FTAG', 'FTHG']")

    # half-time goals
    htg = fose.neutralise_field(data_ed,
                                field=['HTHG', 'HTAG'],
                                field_name=['g_scored_ht', 'g_received_ht'],
                                field_numeric=True,
                                column_field=True)
    # full-time goals
    ftg = fose.neutralise_field(data_ed,
                                field=['FTHG', 'FTAG'],
                                field_name=['g_scored_ft', 'g_received_ft'],
                                field_numeric=True,
                                column_field=True)
    cog = pd.merge(ftg, htg, on=['div', 'season', 'date', 'team'], how='left')

    # --- turnaround ability (last)
    # compute the score
    cog['val'] = (cog['g_scored_ft'] - cog['g_received_ft']) - (cog['g_scored_ht'] - cog['g_received_ht'])
    # handle missing data by simply taking into account the end-result
    cog['val_nan'] = (cog['g_scored_ft'] - cog['g_received_ft'])
    cog['val'] = cog[['val', 'val_nan']].apply(lambda x: x[1] if np.isnan(x[0]) else x[0], axis=1)
    cog['field'] = 'turnaround_ability_last'
    cog = cog[['div', 'season', 'date', 'team', 'field', 'val']]

    # --- turnaround ability (past 3)
    cog_past = cog.copy()
    tmp = cog_past.groupby('team', as_index=False)['val'].rolling(window=3, min_periods=1).sum()
    cog_past['val'] = tmp.reset_index(level=0, drop=True)
    cog_past['field'] = 'turnaround_ability_trend'

    # combine
    cog_co = pd.concat([cog, cog_past], axis=0, sort=False, ignore_index=True)

    # add dummy-date &  lag factor
    cog_co = fose.insert_tp1_vals(data=cog_co)
    cog_co = cog_co.sort_values(['team', 'date']).reset_index(drop=True)
    cog_co['val'] = cog_co.groupby(['team', 'field'])['val'].shift(1)
    res = fose.expand_field(data=cog_co)
    # z-score
    res['val'] = res.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))

    return res



def feat_stanbased(data):
    """Calculates standings based factors:
        - position residual
        - points residual
        - team quality cluster (cluster, consistency)

    Parameters:
    -----------
        data:   pandas dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val

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
    # reverse order so that lower rank is perceived better
    rroh = tmp_2.groupby(['div', 'season'], as_index=False)['val'].max()
    rroh.rename(columns={'val': 'n_places'}, inplace=True)
    tmp_2 = pd.merge(tmp_2, rroh, on=['div', 'season'])
    tmp_2['val'] = tmp_2['n_places'] - tmp_2['val'] + 1
    tmp_2.drop('n_places', axis=1, inplace=True)

    rppa = pd.concat([tmp_1, tmp_2],
                     axis=0,
                     sort=False,
                     ignore_index=True)
    # expand factor
    # add dummy-date &  lag factor
    rppa = fose.insert_tp1_vals(data=rppa)
    rppa = rppa.sort_values(['team', 'date']).reset_index(drop=True)
    rppa['val'] = rppa.groupby(['team', 'field'])['val'].shift(1)
    rppa = fose.expand_field(data=rppa, dates=None)

    # --- team quality cluster (no lag required here)
    tqc = sfs.team_quality_cluster(data=df_1) # already a z-score where necessary
    # add dummy-date
    tqc = fose.insert_tp1_vals(data=tqc)
    # normalise
    date_univ = fose.con_date_univ(data=data)
    # a = tqc.query("div=='E0' & field=='team_quality_consistency' & season=='2018'")
    tqc = fose.expand_field(data=tqc, dates=date_univ)
    # consolidate
    tog = pd.concat([rppa, tqc[tqc['field'] != 'team_quality_cluster'].reset_index(drop=True)],
                    axis=0,
                    sort=False,
                    ignore_index=True)
    # z-score (only for non-categorical)
    tog['val'] = tog.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))
    res = pd.concat([tog, tqc[tqc['field'] == 'team_quality_cluster'].reset_index(drop=True)],
                    axis=0,
                    sort=False,
                    ignore_index=True)
    return res



def feat_h2h(data):
    """Computes head-to-head factors (last 5 h2h):
        - h2h next opponent advantage
        - h2h next opponent chance
    Details:
    --------
        At each point in time, one could also calculate h2h against all teams. However, this would be the
        same as goal superiority factor for example. Therefore, it's of little use and only opponent-specific
        factors are calcualted here. In general, all factors not specific to the 2 opponents are already
        reflected in other factors, so only include opponent specific here.

    """
    # add upcoming games
    upc = fose.con_h2h_set_upcoming(data=data)

    # --- h2h next opponent goal advantage
    dfc = fose.con_h2h_set(data=data,
                           field=['FTHG', 'FTAG'],
                           field_name=['g_scored', 'g_received'])
    dfc_ed = dfc.set_index('date').sort_values('date').groupby(['team', 'opponent'])[['g_scored', 'g_received']]. \
                 rolling(window=5, min_periods=1).sum().reset_index()
    dfc_ed['val'] = dfc_ed['g_scored'] - dfc_ed['g_received']
    # add back other information
    dfc_fi = pd.merge(dfc[['div', 'season', 'date', 'team', 'opponent']],
                      dfc_ed[['date', 'team', 'opponent', 'val']],
                      on=['date', 'team', 'opponent'],
                      how='left')
    # upcoming


    # data_cf = data.query("field=='AvgA'")[['div', 'season', 'date', 'home_team', 'away_team']]
    # pds = data[data['date'] == data['date'].max()].reset_index(drop=True)
    # pds_re = fhome(data=pds)
    # pds_re.drop('field', axis=1, inplace=True)
    # pds_re['val'] = np.nan
    dfc_fi['field'] = 'h2h_next_opponent_advantage'


    # --- h2h next opponent attempts advantage
    dfa = fose.con_h2h_set(data=data,
                           field=['HST', 'AST'],
                           field_name=['shots_attempted_tgt', 'shots_conceded_tgt'])
    dfa_ed = dfa.set_index('date').sort_values('date').groupby(['team', 'opponent'])[
        ['shots_attempted_tgt', 'shots_conceded_tgt']]. \
        rolling(window=5, min_periods=1).sum().reset_index()
    dfa_ed['val'] = dfa_ed['shots_attempted_tgt'] - dfa_ed['shots_conceded_tgt']
    # add back other information
    dfa_fi = pd.merge(dfa[['div', 'season', 'date', 'team', 'opponent']],
                      dfa_ed[['date', 'team', 'opponent', 'val']],
                      on=['date', 'team', 'opponent'],
                      how='left')
    dfa_fi['field'] = 'h2h_next_opponent_chance'

    # assemble
    dfac_fil = pd.concat([dfc_fi, dfa_fi], axis=0, sort=False)

    # insert t+1 observations -> need to know the upcoming opponent!
    # dfac_fil = fose.insert_tp1_vals(data=dfac_fil, by=['field', 'opponent'])

    # lag values by team & opponent
    dfac_fil = dfac_fil.sort_values(['field', 'team', 'opponent', 'date']).reset_index(drop=True)
    dfac_fil['val'] = dfac_fil.groupby(['field', 'team', 'opponent'])['val'].shift(1)
    dfac_fil.drop('opponent', axis=1, inplace=True)
    dfac_fil = fose.expand_field(data=dfac_fil)
    # z-score
    dfac_fil['val'] = dfac_fil.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))

    return dfac_fil



def feat_strength(data, k=3):
    """Compute team strength features:
        - shots attempted / conceded
        - shots on target attempted / conceded
        - hit / conceded wood
        - corners hit / conceded
        - attack strength
        - defense strength
        - attack + defense strength

    These features are calculated using the last 3 games.

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
    xm2 = xm1.groupby(['team'])[list(chain(*fm.values()))].rolling(window=k, min_periods=1).mean().reset_index(drop=True)
    xm2 = pd.concat([xm1[['div', 'season', 'team', 'date']], xm2], axis=1, sort=True)

    # calculate cross-sectional z-score for attack & defense strength
    # - attack strength
    xm1_as = xm2.loc[:,
             ['div', 'season', 'team', 'date', fm['shots'][0], fm['target'][0], fm['wood'][0], fm['corners'][0]]]
    xm1_as = pd.melt(xm1_as,
                     id_vars=['div', 'season', 'team', 'date'],
                     var_name='field',
                     value_name='val').dropna()

    xm1_as_ed = fose.expand_field(data=xm1_as)
    xm1_as_ed['val'] = xm1_as_ed.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))
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

    xm1_ds_ed = fose.expand_field(data=xm1_ds)
    xm1_ds_ed['val'] = xm1_ds_ed.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))
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

    # add dummy-date &  lag factor
    tmp = fose.insert_tp1_vals(data=tmp)
    tmp_lag = tmp.sort_values(['team', 'date']).reset_index(drop=True)
    tmp_lag['val'] = tmp_lag.groupby(['team', 'field'])['val'].shift(1)

    # neutralise for new entrants
    team_chng = fose.newcomers(data=tmp_lag)
    res = fose.neutralise_scores(data=tmp_lag, teams=team_chng, n=k - 1)
    res = fose.expand_field(data=res)
    # z-score
    res['val'] = res.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))

    return res


def feat_odds_volatility(data, odds_fields=odds_fields, odds_fields_neutral=odds_fields_neutral):
    """Calculates odds volatility of win/draw events across all bookies for each game."""
    data_neu = fose.neutralise_field_multi(data=data,
                                           field=odds_fields,
                                           field_map=odds_fields_neutral,
                                           field_numeric=True,
                                           column_field=False)
    # unique fields
    ofn = odds_fields_neutral.groupby('event')['field_neutral'].unique().reset_index()
    ofn = ofn.explode('field_neutral').reset_index(drop=True).rename(columns={'field_neutral': 'field'})
    # add event
    data_neu = pd.merge(data_neu,
                        ofn,
                        how='left',
                        on='field')
    # --- odds volatility
    # calculate vol of draw/win and derive average
    df1 = data_neu.groupby(['season', 'div', 'date', 'team', 'event'])['val'].std().reset_index()
    df1 = df1.groupby(['season', 'div', 'date', 'team'])['val'].mean().reset_index()
    df1['field'] = 'odds_volatility'

    return df1



def feat_odds_accuracy(data, odds):
    """Estimate odds accuracy using a logit model.

    # Parameters:
    -------------
        data:   pd dataframe
                a dataframe with columns div, date, season, home_team, away_team, field, val
        odds:   pd dataframe
                a dataframe with columns div, date, season, field, val

    """
    event_wdl = con_res_wd(data=data, field='FTR', encoding=True)
    # merge results with odds
    mo = odds.pivot_table(index=['div', 'season', 'date', 'team'], columns='field', values='val').reset_index()
    rndo = pd.merge(event_wdl, mo, on=['div', 'season', 'date', 'team'], how='left')
    # remove na's
    rndo = rndo.dropna().reset_index(drop=True)
    # estimate accuracy
    rndo_est = rndo.groupby(['div', 'season', 'team', 'field']).apply(fose.est_odds_accuracy,
                                                                      y='val',
                                                                      x=['odds_win', 'odds_draw',
                                                                         'odds_lose']).reset_index()
    rndo_est.rename(columns={0: 'val'}, inplace=True)
    return rndo_est


def feat_odds_uncertainty(data, odds):
    """Derives the prediction/odds uncertainty features.
        - volatility of odds (the lower, the better)
        - odds prediction accuracy (the more accurate, the better)
        - pricing spread (the higher, the better)
    """
    # --- odds volatility
    df1 = feat_odds_volatility(data=data)
    df1_ed = fose.expand_field(data=df1)
    df1_ed['val'] = df1_ed.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(-1 * x, ddof=1))

    # --- historical odds prediction accuracy
    df2 = feat_odds_accuracy(data=data, odds=odds)
    df2_ed = df2.query("field in ['win', 'lose']").groupby(['div', 'season', 'team']).agg('mean').reset_index()
    df2_ed['field'] = "odds_accuracy"
    # expand field
    date_univ = fose.con_date_univ(data=data)
    df2_ed = fose.expand_field(data=df2_ed, dates=date_univ, keys=['div', 'season', 'team', 'field'])
    df2_ed['val'] = df2_ed.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))

    # --- odds uncertainty composite
    dfc = pd.concat([df1_ed, df2_ed], axis=0, sort=True)
    dfc = dfc.groupby(['div', 'season', 'date', 'team']).agg('mean').reset_index()
    dfc['field'] = "uncertainty_composite"
    dfc['val'] = dfc.groupby(['div', 'season', 'date', 'field'])['val'].transform(lambda x: zscore(x, ddof=1))

    res = pd.concat([df1_ed, df2_ed, dfc], axis=0, sort=True)
    return res
