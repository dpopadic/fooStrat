# test task ----------------------
# import pandas as pd
# import numpy as np
# df_test = pd.DataFrame({'x': np.random.normal(0.05, 0.3, 1000),
#                         'y': np.random.normal(0.07, 0.9, 1000)})
# df_test.to_pickle('./pro_data/df_test.pkl')

from datetime import datetime
myFile = open('append.txt', 'a')
myFile.write('\nAccessed on ' + str(datetime.now()))
