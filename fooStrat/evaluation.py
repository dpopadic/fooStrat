import pandas as pd
import numpy as np
import fooStrat.servicers as fose



def eval_feature(data, results, feature, categorical=False):
    """Evaluate the efficacy of a feature. Returns a dictionary with:
        edge by division
        edge by season
        information coefficients
        summary statistics
            edge residual:  top bucket edge - bottom bucket edge
            ic:             average ic

    Parameters:
    -----------
        data:           pd dataframe
                        signals for each team with columns season, div, date, team, field, val
        feature:        str
                        feature to evaluate (eg. goal_superiority)
        categorical:    boolean, False
                        whether the feature is categorical

    """

    # calculate buckets
    if categorical == True:
        df = data.query('field==@feature').reset_index(drop=True)
        df['bucket'] = df['val']
    else:
        df = fose.comp_bucket(data=data.query('field==@feature'), bucket_method='first', bucket=5)

    # retrieve relevant results to test against
    rc = results['wdl'].query('field=="win"').drop('field', axis=1)

    # compute the hit ratio by bucket for the factor
    edge_1 = np.round(comp_edge(factor_data=df, results=rc, byf=['overall', 'div']), 3)
    edge_2 = np.round(comp_edge(factor_data=df, results=rc, byf=['season']), 3)

    if categorical == True:
        ic, ic_avg = None, None
        edge_res = np.round(np.abs(edge_1.query("field == 'overall'")['val'].agg({"max", "min"}).diff().values[1]), 3)
    else:
        # compute IC's
        ic = np.round(info_coef(data=df, results=results['gd'], byf=['div', 'season']), 3)
        # summary
        edge_res = np.round(np.abs(edge_1.query("field == 'overall' & bucket in [1, 5]")['val'].diff().values[1]), 3)
        ic_avg = np.round(ic['val'].mean(), 3)

    smry = {'edge_residual': edge_res, 'ic': ic_avg}
    # evaluation objects
    res = {'edge_div': edge_1, 'edge_season': edge_2, 'ic': ic, 'summary': smry}

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
    res_0 = results.query('field == @event').reset_index(drop=True)
    res_0.drop('field', axis=1, inplace=True)
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


def pnl_eval_summary(z):
    """P&L evaluation summary"""
    # hit ratio
    n_won = np.sum(z > 0)
    n_lost = np.sum(z < 0)
    hit_ratio = n_won / (n_won + n_lost)
    # payoff
    payoff_bet_mean = np.mean(z)
    payoff_bet_wins = np.sum(z[z > 0]) / n_won
    # streak
    streak = streaks_analysis(x=z)
    streak = np.array(streak)
    streak_win_mean = np.mean(streak[streak > 0])
    streak_lose_mean = np.abs(np.mean(streak[streak < 0]))
    streak_win_max = np.max(streak[streak > 0])
    streak_lose_max = np.abs(np.min(streak[streak < 0]))
    rn = ['hit_ratio', 'payoff_bet_mean', 'payoff_bet_wins', 'streak_win_mean',
          'streak_lose_mean', 'streak_win_max', 'streak_lose_max']
    va = [hit_ratio, payoff_bet_mean, payoff_bet_wins, streak_win_mean,
          streak_lose_mean, streak_win_max, streak_lose_max]
    q = pd.DataFrame(va, columns=['val'], index=rn)
    return q



def streaks_analysis(x):
    """Returns streaks of positive / negative streaks."""
    z = [1 if i > 0 else 0 for i in x]
    y = []
    p = 1
    for j in range(1, len(z)):
        if z[j] - z[j - 1] == 0:
            p += 1
        else:
            if z[j - 1] == 1:
                y.append(p)
            else:
                y.append(-p)
            p = 1
    # last iteration to add
    y.append(p * (1 if z[j - 1] == 1 else -1))
    return y








