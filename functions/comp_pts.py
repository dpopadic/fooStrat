def comp_pts(res):
    """Returns the points scored for each game given a string."""
    # defining won, draw, lost
    res_def = ['H','D','A']
    if res=='H':
        score = 3
    elif res=='D':
        score = 1
    elif res=='A':
        score = 0
    else:
    score = 0
    return(score)


def comp_pts(res, persp):
    """Returns the points scored for each game given a string and
    the perspective (home / away)."""
    if res=='H' & persp=='home':
        score = 3
    elif res=='H' & persp=='away':
        score = 0
    elif res=='A' & persp=='home':
        score = 0
    elif res=='A' & persp=='away':
        score = 3
    elif res=='D':
        score = 1
    else:
        score = 0
    return(score)





