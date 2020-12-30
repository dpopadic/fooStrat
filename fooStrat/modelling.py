import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from fooStrat.helpers import class_accuracy_stats, transform_range
import fooStrat.servicers as fose


def est_prob(factors, results, feature):
    """Estimate probability of an event occuring (eg. win) for a factor using a naive bayes model. The
    estimation uses a 3 season non-overlapping window. Note that the probability estimation is in-sample
    and only provides a crude guide.

    Parameters:
    -----------
        scores (dataframe):     a dataframe with at least columns date, team, field, val (eg. goal_superiority)
        result (dataframe):     a dataframe with results and columns date, team & val (eg. 0/1 for loss/win)
        field (string):         the field in scores to uses to fit the model (eg. "goal_superiority")

    Returns:
    --------
        A few objects are returned:
                1. A dataframe with probabilities for each event
                2. Evaluation statistics

    # Details:
    ----------
        Note that the probabilities are related to the 1-event (eg. win).

    """
    sfd = factors.query("field==@feature").reset_index(drop=True)
    sfd = fose.append_custom_window(sfd, k=3)
    acon = sfd.pivot_table(index=['season', 'div', 'date', 'team', 'window'],
                           columns='field',
                           values='val').reset_index()
    # merge with results
    prob = pd.merge(results, acon,
                    on=['div', 'season', 'date', 'team'],
                    how='right')
    prob.dropna(inplace=True)
    prob.reset_index(drop=True, inplace=True)
    # estimate probability
    prob['proba'] = prob.groupby(['team', 'window'],
                                 as_index=False,
                                 group_keys=False)[['val', feature]].apply(lambda x: mod_est_nb(x))
    # accurary evaluation
    y = prob['val'].to_numpy()
    y_pred = prob['proba'].apply(lambda x: 1 if x >= 0.5 else 0).to_numpy()
    conf_mat = confusion_matrix(y, y_pred)
    stats = class_accuracy_stats(conf_mat)
    # reshape results
    prob = prob.drop(['val', feature], axis=1)
    prob.rename(columns = {'proba': 'val'}, inplace=True)
    return prob, stats



def mod_est_nb(x):
    """Estimate target variable using naive bayes model."""
    xed = x.drop('val', axis=1).values.reshape(len(x), -1)
    y = x['val'].values
    # note: that output is 2d array with 1st (2nd) column probability for 0 (1) with 0.5 threshold
    z = GaussianNB().fit(xed, y).predict_proba(xed)[:, 1]
    return pd.Series(z, index=x.index).to_frame()



def con_mod_datset_0(factors, results):
    """Construct the modelling data set.

    Parameters:
    -----------
        scores:     pandas dataframe
                    signals for each team with columns season, div, date, team, field, val
        results:    pandas dataframe
                    results of games with columns season, div, date, team, val

    """
    # reshape to wide format
    acon = factors.pivot_table(index=['season', 'div', 'date', 'team'],
                               columns='field',
                               values='val').reset_index()

    rcon = results.drop(['field'], axis=1)
    rcon.rename(columns={'val': 'result'}, inplace=True)

    # signals and results
    arcon = pd.merge(rcon, acon,
                     on=['div', 'season', 'date', 'team'],
                     how='inner')

    # drop rows where variables have no data at all
    arcon = arcon.dropna().reset_index(level=0, drop=True)

    return arcon



def con_mod_datset_1(data, per_ind, t_fit, t_pred, per, categorical=None, pred_mode=False):
    """Construct the modelling dataset for a single model fit at time t. The default lookback
    period is 3 years. The model is only fitted at dates specified in per_ind.

    Parameters:
    -----------
        data:       pd dataframe
                    a table with factor data and key columns date, div, season, team, result, factor_1, .., factor_n
        per_ind:    pd dataframe
                    a table with columns div, date representing the dates on which games took place
        t_fit:      datetime64
                    a date of interest for which to fit the model
        t_pred:     datetime64
                    a upper bound date for which to make predictions
        per:        str
                    a string indicating the lookback period to use for the model data set (eg. '52W')
        categorical: list
                    a list of categorical features if any
        pred_mode:  boolean, False
                    in prediction mode (True) or not (False) - this matters since the prediction date is
                    usually far out & hence the lookback period needs to be effective

    Details:
    --------
        For every point in time t, the last n observations are in X_train up to t-1 and X_test
        includes all observations for t that need to be predicted. The id_test output object
        provides all meta-data/keys for this prediction set.

    Returns:
    --------
        X_train, X_test, y_train, id_test
    """
    # consider only last n obervations (adjustment needed in prediction mode)
    if pred_mode is False:
        per_ind_t = per_ind.query("date <= @t_pred").set_index('date').last(per).reset_index()
    else:
        # extract prediction date to filter relevant estimation window & add back afterwards
        t_pred_ed = per_ind['date'].iloc[-2]
        per_ind_t = per_ind.query("date <= @t_pred_ed").set_index('date').last(per).reset_index()
        per_ind_t = pd.concat([per_ind_t, per_ind.tail(1)], axis=0, sort=True).reset_index(drop=True)

    data_edoh = pd.merge(data, per_ind_t['date'], how="inner", on="date")
    # one-hot encoding
    if categorical is not None:
        data_edoh = pd.get_dummies(data_edoh, columns=categorical)

    # training data set
    as_train = data_edoh[data_edoh['date'] <= t_fit].reset_index(drop=True)
    as_train_0 = as_train.drop(['date', 'div', 'team', 'season'], axis=1)

    # prediction data set
    as_test = data_edoh[(data_edoh['date'] > t_fit) & (data_edoh['date'] <= t_pred)].reset_index(drop=True)
    as_test_0 = as_test.drop(['date', 'div', 'team', 'season'], axis=1)

    # explanatory and target variables declarations
    # -- train
    y_train = as_train_0['result'].values
    X_train = as_train_0.drop('result', axis=1).values
    # -- test
    X_test = as_test_0.drop('result', axis=1).values

    # meta data with keys
    meta_test = as_test.loc[:, ['date', 'div', 'season', 'team', 'result']]

    return X_train, X_test, y_train, meta_test



def est_hist_proba(data,
                   est_dates,
                   start_date=None,
                   lookback='156W',
                   categorical=None,
                   models=['nb', 'knn', 'lg', 'dt'],
                   by='team'):
    """Estimate historical probability using an ensemble model. By default,
    four classification models are estimated: naive bayes, knn, logistic regression
    and a random forest tree model. Models are estimated for each team by default."""
    per_iter = mod_periods(est_dates=est_dates, start_date=start_date)
    per_ind = est_dates[['div', 'season', 'date']]
    res = pd.DataFrame()
    for t in range(1, len(per_iter)):
        t_fit = per_iter[t - 1]
        t_pred = per_iter[t]
        dfz = data.groupby(by,
                           as_index=False,
                           group_keys=False).apply(lambda x: est_proba_ensemble(data=x,
                                                                                per_ind=per_ind,
                                                                                t_fit=t_fit,
                                                                                t_pred=t_pred,
                                                                                lookback=lookback,
                                                                                categorical=categorical,
                                                                                models=models))
        res = pd.concat([res, dfz])

    return res


def est_proba_nb(data, per_ind, t_fit, t_pred, lookback, categorical):
    """Estimate historical probabilities."""
    X_train, X_test, y_train, meta_test = con_mod_datset_1(data=data,
                                                           per_ind=per_ind,
                                                           t_fit=t_fit,
                                                           t_pred=t_pred,
                                                           per=lookback,
                                                           categorical=categorical)
    if len(X_train) < 1 or len(X_test) < 1:
        est_proba = pd.DataFrame()
    else:
        # make no predictions if only 1 class (eg. win) is present in training set (revisit this later)
        try:
            z = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
            est_proba = pd.concat([meta_test, pd.DataFrame(z, columns=['val'])], axis=1)
        except:
            est_proba = pd.DataFrame()

    return est_proba



def est_proba_ensemble(data, per_ind, t_fit, t_pred, lookback, categorical, models, pred_mode=False):
    """Estimate historical probabilities."""
    X_train, X_test, y_train, meta_test = con_mod_datset_1(data=data,
                                                           per_ind=per_ind,
                                                           t_fit=t_fit,
                                                           t_pred=t_pred,
                                                           per=lookback,
                                                           categorical=categorical,
                                                           pred_mode=pred_mode)
    if len(X_train) < 1 or len(X_test) < 1:
        est_proba = pd.DataFrame()
    else:
        # make no predictions if only 1 class (eg. win) is present in training set (revisit this later)
        try:
            # fit various models
            z_nb = z_knn = z_lg = z_dt = [np.nan for i in range(len(X_test))]
            if 'nb' in models:
                z_nb = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
            if 'knn' in models:
                z_knn = KNeighborsClassifier(n_neighbors=50).fit(X_train, y_train).predict_proba(X_test)[:, 1]
            if 'lg' in models:
                z_lg = LogisticRegression().fit(X_train, y_train).predict_proba(X_test)[:, 1]
            if 'dt' in models:
                z_dt = DecisionTreeClassifier(max_depth=10,
                                              max_features="sqrt",
                                              min_samples_leaf=30,
                                              criterion="gini").fit(X_train, y_train).predict_proba(X_test)[:, 1]
            # average probability
            z = np.nanmean([z_nb, z_knn, z_lg, z_dt], axis=0)
            est_proba = pd.concat([meta_test, pd.DataFrame(z, columns=['val'])], axis=1)
        except:
            est_proba = pd.DataFrame()

    return est_proba






def mod_periods(est_dates, start_date=None, latest_only=False):
    """Construct estimation period set for modelling.

    Details: If needed, provide one of:
                start_date:     when the estimation should start
                latest_only:    to
    """
    if start_date is not None:
        tmp = est_dates.loc[est_dates['date'] >= start_date, 'est_date']
        per_iter = pd.DataFrame(tmp.unique(), columns=['date'])
    else:
        per_iter = est_dates['est_date']
        per_iter = pd.DataFrame(per_iter.unique(), columns=['date'])

    if latest_only is not False:
        per_iter = per_iter.tail(1)

    per_iter = per_iter[per_iter['date'].notnull()].date
    per_iter.reset_index(drop=True, inplace=True)
    return per_iter





def est_hist_prob_rf(arcon, est_dates, start_date=None):
    """Estimate probability using a random forest classification model."""

    # global ml parameter settings
    # setup the parameters and distributions to sample from
    param_dist = {"max_depth": [10, None],
                  "max_features": ['log2', 'auto', 'sqrt'],
                  "min_samples_leaf": [2, 10, 20],
                  "criterion": ["gini", "entropy"]}

    # construct date universe
    per_ind = est_dates[(est_dates['div'] == arcon['div'].iloc[0])]
    if start_date is not None:
        per_iter = per_ind[(est_dates['date'] >= start_date)]['date']
    else:
        per_iter = per_ind['date']

    res = pd.DataFrame()
    for t in per_iter:
        # t = per_iter.iloc[0]
        X_train, X_test, y_train, id_test = con_mod_datset_1(data=arcon,
                                                             per_ind=per_ind,
                                                             t=t,
                                                             per='312W')
        # instantiate a Decision Tree classifier
        # tree = DecisionTreeClassifier()
        # instantiate the RandomizedSearchCV object
        # tree_cv = GridSearchCV(estimator=tree, param_grid=param_dist, cv=5)

        # instantiate ada..
        tree = DecisionTreeClassifier(max_depth=10,
                                      max_features="auto",
                                      min_samples_leaf=10,
                                      random_state=1)
        ada = AdaBoostClassifier(base_estimator=tree,
                                 n_estimators=10,
                                 random_state=1)
        ada.fit(X_train, y_train)
        pred = ada.predict_proba(X_test)
        pred = pd.DataFrame(pred, columns=ada.classes_)

        # fit it to the data
        #tree_cv.fit(X_train, y_train)
        #y_pp = tree_cv.predict_proba(X_test)
        #y_pp = pd.DataFrame(y_pp, columns=tree_cv.classes_)
        # stats.describe(y_pp)

        # add back id info
        # res_0 = pd.concat([arcon_spec, y_pp], axis=1)
        tmp = pd.concat([id_test, pred], axis=1)
        res = pd.concat([res, tmp])

    res.reset_index(drop=True, inplace=True)
    return res




def comp_mispriced(prob, odds, prob_threshold, res_threshold):
    """
    Parameters
    ----------
    prob:           pandas dataframe
                    implied probabilities from a model for each event with columns date, team
    odds:           pandas dataframe
                    market odds from bookmaker
    prob_threshold: float
                    implied probability threshold for events to look at
    res_threshold:  float
                    magnitude of mispricing residual to look at
    Returns
    -------
    A pandas dataframe with mispriced events.

    """
    resi = pd.merge(odds.rename(columns={'val': 'odds'}),
                    prob.rename(columns={'val': 'implied'}),
                    on=["div", "season", "date", "team"],
                    how="inner")
    resi["market"] = 1 / resi.loc[:, "odds"]
    # scale estimated probabilities to the implied range
    resi["implied"] = transform_range(x = resi['implied'], y = resi['market'])
    # compute residuals
    resi["resid"] = resi["implied"] - resi["market"]
    pos = resi.query("resid>@res_threshold & implied>@prob_threshold")
    pos = pos[['season', 'div', 'date', 'team', 'implied', 'market']]
    pos.reset_index(inplace=True, drop=True)
    return pos



