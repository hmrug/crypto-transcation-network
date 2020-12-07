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
from multiprocessing import Process
import multiprocessing

################### Logging settings #########################################


logging.basicConfig(filename="err.log",
                    level=logging.DEBUG, format='%(asctime)s :%(message)s')


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
               name + "_s": sum([G.nodes()[node]["is_sink"] for node in graph_nodes]),
               name + "_m": sum([G.nodes()[node]["is_miner"] for node in graph_nodes])}

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


def files_walker(files, json_output,directory):
    #files = glob.glob(directory)
    files.sort()
    for file in files:
        with open(directory + "/" + file, 'r', encoding='utf8', errors='ignore') as f:
            logging.info("Analysing data from {}".format(file[:-8]))
            G = nx.read_graphml(f)
            bowtie_dict = bowtie_analysis(G)

            try:
                with open(json_output, "r+") as fi:
                    data = json.load(fi)
                    new_entry = {file[5:-8]: bowtie_dict}
                    data.update(new_entry)
                    fi.seek(0)
                    json.dump(data, fi, indent=4)
                    logging.info("writing bow tie component from {} to {}".format(
                        file[5:-8], json_output))
                    logging.info("#" * 50)
            except OSError as e:
                logging.error(e)

    return True


#################### Parser settings #########################################
parser = argparse.ArgumentParser(description='Detect groups in a video')

parser.add_argument("directory", help='directory of the graph files')

parser.add_argument(
    "-o", "--output",
    help='name of the json output file',
    default="new.json")


def main(directory=None, output=None):

    if directory is None:
        return False

    nr_cores = multiprocessing.cpu_count()
    json_output = output

    if not os.path.isfile(json_output):
        with io.open(os.path.join(json_output), 'w') as db_file:
            db_file.write(json.dumps({}))

    core_dict = {}
    np_files = np.array(os.listdir(directory))
    chunk_lst = np.array_split(np_files, nr_cores)
    for i in range(nr_cores):
        process_name = f"p{i}"
        file_name = f"test{i}.json"
        core_dict[process_name] = Process(target=files_walker(list(chunk_lst[i]), file_name, directory))

        core_dict[process_name].start()
    
    logging.info("BTC bow tie analysis finished")
    return True


if __name__ == "__main__":
    logging.info("Start analysing BTC network")
    args = parser.parse_args()
    main(**vars(args))
