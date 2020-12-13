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


def degree_dist(G, degree_type=None):
    degs = {}
    for n in G.nodes():
        if degree_type == "in":
            deg = G.in_degree(n)
        elif degree_type == "out":
            deg = G.out_degree(n)
        else:
            deg = G.degree(n)
        if deg not in degs:
            degs[deg] = 0
        degs[deg] += 1
    G_y = [v/len(G.nodes()) for (k, v) in sorted(degs.items())]
    G_x = [i for i in range(len(G_y))]

    return G_x, G_y


def files_walker(files, output_dir):

    for file in files:
        logging.info("Analysing data from {}".format(file[-18:-8]))
        G = nx.read_graphml(file)
        degree_regular = degree_dist(G)
        in_degree = degree_dist(G, "in")
        out_degree = degree_dist(G, "out")

        try:
            with io.open(os.path.join(output_dir, file[-18:-8]+".json"), 'w') as json_file:
                final_dict = dict()
                final_dict.update({"regular": degree_regular})
                final_dict.update({"in": in_degree})
                final_dict.update({"out": out_degree})

                json_file.write(json.dumps(final_dict))

                logging.info(
                    "writing degree distributions from {}".format(file[-18:-8]))
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
    default="results/degreedist_json")


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
