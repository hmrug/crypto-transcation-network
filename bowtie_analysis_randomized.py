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

import warnings
warnings.filterwarnings("ignore")


def randomize(g):
    graph = g.copy()
    undirected_graph = graph.to_undirected()
    nswap = len(undirected_graph.edges())/2
    max_tries = 100*len(undirected_graph.edges())
    seed = np.random.seed()
    nx.algorithms.swap.double_edge_swap(
        undirected_graph, nswap=nswap, seed=seed, max_tries=max_tries)
    return undirected_graph.to_directed()


def get_further_stats(G):
    avg_clustering = nx.average_clustering(G)
    degree_assortavity = nx.degree_assortativity_coefficient(G)
    # create output dict
    result_dict = {}
    result_dict["clustering"] = avg_clustering
    result_dict["assortativity"] = degree_assortavity

    return result_dict


def bowtie_analysis(G):
    # reverse all direction of the graph
    GT = nx.reverse(G, copy=True)
    # calculate SSC
    scc = list(nx.strongly_connected_components(G))
    if len(scc) == 0:
        return{}

    SSC = max(scc, key=len)

    # take any node n from SSC and do a depth first search
    # through directed graph beginning from node n
    v_any = list(SSC)[0]
    DFS_G = set(nx.dfs_tree(G, v_any).nodes())
    DFS_GT = set(nx.dfs_tree(GT, v_any).nodes())
    OUT = DFS_G - SSC
    IN = DFS_GT - SSC
    V_rest = set(G.nodes()) - SSC - OUT - IN

    TUBES = set()
    INTENDRILS = set()
    OUTTENDRILS = set()
    OTHER = set()

    for v in V_rest:
        # irv => in reaches node v
        irv = len(IN & set(nx.dfs_tree(GT, v).nodes())) is not 0
        # vro => node v reaches out
        vro = len(OUT & set(nx.dfs_tree(G, v).nodes())) is not 0
        if irv and vro:
            TUBES.add(v)
        elif irv and not vro:
            INTENDRILS.add(v)
        elif not irv and vro:
            OUTTENDRILS.add(v)
        elif not irv and not vro:
            OTHER.add(v)

    FRINGE = set()
    DISCONNECTED = set()
    for o in OTHER:
        # orIT => node o reaches INTENDRILS
        orIT = len(INTENDRILS & set(nx.dfs_tree(G, o))) is not 0
        # OTro => OUTTERNDIRLS reaches node o
        OTro = len(OUTTENDRILS & set(nx.dfs_tree(GT, o))) is not 0
        if orIT or OTro:
            FRINGE.add(o)
        else:
            DISCONNECTED.add(o)

    TENDRILS = INTENDRILS.union(OUTTENDRILS)

    def component_result(name, graph_nodes):
        return{name: len(graph_nodes),
               }

    result_dict = dict()
    result_dict.update(component_result("nodes", G.nodes()))
    result_dict.update(component_result("ssc", SSC))
    result_dict.update(component_result("in", IN))
    result_dict.update(component_result("out", OUT))
    result_dict.update(component_result("tubes", TUBES))
    result_dict.update(component_result("tendrils", TENDRILS))
    result_dict.update(component_result("fringe", FRINGE))
    result_dict.update(component_result("disconnected", DISCONNECTED))

    return result_dict


def files_walker(files, output_dir):

    for file in files:
        logging.info("Analysing data from {}".format(file[-18:-8]))
        G = nx.read_graphml(file)
        G_random = randomize(G.copy())
        bowtie_dict = bowtie_analysis(G)
        stats_dict = get_further_stats(G)
        bowtie_dict_random = bowtie_analysis(G_random)
        stats_dict_random = get_further_stats(G_random)

        ############## create dict for json ##################

        final_dict = {}
        final_dict["bowtie"] = bowtie_dict
        final_dict["stats"] = stats_dict
        final_dict["bowtie_random"] = bowtie_dict_random
        final_dict["stats_random"] = stats_dict_random

        ######################################################

        try:
            with io.open(os.path.join(output_dir, file[-18:-8]+"_randomized.json"), 'w') as json_file:
                json_file.write(json.dumps(final_dict))
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

    logging.basicConfig(filename=os.path.join(
        output, "logfile.log"), level=logging.DEBUG, format='%(asctime)s :%(message)s')

    logging.info("Start analysing BTC network")
    logging.info('Start Analysing bow tie structure in {}'.format(directory))

    nr_cores = multiprocessing.cpu_count()
    logging.info(
        'This machine has {} cores which can be used'.format(nr_cores))

    files = glob.glob(directory)
    random.shuffle(files)

    nr_processes = min(len(files), nr_cores)
    logging.info('Run {} jobs'.format(nr_processes))

    bins = np.array_split(files, nr_processes)

    jobs = list()

    for i in range(nr_processes):
        #process_name = f"Process_{i}"
        jobs.append(Process(target=files_walker, args=(list(bins[i]), output)))

    for i, process in enumerate(jobs):
        process.start()
        logging.info("started process_{}".format(i+1))

    for process in jobs:
        process.join()

    end_time = time()
    seconds_elapsed = end_time - start_time
    hours, rest = divmod(seconds_elapsed, 3600)
    minutes, seconds = divmod(rest, 60)

    logging.info("BTC bow tie analysis finished after {} hours {} minutes and {} seconds".format(
        hours, minutes, int(seconds)))
    return True

# directory = 'data/NET-btc-heur_0-week/201[0-1]*'
# output = 'results/bow_tie_output_new'
# main(directory,output)
# python bowtie_analysis.py "data/NET-btc-heur_0-week/201[0-1]*" -o "results/bow_tie_json_output"


if __name__ == "__main__":
    args = parser.parse_args()
    main(**vars(args))
