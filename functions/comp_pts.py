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
