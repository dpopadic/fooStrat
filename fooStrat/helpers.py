import pandas as pd
import os

def anti_join(x, y, on):
    """Anti-join function that returns rows from x not matching y."""
    oj = x.merge(y, on=on, how='outer', indicator=True)
    z = oj[~(oj._merge == 'both')].drop('_merge', axis=1)
    return z


def ver_type(data, field):
    """Make sure data types in a dataframe are as desired. Make adjustments if not.

    Parameters:
    -----------
        data:   pandas dataframe
                the data that needs to be checked
        field:  dict
                the fields with target data types. Options are:

                    str:        object
                    float:      float64
                    int:        int64
                    date:       datatime64

                For example, one wants an input field in data to be a string. In that case,
                you set field = {'my_column': 'str'} and the my_column field is checked whether
                it is a string (object) and converted to it if not.

    Example:
    --------


    """
    # the template to compare desired types to
    temp = {'str': 'object',
            'float': 'float64',
            'int': 'int64',
            'date': 'datetime'}

    for (key, value) in field.items():
        i = [key, value]
        if data[i[0]].dtypes == temp[i[1]]:
            pass
        else:
            data = data.copy()
            if i[1] == "int":
                data[i[0]] = pd.to_numeric(data[i[0]], downcast='signed', errors='coerce')
            elif i[1] == "float":
                data[i[0]] = pd.to_numeric(data[i[0]], errors='coerce')
            elif i[1] == "str":
                data[i[0]] = pd.to_string(data[i[0]])
            elif i[1] == "date":
                data[i[0]] = pd.to_datetime(data[i[0]], errors='coerce')

    return data


def jitter(x, noise_reduction=1000000):
    """Add noise to a series of observations. Useful for ranking functions.
    Parameters:
    -----------
        x (series): a series of numerical observations
        noise_reduction (int): magnitude of noise reduction (higher values mean less noise)
    Example:
    --------
        x = np.random.normal(0, 1, 100).transpose()
        y = jitter(x, noise_reduction=100)
        compare = pd.DataFrame([x, y])
    """
    l = len(x)
    stdev = x.std()
    z = (np.random.random(l) * stdev / noise_reduction) - (stdev / (2 * noise_reduction))
    return z



def class_accuracy_stats(conf_mat):
    """Calculate relevant ratio's from the confusion matrix with two classes.

    Parameters:
    -----------
        conf_mat (array):   a confusion matrix with two classes

    Returns:
    --------
        Summary statistics in ratio format.

    Details:
    --------
        The following stats are calculated:
            accuracy:   (tp + tn) / (tp + tn + fp + fn)
            precision:  tp / (tp + fp) (also called positive predictive value - PPV)
            recall:     tp / (tp + fn) (also called sensitivity, hit-rate, true-positive rate)
            F1 score:   2 * (precision * recall) / (precision + recall) -> harmonic mean of precision & recall

        Interpretation with spam-email classification:
            high precision:     not many real emails predicted as spam
            high recall:        predicted most spam emails correctly

    """
    TN = conf_mat[0, 0]
    FN = conf_mat[1, 0]
    FP = conf_mat[0, 1]
    TP = conf_mat[1, 1]
    pre = TP / (TP + FP)
    rec = TP / (TP + FN)
    x = {'accuracy': (TP + TN) / conf_mat.sum(),
         'precision': pre,
         'recall':  rec,
         'f1': 2 * pre * rec / (pre + rec)
         }
    x = pd.DataFrame.from_dict(x, orient="index", columns=["val"])
    return x


def transform_range(x, y):
    xmin = x.min()
    xmax = x.max()
    ymin = y.min()
    ymax = y.max()
    z = ((x - xmin) / (xmax - xmin)) * (ymax - ymin) + ymin
    return z


