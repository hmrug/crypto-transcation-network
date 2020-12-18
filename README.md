# Temporal Bow-Tie Component Analysis of the Bitcoin Network

## Bow-tie analysis

The analsysis was done on the btc user graphs stored at /mnt/hdd_data/btc on the server consensus.business.uzh.ch

The results of the bow tie analysis were put into the folder /mnt/hdd_data/btc/results

The bow tie analysis can be run over arbitrary graphs with the script bowie_analysis.py

The script takes as input the files of the btc graphs and the path where the outputs should get dumped

It creates an output folder at the set location and writes the result json files with the bow tie 
components as keys and the nodes as values into that folder for all the given graphs together with a logfile

Example to run the script on the daily snapshots from 2012-2015 see below:
```
python3 bowtie_analysis.py "/mnt/hdd_data/btc/NET-btc530k-heur_1-day/201[2-5]*" -o "/mnt/hdd_data/btc/results/btc530k_day_2012-2015" 
```

On the resulting json files that got created with the previous script you can then run the memory-less markov chain analysis like follows
and set the output directory for the transition matrices json files with t-o see example:

```
python3 markov.py "/mnt/hdd_data/btc/results/btc530k_day_2012-2015/2*" -o "/home/jleupp/jleupp/results"
```

Since the resulting json files from the bow tie analysis contain the ID's of all nodes and including their attributes (is_miner and is_sink)
you can run the script bellow to create one json file with the timestamp of the snapshot as keys and a dictionary of the bowtie components and only their count of nodes
as values see example:
```
python3 bowtie_analysis.py "/mnt/hdd_data/btc/NET-btc530k-heur_1-day/201[2-5]*" -o "/mnt/hdd_data/btc/results/btc530k_day_2012-2015" 
```

With the same logic you can run the script markov_statistics to combine all the transition matrices in one big json file

The two final json with the results from the bow-tie analysis and the markov chain is found in the folder:

/crypto-transcation-network/tree/master/results/NET-btc530k-heur_1-day

## Visualisation

All the results are visualized in the jupiter notebook which can be found here:

https://github.com/lutharsanen/crypto-transcation-network/blob/master/BowTie-Bitcoin%20Visualization.ipynb

Since it is interactive in order to run it you have to pull the repository and run all cells. All the needed files are in the result folder. 
Make sure to have the newest version of pandas and plotly installed otherwise it will not work.



