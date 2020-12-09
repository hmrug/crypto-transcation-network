#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 09:58:07 2020

@author: joel
"""

# visualisation 
import pandas as pd
import numpy as np
import os
import io
import json
import glob
from time import time
import argparse

#################### Parser settings #########################################
parser = argparse.ArgumentParser(description='Detect groups in a video')

parser.add_argument("file_dir", help='directory of the json bow tie files')

parser.add_argument(
    "-o", "--output_dir",
    help='name of the json output directory',
    default="results")

def main(file_dir, output_dir ):
    
    files = glob.glob(file_dir)
    files.sort()
    
    bt_dict = dict()
    states = ["ssc","in","out","tubes","tendrils","fringe","disconnected"]
    
    # extension "_s" if transaction is sunk and "_m" if node is miner
    states_extended = np.array(list(map(lambda x: [x, x + '_s', x + '_m'], states))).ravel()
    
    for file in files:
        
        with open(file, 'r') as bt_file:
            data = bt_file.read()
            
        bt_data = json.loads(data)
        
        comp_count = dict(zip(states_extended, [0]*len(states_extended))) 
        for _, attr in bt_data.items():
            comp = attr['bt_comp']
            comp_count[comp] +=1
            
            # check for sunk transactions
            if attr['is_sink']:
                comp_count[comp + '_s'] +=1
            
            # check if node is miner
            if attr['is_miner']:
                comp_count[comp + '_m'] +=1
            
        bt_comp = {file[-15:-5]:comp_count}
        bt_dict.update(bt_comp )
        
    with io.open(os.path.join(output_dir, "bt_comp_count.json"), 'w') as json_file:
       json_file.write(json.dumps(bt_dict))

# output_dir = '/home/joel/GitHub/crypto-transcation-network'
# file_dir = "/home/joel/GitHub/crypto-transcation-network/results/bow_tie_json_output/20*"
# main(file_dir,output_dir)
# python bt_visualize.py "/home/joel/GitHub/crypto-transcation-network/results/bow_tie_json_output/20*" -o "/home/joel/GitHub/crypto-transcation-network/results"

if __name__ == "__main__":
    args = parser.parse_args()
    main(**vars(args))