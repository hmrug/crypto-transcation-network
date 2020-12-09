#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 16:08:13 2020

@author: joel
"""

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

# python markov.py "/home/joel/GitHub/crypto-transcation-network/results/bow_tie_json_output/20*" -o "/home/joel/GitHub/crypto-transcation-network/results"

#################### Parser settings #########################################
parser = argparse.ArgumentParser(description='Detect groups in a video')

parser.add_argument("file_dir", help='directory of the json bow tie files')

parser.add_argument(
    "-o", "--output_dir",
    help='name of the json output directory',
    default="results")


# output_dir = '/home/joel/GitHub/crypto-transcation-network'
# file_dir = "/home/joel/GitHub/crypto-transcation-network/results/bow_tie_json_output/20*"

def main(file_dir, output_dir):
    
    files = glob.glob(file_dir)
    files.sort()
    
    # possible bow tie states
    # inactive meaning the node is either not in t or t+1
    states = ["ssc","in","out","tubes","tendrils","fringe","disconnected","inactive"]
    
    # dictionary where all the transition matrices will be stored with date as key
    transition_dict = dict()
    
    # go through all json bow tie output files and compare states from t with t+1
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
        
        # all nodes present in btc network at t and t+1    
        nodes = nodes_A.union(nodes_B)
        
        # initialize transition matrix (tm)
        transition_matrix = np.zeros(shape=(len(states),len(states)),dtype=int)
        
        # go through all nodes and compare its state in t with t+1 and update tm
        for node in list(nodes):
            attr_A , attr_B = A.get(node), B.get(node)
            state_A = attr_A['bt_comp'] if attr_A != None else 'inactive'
            state_B = attr_B['bt_comp'] if attr_B != None else 'inactive'
            index_A, index_B = states.index(state_A), states.index(state_B)
            transition_matrix[index_A][index_B] += 1
        
        # the key to the transition matrix is the date of t+1
        transition_dict.update({file_B[-15:-5]:transition_matrix.tolist()})
        
    with io.open(os.path.join(output_dir, "transition_matrices.json"), 'w') as json_file:
        json_file.write(json.dumps(transition_dict))

if __name__ == "__main__":
    args = parser.parse_args()
    main(**vars(args))