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
