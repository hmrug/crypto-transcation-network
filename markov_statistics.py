#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 08:10:05 2020

@author: joel
"""

import pandas as pd
import numpy as np
import os
import io
import json
from time import time

#statistics
path_tm = "/home/joel/GitHub/crypto-transcation-network/results"
file = os.path.join(path_tm, "transition_matrices.json")

with open(file, 'r') as tm_file:
    data = tm_file.read()

transition_dict = json.loads(data)
states = ["ssc","in","out","tubes","tendrils","fringe","disconnected","inactive"]

tm_matrix = np.zeros(shape=(len(states),len(states)),dtype=int)
for key, tm in transition_dict.items():
    tm_matrix += np.array(np.array(tm))
    
tm_matrix_pct = tm_matrix/tm_matrix.sum()

df = pd.DataFrame(tm_matrix, index=states, columns=states)
df_pct = df/df.sum().sum()*100