

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

df_tmp = pd.read_excel('data/all-euro-data-2018-2019.xlsx', sheet_name='E0')
df_tmp.head()

df = pd.read_excel('data/all-euro-data-2018-2019.xlsx', sheet_name=None)

df_cons = pd.DataFrame.from_dict(df, orient='index')

df_cons = pd.DataFrame([df], index='Div', column)

df['E0']

df_cons.head()
df_cons.columns



