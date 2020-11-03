from fooStrat.features import feat_odds_volatility, feat_odds_accuracy

match_odds = pd.read_pickle('data/pro_data/match_odds.pkl')
odds = match_odds
data = source_core

def feat_odds_uncertainty(data, odds):
    """Derives the prediction/odds uncertainty features.
        - volatility of odds (the higher, the better)
        - odds prediction uncertainty (the less accurate, the better)
        - pricing spread (the higher, the better)
    """
    # --- odds volatility
    df1 = feat_odds_volatility(data=data)

    # --- historical odds prediction accuracy
    df2 = feat_odds_accuracy(data=data, odds=odds)
    df2_ed = df2.query("field in ['win', 'lose']").groupby(['div', 'season', 'team']).agg('mean').reset_index()
    # reverse direction
    df2_ed['val'] = 1 - df2_ed['val']
    df2_ed['field'] = "odds_accuracy"
    # expand field
    date_univ = fose.con_date_univ(data=data)
    tmp = fose.expand_field(data=df2_ed, dates=date_univ, keys=['div', 'season', 'team', 'field'])
    a = tmp.query("team=='liverpool'")

    return data

























