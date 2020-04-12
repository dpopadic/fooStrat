# MODEL CONSTRUCTION --------------------------------------------------------------------------------------------------

import pandas as pd


# DATA PREPARATIONS ---------------------------------------------------------------------------------------------------
factor_library = pd.read_pickle('pro_data/factor_library.pkl')

a = factor_library.query('div=="Argentina Superliga"').sort_values(['date','team'])

a = source_core.query('div=="Argentina Superliga" & field=="FTR"')

pd.pivot_table(factor_library)


data = source_core

