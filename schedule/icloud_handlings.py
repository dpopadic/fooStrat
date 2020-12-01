import pandas as pd
fp = '/Users/dariopopadic/Library/Mobile Documents/com~apple~CloudDocs/PycharmProjects/'
fl = 'leagues_map.pkl'
df = pd.read_pickle(fp + fl)
df.to_pickle(fp + 'df.pkl')
