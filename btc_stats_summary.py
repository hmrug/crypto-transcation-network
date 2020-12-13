# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 21:03:45 2020

@author: Besitzer
"""

import networkx as nx
import numpy as np
import os
import io
import json
import argparse
import logging
import glob
import random
from multiprocessing import Process, Queue
from time import time
import math


def files_walker(files, json_output, directory):
    d = {}
    d["g_nodes"] = []
    d["g_edges"] = []
    d["g_density"] = []
    d["std_in"] = []
    d["std_out"] = []
    d["skew_in"] = []
    d["skew_out"] = []
    d["date"] = []
    for file in files:
        # print(file)
        with open(directory+'/'+file, 'r') as f:
            data = json.load(f)
            d["g_nodes"].append(data["stats"][0])
            d["g_edges"].append(data["stats"][1])
            d["g_density"].append(data["stats"][2])
            d["std_in"].append(data["stats"][3])
            d["std_out"].append(data["stats"][4])
            d["skew_in"].append(data["stats"][5])
            d["skew_out"].append(data["stats"][6])
            d["date"].append(file[:10])
            # print(data["stats"])
    with open(json_output, "w") as fi:
        fi.write(json.dumps(d))
    return d


#################### Parser settings #########################################
#parser = argparse.ArgumentParser(description='Detect groups in a video')

#parser.add_argument("directory", help='directory of the graph files')

# parser.add_argument(
#    "-o", "--output",
#    help='name of the json output file',
#    default="results/output_json")


if __name__ == "__main__":
    start_time = time()
    logging.info("Start combining json files")

    files = os.listdir("/mnt/smbshares/lkunam/btc530k-heur-basic_stats")
    # print(files)
    directory = "/mnt/smbshares/lkunam/btc530k-heur-basic_stats"
    # print(directory)

    files_walker(files, "btc_stats.json", directory)

    end_time = time()
    seconds_elapsed = end_time - start_time
    hours, rest = divmod(seconds_elapsed, 3600)
    minutes, seconds = divmod(rest, 60)
    logging.info("json combination finished after {} hours {} minutes and {} seconds"
                 .format(hours, minutes, int(seconds)))
