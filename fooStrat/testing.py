import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import GaussianNB
from scipy.stats import zscore


data = source_core.query("div == 'E0'").reset_index(drop=True)

a = dfac_fil.query("team == 'liverpool' & season == '2020'")

df = pd.DataFrame({
    'y': np.random.randn(20),
    'x1': np.random.randn(20),
    'x2': np.random.randn(20),
    'grp': ['a', 'b'] * 10})

def ols_res(x):
    xed = x[['x1', 'x2']].values.reshape(len(x), -1)
    y = x['y'].values
    z = LinearRegression().fit(xed, y).predict(xed)
    return pd.Series(z, index=x.index)

df['pred'] = df.groupby('grp', as_index=False, group_keys=False).apply(lambda x: ols_res(x))


df = pd.DataFrame({
    'y': [0] * 10 + [1] * 10,
    'x1': np.random.randn(20),
    'x2': np.random.randn(20),
    'grp': ['a', 'b'] * 10})
x = df
def nb_res(x):
    xed = x[['x1', 'x2']].values.reshape(len(x), -1)
    y = x['y'].values
    z = GaussianNB().fit(xed, y).predict_proba(xed)[:, 1]
    return pd.Series(z, index=x.index)

df['pred'] = df.groupby('grp', as_index=False, group_keys=False).apply(lambda x: nb_res(x))





a = dasetmod.query("date <= @t_pred").set_index('date').last('156W').reset_index()
d = a.team.unique()
b = a.query("team=='bournemouth'").reset_index(drop=True)

for i in range(0, len(d)):
    ik = d[i]
    b = a.query("team==@ik").reset_index(drop=True)
    X_train, X_test, y_train, meta_test = con_mod_datset_1(data=b,
                                                           per_ind=per_ind,
                                                           t_fit=t_fit,
                                                           t_pred=t_pred,
                                                           per='156W')
    if len(X_train) < 1 or len(X_test) < 1:
        est_proba = pd.DataFrame()
    else:
        # make no predictions if only 1 class (eg. win) is present in training set (revisit this later)
        try:
            z = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
            est_proba = pd.concat([meta_test, pd.DataFrame(z, columns=['val'])], axis=1)
        except:
            est_proba = pd.DataFrame()

    print(ik)











