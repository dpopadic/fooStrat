import pandas as pd
import numpy as np
import fooStrat.servicers as fose

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



def reshape_wdl(data, event, as_numeric=False):
    """Reshape win, draw, lose events for teams.

    Parameters:
    -----------
        data:           pandas dataframe
                        A dataframe with columns season, date, div, home_team, away_team, field, val
        event:          str
                        How to shape the result. Options are:
                            win     highlight whether a team won with 0 / 1
                            lose    highlight whether a team lost with 0 / 1
                            draw    highlight whether a team drew with 0 / 1
                            wdl     highlight what the team did: win, lose, draw
        as_numeric:     boolean
                        when event is wdl, return `val` as string or numeric

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
        if as_numeric == True:
            res['val'] = res['val'].apply(lambda x: 1 if x == 'win' else (0 if x == 'draw' else -1))

    res = res.sort_values(['div', 'date']).reset_index(level=0, drop=True)

    return res


def con_res_wd(data, field, event=None, encoding=True):
    """
    Constructs the event result data in a manner that is readily available for back-testing.

    Parameters:
    -----------
        data (dataframe):       a dataframe with columns season, date, div, home_team, away_team, field, val
        field (string):         a string that defines the event (eg. 'FTR' for full-time results)
        event (string):         optional, a specific event only (eg. win)
        encoding (string):      whether to encode the events or not (defaults to True)

    Returns:
    --------
        A dataframe of results 0/1 with fields win, draw, lost for each team.

    Details:
    --------
        Encoding means that the val column for each event (eg. win) will be a 0/1 and each team will be represented
        twice (once with 1 and once with 0). When encoding is not desired, the val column will simply be 'win' for a
        specific team for example and each team is only represented once.

    Example:
    --------
    (encoding=True)
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
        if event is not None:
            res = reshape_wdl(data=res_tmp, event=event)
        else:
            d_win = reshape_wdl(data=res_tmp, event="win")
            d_lose = reshape_wdl(data=res_tmp, event="lose")
            d_draw = reshape_wdl(data=res_tmp, event="draw")

            res = pd.concat([d_win, d_lose, d_draw], axis=0, sort=True)
            res = res.sort_values(['date', 'div', 'season']).reset_index(level=0, drop=True)
    else:
        if event is None:
            event = 'wdl'
        res = reshape_wdl(data=res_tmp, event=event)

    return res



def con_res(data, obj, event=None):
    """Constructs results objects that are required for testing.

    Parameters:
    -----------
        data (dataframe):       a dataframe with columns season, date, div, home_team, away_team, field, val
        obj (string/list):      the object(s) to construct:
                                    gd:     goals difference by game
                                    wdl:     win or draw by game (binary 0/1 if won, drew or lost for each team)
        field (list or string): a string that defines the event for the object (eg. 'FTR' when wd or
                                ['FTHG', 'FTAG'] when gd)
        event (string)          optional, when obj is wdl, a specific event of interest only (eg. win)

    Returns:
    --------
        A dataframe with the results in optimal shape.

    """
    wdl = gd = None
    if "wdl" in obj:
        wdl = con_res_wd(data=data, field='FTR', event=event)

    if "gd" in obj:
        gd = con_res_gd(data=data, field=['FTHG', 'FTAG'])

    if len(obj) <= 1 and obj[0] == 'wdl':
        res = wdl
    elif len(obj) <= 1 and obj[0] == 'gd':
        res = gd
    else:
        res = {'wdl': wdl, 'gd': gd}

    return res





