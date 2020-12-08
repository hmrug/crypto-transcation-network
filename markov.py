#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 16:08:13 2020

@author: joel
"""

import networkx as nx
import pandas as pd
import numpy as np
import os
import io
import json
import argparse
import logging
import glob
import random
import multiprocessing
from multiprocessing import Process, Queue
from time import time


path = "/home/joel/GitHub/crypto-transcation-network/results/bow_tie_json_output"
files = glob.glob(path+"/20*")
files.sort()

states = ["ssc","in","out","tubes","tendrils","fringe","disconnected","inactive"]
transition_matrix = np.zeros(shape=(len(states),len(states)),dtype=int)

for i in range(len(files)-1):
    file_A = files[i]
    with open(file_A, 'r') as myfile:
        data_A=myfile.read()
        
    file_B = files[i+1]
    with open(file_B, 'r') as myfile:
        data_B=myfile.read()
    
    A = json.loads(data_A)
    B = json.loads(data_B)
    
    nodes_A , nodes_B= set(A.keys()), set(B.keys())
    # union_nodes = nodes_A.intersection(nodes_B)
    # to_inactive = nodes_A - nodes_B
    # to_active = nodes_B - nodes_A 
    
    nodes = nodes_A.union(nodes_B)
    #transition_matrix = np.zeros(shape=(len(states),len(states)),dtype=int)
    # transition_matrix_miner = np.zeros(shape=(len(states),len(states)),dtype=int)
    # transition_matrix_sink = np.zeros(shape=(len(states),len(states)),dtype=int)
    
    for node in list(nodes):
        attr_A , attr_B = A.get(node), B.get(node)
        state_A = attr_A['bt_comp'] if attr_A != None else 'inactive'
        state_B = attr_B['bt_comp'] if attr_B != None else 'inactive'
        index_A, index_B = states.index(state_A), states.index(state_B)
        transition_matrix[index_A][index_B] += 1
    
transition_matrix_pct =  transition_matrix/transition_matrix.sum()