

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

df = pd.read_excel('data/all-euro-data-2018-2019.xlsx', sheet_name='E0')
df.head()
df.columns



