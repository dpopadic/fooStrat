# -----------------------------------------------
# --- LEAGUE STANDINGS: MAJOR LEAGUES
# -----------------------------------------------
import pandas as pd
import numpy as np

# TensorFlow, Theano, PyTorch, Keras, Scikit-Learn, NumPy, SciPy, Pandas, statsmodels


df = pd.read_pickle('pro_data/major_leagues.pkl')
df.head()

# see all column names..
for col in df.columns:
    print(col)

ml_map = pd.DataFrame(Competition = {'E0':'England Premier League', 'E1':'England Championship League'})




