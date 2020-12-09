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
import multiprocessing
from multiprocessing import Process, Queue
from time import time
import math
from scipy.stats import skew


def calculate_btc_stats(g):
    g_nodes = len(g.nodes())
    g_edges = len(g.edges())
    g_density = nx.density(g)
    std_in = np.std(list(dict(g.in_degree()).values()))
    std_out = np.std(list(dict(g.out_degree()).values()))
    skew_in = skew(list(dict(g.in_degree()).values()))
    skew_out = skew(list(dict(g.out_degree()).values()))
    return (g_nodes, g_edges, g_density, std_in, std_out, skew_in, skew_out)


def files_walker(files, output_dir):

    stats_dict = {}

    for file in files:
        logging.info("Analysing data from {}".format(file[-18:-8]))
        G = nx.read_graphml(file)
        stats = calculate_btc_stats(G)
        stats_dict["stats"] = stats

        try:
            with io.open(os.path.join(output_dir, file[-18:-8]+".json"), 'w') as json_file:
                json_file.write(json.dumps(stats_dict))

                logging.info(
                    "writing bow tie component from {}".format(file[-18:-8]))
                logging.info("#" * 80)

        except OSError as e:
            logging.error(e)

    return True


#################### Parser settings #########################################
parser = argparse.ArgumentParser(description='Detect groups in a video')

parser.add_argument("directory", help='directory of the graph files')

parser.add_argument(
    "-o", "--output",
    help='name of the json output file',
    default="results/output_json")


def main(directory=None, output=None):

    if directory is None:
        return False

    if not os.path.exists(output):
        os.makedirs(output)

    start_time = time()

    logging.basicConfig(filename=os.path.join(output, "logfile.log"),
                        level=logging.DEBUG, format='%(asctime)s :%(message)s')

    logging.info("Start analysing BTC network")
    logging.info('Start Analysing bow tie structure in {}'.format(directory))

    nr_cores = multiprocessing.cpu_count()
    logging.info(
        'This machine has {} cores which can be used'.format(nr_cores))

    files = glob.glob(directory)
    # random.shuffle(files)
    files.sort()

    nr_processes = min(len(files), nr_cores)
    logging.info('Run {} jobs'.format(nr_processes))

    # devide files in bins for the different processes
    # early files always get computed fist but distributed evenly among cores
    rep = math.ceil((len(files)/nr_processes))
    index = list(range(nr_processes)) * rep
    index = index[:len(files)]

    # rolling bins
    bins = [[] for _ in range(nr_processes)]
    for i, file in enumerate(files):
        idx = index[i]
        bins[idx].append(file)

    jobs = list()

    for i in range(nr_processes):
        #process_name = f"Process_{i}"
        jobs.append(Process(target=files_walker, args=(bins[i], output)))

    for i, process in enumerate(jobs):
        process.start()
        logging.info("started process_{}".format(i+1))

    for process in jobs:
        process.join()

    end_time = time()
    seconds_elapsed = end_time - start_time
    hours, rest = divmod(seconds_elapsed, 3600)
    minutes, seconds = divmod(rest, 60)

    logging.info("BTC bow tie analysis finished after {} hours {} minutes and {} seconds"
                 .format(hours, minutes, int(seconds)))
    return True

# directory = 'data/NET-btc-heur_0-week/201[0-1]*'
# output = 'results/bow_tie_output_new'
# main(directory,output)
# python bowtie_analysis.py "data/NET-btc-heur_0-week/201[0-1]*" -o "results/bow_tie_json_output"


if __name__ == "__main__":
    args = parser.parse_args()
    main(**vars(args))
