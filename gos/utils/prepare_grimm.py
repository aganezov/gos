# -*- coding: utf-8 -*-
from collections import defaultdict
import os
from gos.utils.prepare_grimm_with_repeats import read_gene_order_data, read_gene_to_int_map, Gene

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"

def write_grimm_file(gene_order_file, gene_mapping_file, output_file=None, genome_name=None):
    genome = read_gene_order_data(gene_order_file)
    mapping = read_gene_to_int_map(gene_mapping_file)
    if output_file is None:
        output_dir = os.path.join(os.path.dirname(gene_order_file), "7_genomes_exp")
        basename = os.path.basename(gene_order_file)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, basename.replace(".txt", ".grimm"))
    for chromosome in genome.keys():
            genome[chromosome].sort(key=lambda entry: (entry.start_coordinate + entry.end_coordinate) / 2)
    with open(output_file, "wt") as destination:
        print(">", genome_name, file=destination)
        for fragment, gene_order in genome.items():
            for entry in gene_order:
                if isinstance(entry, Gene):
                    string_value = mapping[entry.name]
                else:
                    string_value = entry.name + "__repeat"
                print("-" if entry.strand == -1 else "", string_value, sep="", end=" ", file=destination)
            print("$", file=destination)

if __name__ == "__main__":
    write_grimm_file(gene_order_file="/Users/aganezov/Dropbox/data/opossum/monDom5_gene_order.txt",
                     gene_mapping_file="/Users/aganezov/Dropbox/data/7_experiment/monDom5_gene_order_grimm-map.txt",
                     genome_name="rat")
