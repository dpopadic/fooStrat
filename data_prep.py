import pandas as pd
import os
# undo latest commit Alt + 9 -> log Tab -> select last commit

# single sheet visualisation..
df_tmp = pd.read_excel('src_data/all-euro-data-2018-2019.xlsx', sheet_name='E0')
df_tmp.head()

# major leagues data
# ---
src_dat_path = os.path.join(os.getcwd(), 'src_data', '')
fi_nm = ['src_data/' + f for f in os.listdir(src_dat_path) if f[:13] == 'all-euro-data']

df = pd.DataFrame()
for f in fi_nm:
    df0 = pd.read_excel(f, sheet_name=None)
    for key, i in df0.items():
        df = df.append(i, ignore_index=True, sort=False)
df.to_pickle('./pro_data/major_leagues.pkl')


# niche leagues data
# ---
di = pd.read_excel('src_data/new_leagues_data.xlsx', sheet_name=None)
df0 = pd.DataFrame()
for key, i in di.items():
    df0 = df0.append(i, ignore_index=True)
df0.to_pickle('./pro_data/niche_leagues.pkl')

