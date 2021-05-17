# pylint: disable=C0103
"""
Python script "Experiment_class.py"
by Matthew Garcia, Postdoctoral Research Associate
Dept. of Forest and Wildlife Ecology
University of Wisconsin - Madison
matt.e.garcia@gmail.com

Copyright (C) 2021 by Matthew Garcia
"""


class Experiment:
    """SBW flight modeling experiment details."""

    def __init__(self, var_name, idx, var_value):
        self.variable = var_name
        self.index = idx
        self.value = var_value


def gen_experiments():
    experiments = dict()
    experiments['default'] = Experiment('None', 0, 0)
    #
    var = 'min_windspeed'
    start_idx, end_idx = 1, 9
    min_val, max_val, val_inc = 0.0, 4.0, 0.5
    for i in range(start_idx, end_idx+1):
        experiments['%d' % i] = Experiment(var, i, min_val + val_inc * (i - start_idx))
    #
    var = 'wingbeat_eff'
    start_idx, end_idx = 11, 30
    min_val, max_val, val_inc = 0.1, 2.0, 0.1
    for i in range(start_idx, end_idx+1):
        experiments['%d' % i] = Experiment(var, i, min_val + val_inc * (i - start_idx))
    #
    start_idx, end_idx = 241, 249
    min_val, max_val, val_inc = 1.41, 1.49, 0.01
    for i in range(start_idx, end_idx+1):
        experiments['%d' % i] = Experiment(var, i, min_val + val_inc * (i - start_idx))
    #
    start_idx, end_idx = 251, 259
    min_val, max_val, val_inc = 1.51, 1.59, 0.01
    for i in range(start_idx, end_idx+1):
        experiments['%d' % i] = Experiment(var, i, min_val + val_inc * (i - start_idx))
    #
    start_idx, end_idx = 261, 269
    min_val, max_val, val_inc = 1.61, 1.69, 0.01
    for i in range(start_idx, end_idx+1):
        experiments['%d' % i] = Experiment(var, i, min_val + val_inc * (i - start_idx))
    #
    var = 'delta_nu'
    start_idx, end_idx = 35, 50
    min_val, max_val, val_inc = 0.85, 1.00, 0.01
    for i in range(start_idx, end_idx+1):
        experiments['%d' % i] = Experiment(var, i, min_val + val_inc * (i - start_idx))
    return experiments

# end Experiment_class.py
