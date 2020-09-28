import pandas as pd
import numpy as np
import fooStrat.servicers as fose

def eval_feature(data, results, feature):
    """Evaluate the efficacy of a feature. Returns a dictionary with:
        edge by division
        edge by season
        information coefficients
        summary statistics
            edge residual:  top bucket edge - bottom bucket edge
            ic:             average ic

    Parameters:
    -----------
        data:       pd dataframe
                    signals for each team with columns season, div, date, team, field, val
        feature:    str
                    feature to evaluate:
                        goal_superiority

    """

    # calculate buckets
    df = fose.comp_bucket(data=data.query('field==@feature'), bucket_method='first', bucket=5)

    # retrieve relevant results to test against
    rc = results['wdl'].query('field=="win"').drop('field', axis=1)

    # compute the hit ratio by bucket for the factor
    edge_1 = np.round(comp_edge(factor_data=df, results=rc, byf=['overall', 'div']), 3)
    edge_2 = np.round(comp_edge(factor_data=df, results=rc, byf=['season']))

    # compute IC's
    ic = np.round(info_coef(data=df, results=results['gd'], byf=['div', 'season']), 3)

    # summary
    edge_res = np.round(np.abs(edge_1.query("field == 'overall' & bucket in [1, 5]")['val'].diff().values[1]), 3)
    ic_avg = np.round(ic['val'].mean(), 3)
    smry = {'edge_residual': edge_res, 'ic': ic_avg}

    # evaluation objects
    res = {'edge_div': edge_1, 'edge_season': edge_2, 'ic': ic, 'summary': smry}

    return res



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
    nf0 = fose.neutralise_field(data=data, field=field, field_name=field_name, field_numeric=True, column_field=True)
    nf0['val'] = nf0[field_name[0]] - nf0[field_name[1]]
    del nf0[field_name[0]]
    del nf0[field_name[1]]
    return nf0



def reshape_wdl(data, event):
    """Reshape win, draw, lose events for teams.

    Parameters:
    -----------
        data:   pandas dataframe
                A dataframe with columns season, date, div, home_team, away_team, field, val
        event:  str
                How to shape the result. Options are:
                    win     highlight whether a team won with 0 / 1
                    lose    highlight whether a team lost with 0 / 1
                    draw    highlight whether a team drew with 0 / 1
                    wdl     highlight what the team did: win, lose, draw

    """

    if event == "win":
        # home team
        home = data.loc[:, ['div', 'season', 'date', 'home_team', 'val']]
        home['val'] = home.loc[:, 'val'].apply(lambda x: 1 if x == 'H' else 0)
        home['field'] = "win"
        home.rename(columns={'home_team': 'team'}, inplace=True)

        # away team
        away = data.loc[:, ['div', 'season', 'date', 'away_team', 'val']]
        away['val'] = away.loc[:, 'val'].apply(lambda x: 1 if x == 'A' else 0)
        away['field'] = "win"
        away.rename(columns={'away_team': 'team'}, inplace=True)

        res = pd.concat([home, away], axis=0, sort=True)

    elif event == "lose":
        # home team
        home = data.loc[:, ['div', 'season', 'date', 'home_team', 'val']]
        home['val'] = home.loc[:, 'val'].apply(lambda x: 1 if x == 'A' else 0)
        home['field'] = "lose"
        home.rename(columns={'home_team': 'team'}, inplace=True)

        # away team
        away = data.loc[:, ['div', 'season', 'date', 'away_team', 'val']]
        away['val'] = away.loc[:, 'val'].apply(lambda x: 1 if x == 'H' else 0)
        away['field'] = "lose"
        away.rename(columns={'away_team': 'team'}, inplace=True)

        res = pd.concat([home, away], axis=0, sort=True)

    elif event == "draw":
        draw = data.copy()
        draw['val'] = data.loc[:, 'val'].apply(lambda x: 1 if x == 'D' else 0)
        draw['field'] = 'draw'
        res = pd.melt(draw,
                       id_vars=['div', 'season', 'date', 'field', 'val'],
                       value_name='team')
        res.drop(['variable'], axis=1, inplace=True)

    elif event == "wdl":
        # home team
        home = data.loc[:, ['div', 'season', 'date', 'home_team', 'val']]
        home['val'] = home.loc[:, 'val'].apply(lambda x: "win" if x == 'H' else ("draw" if x == "D" else "lose"))
        home['field'] = "result"
        home.rename(columns={'home_team': 'team'}, inplace=True)

        # away team
        away = data.loc[:, ['div', 'season', 'date', 'away_team', 'val']]
        away['val'] = away.loc[:, 'val'].apply(lambda x: "win" if x == 'A' else ("draw" if x == "D" else "lose"))
        away['field'] = "result"
        away.rename(columns={'away_team': 'team'}, inplace=True)

        res = pd.concat([home, away], axis=0, sort=True)

    res = res.reset_index(level=0, drop=True)

    return res


def con_res_wd(data, field, encoding=True):
    """
    Constructs the event result data in a manner that is readily available for back-testing.

    Parameters:
    -----------
        data (dataframe):       a dataframe with columns season, date, div, home_team, away_team, field, val
        field (string):         a string that defines the event (eg. 'FTR' for full-time results)
        encoding (string):      whether to encode the events or not (defaults to True)

    Returns:
    --------
        A dataframe of results 0/1 with fields win, draw, lost for each team.

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

    if encoding == True:
        # win, draw lose one-hot encoding
        d_win = reshape_wdl(data=res_tmp, event="win")
        d_lose = reshape_wdl(data=res_tmp, event="lose")
        d_draw = reshape_wdl(data=res_tmp, event="draw")

        res = pd.concat([d_win, d_lose, d_draw], axis=0, sort=True)
        res = res.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)
    else:
        res = reshape_wdl(data=res_tmp, event="wdl")

    return res



def con_res(data, obj):
    """Constructs results objects that are required for testing.

    Parameters:
    -----------
        data (dataframe):       a dataframe with columns season, date, div, home_team, away_team, field, val
        obj (string/list):      the object(s) to construct:
                                    gd:     goals difference by game
                                    wdl:     win or draw by game (binary 0/1 if won, drew or lost for each team)
        field (list or string): a string that defines the event for the object (eg. 'FTR' when wd or
                                ['FTHG', 'FTAG'] when gd)

    Returns:
    --------
        A dataframe with the results in optimal shape.

    """
    wdl = gd = None
    if "wdl" in obj:
        wdl = con_res_wd(data=data, field='FTR')

    if "gd" in obj:
        gd = con_res_gd(data=data, field=['FTHG', 'FTAG'])

    res = {'wdl': wdl, 'gd': gd}

    return res



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

    Details:
    --------
        Note that factor_data is assumed to be lagged so that there is no lookahead bias.

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
    rd = results.rename(columns={'val': 'gd'}).copy()
    ad = pd.merge(rd, data, on=['div', 'season', 'team', 'date'], how='left')
    ad = ad.dropna().reset_index(drop=True)

    # overall
    # r0 = A["gd"].corr(A["val"], method='spearman')
    # r0 = pd.DataFrame({'field': 'overall', 'val': [r0]})
    # res = pd.concat([r0, r1], axis=0, ignore_index=True)

    # by group
    ic = ad.groupby(byf)["gd"].corr(ad["val"], method='spearman').reset_index()
    ic.rename(columns={'gd': 'val'}, inplace=True)
    return ic

