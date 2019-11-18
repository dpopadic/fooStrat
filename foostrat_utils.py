def comp_pts(res):
    """Returns the points scored for each game given a string of W, D or L."""
    if res=='W':
        score = 3
    elif res=='L':
        score = 0
    elif res=='D':
        score = 1
    else:
        score = 0
    return(score)

def reconfig_res(res, persp):
    """Returns W, D, L for each game given a string of H, D or A and
    the perspective (home / away)."""
    if res=='H' and persp=='home':
        score = 'W'
    elif res=='H' and persp=='away':
        score = 'L'
    elif res=='A' and persp=='home':
        score = 'L'
    elif res=='A' and persp=='away':
        score = 'W'
    elif res=='D':
        score = 'D'
    else:
        score = ''
    return(score)

def ret_xl_cols(file_names, id_col):
    """Returns all available columns across all tabs and multiple excel files."""
    df_cols = pd.DataFrame()
    for f in file_names:
        df0 = pd.read_excel(f, sheet_name=None)
        for key, i in df0.items():
            seas = f[23:32]
            if (i.shape[0] == 0):
                val = np.nan
            else:
                val = i.loc[1, id_col]
            df_tmp = pd.DataFrame({"field": i.columns.values, id_col: val, "season": seas})
            df_cols = df_cols.append(df_tmp, ignore_index=True, sort=False)
    return(df_cols)


