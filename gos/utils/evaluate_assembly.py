# -*- coding: utf-8 -*-
import os

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"


def get_history_as_vertices_pairs(history_file):
    result = []
    with open(history_file, "rt") as source:
        for line in source:
            gene_1, gene_2 = line.split()
            vertex_1 = (gene_1[1:] + "t") if gene_1.startswith("-") else (gene_1 + "h")
            vertex_2 = (gene_2[1:] + "h") if gene_2.startswith("-") else (gene_2 + "t")
            result.append((vertex_1, vertex_2))
            result.append((vertex_2, vertex_1))
    return result


def get_assembly_results(results_file):
    result = []
    with open(results_file, "rt") as source:
        for line in source:
            split_data = line.split()
            vertex_1, vertex_2 = split_data[0], split_data[1]
            repeat = split_data[3]
            score = split_data[4]
            result.append((vertex_1, vertex_2, repeat, score))
    return result

if __name__ == "__main__":
    history_files = [
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/opossum_95_400.fh",
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/opossum_95_800.fh",
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/opossum_95_1200.fh",
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/opossum_95_1600.fh",
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/opossum_95_2000.fh"
    ]
    result_files = [
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/output/7_opossum_95_400.txt",
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/output/7_opossum_95_800.txt",
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/output/7_opossum_95_1200.txt",
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/output/7_opossum_95_1600.txt",
        "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment/output/7_opossum_95_2000.txt"
    ]

    for history_file, result_file in zip(history_files, result_files):
        history = get_history_as_vertices_pairs(history_file)
        result = get_assembly_results(result_file)
        # print("Got", len(result), "possible assemblies")
        # print("Got", len(history) / 2, "real breakages")
        true_assemblies = 0
        for vertex_1, vertex_2, repeat, score in result:
            if (vertex_1, vertex_2) in history or (vertex_2, vertex_1) in history:
                true_assemblies += 1

        print("Experiment", os.path.basename(history_file).replace(".fh", ""))
        print("Got", true_assemblies, "correct assemblies out of", len(history) // 2, "and", len(result) - true_assemblies, "incorrect assemblies")
