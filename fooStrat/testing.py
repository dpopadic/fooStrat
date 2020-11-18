import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import GaussianNB
from scipy.stats import zscore

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








