#!/usr/bin/env python3
from concurrent import futures
from csv import writer
import networkx as nx
import random
import sys
import time

def serial_test(graphs):
    for g in graphs:
        iterate_cliques(g)

def parallel_test(graphs, max_workers):
    with futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        executor.map(iterate_cliques, graphs)

def iterate_cliques(g):
    for _ in nx.find_cliques(g):
        pass

if __name__ == '__main__':
    out = writer(sys.stdout)
    out.writerow(['num graphs', 'serial time', 'parallel time'])

    n = 100
    graphs = [nx.dense_gnm_random_graph(n, n*n) for _ in range(500)]

    # Run with a number of different randomly generated graphs
    for num_graphs in range(50, 1001, 50):
        sample = random.choices(graphs, k = num_graphs)

        start = time.time()
        serial_test(sample)
        serial_time = time.time() - start

        start = time.time()
        parallel_test(sample, 16)
        parallel_time = time.time() - start

        out.writerow([num_graphs, serial_time, parallel_time])
