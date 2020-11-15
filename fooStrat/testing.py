import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

df = pd.DataFrame({
    'y': np.random.randn(20),
    'x1': np.random.randn(20),
    'x2': np.random.randn(20),
    'grp': ['a', 'b'] * 10})

def ols_res(x, y):
    x_2d = x.values.reshape(len(x), -1)
    return pd.Series(LinearRegression().fit(x_2d, y).predict(x_2d))

df.groupby('grp').apply(lambda df: df[['x1', 'x2']].apply(ols_res, y=df['y']))


def ols_res(x):
    x_2d = x[['x1', 'x2']].values.reshape(len(x), -1)
    y = x['y'].values
    z = LinearRegression().fit(x_2d, y).predict(x_2d)
    return pd.Series(z)

df['yz'] = df.groupby('grp')['y'].transform(lambda x: zscore(x))

df.groupby('grp').apply(lambda x: ols_res(x))















