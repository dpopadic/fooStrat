import pandas as pd
import fooStrat.servicers as fose


def team_quality_cluster(data):
    """Calculates the team quality cluster features. The sub-factors are:
       - team quality cluster (by season)
       - consistency: autocorrelation of points scored (last 5 seasons)

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









