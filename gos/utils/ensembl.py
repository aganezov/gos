# -*- coding: utf-8 -*-

import os
from networkx import Graph, networkx

GENE_ORDER_FILES = [
    "/Users/aganezov/Dropbox/data/cat/felCat6.2_gene_order.txt",
    "/Users/aganezov/Dropbox/data/chimpanzee/panTro2.1.4_gene_order.txt",
    "/Users/aganezov/Dropbox/data/dog/canFam3.1_gene_order.txt",
    "/Users/aganezov/Dropbox/data/human/hg38_gene_order.txt",
    "/Users/aganezov/Dropbox/data/mouse/mm38_gene_order.txt",
    "/Users/aganezov/Dropbox/data/opossum/monDom5_gene_order.txt",
    "/Users/aganezov/Dropbox/data/rat/rn6.0_gene_order.txt"
]

PARALOGOUS_FILES = [
    "/Users/aganezov/Dropbox/data/cat/felCat6.2_paralogs.txt",
    "/Users/aganezov/Dropbox/data/chimpanzee/panTor2.1.4_paralogs.txt",
    "/Users/aganezov/Dropbox/data/dog/canFam3.1_paralogs.txt",
    "/Users/aganezov/Dropbox/data/human/hg38_paralogs.txt",
    "/Users/aganezov/Dropbox/data/mouse/mm38_paralogs.txt",
    "/Users/aganezov/Dropbox/data/opossum/monDom5_paralogs.txt",
    "/Users/aganezov/Dropbox/data/rat/rn6.0_paralogs.txt"
]

HOMOLOGOUS_FILE = []

for dir_name in ["/Users/aganezov/Dropbox/data/cat/", "/Users/aganezov/Dropbox/data/dog/",
                 "/Users/aganezov/Dropbox/data/chimpanzee/", "/Users/aganezov/Dropbox/data/human/",
                 "/Users/aganezov/Dropbox/data/mouse/", "/Users/aganezov/Dropbox/data/opossum/",
                 "/Users/aganezov/Dropbox/data/rat/"]:
    HOMOLOGOUS_FILE.extend(
        [os.path.join(dir_name, file_name) for file_name in os.listdir(dir_name) if file_name.endswith("homologous.txt")])


def create_closure_gene_map(gene_order_files=GENE_ORDER_FILES, paralogous_files=PARALOGOUS_FILES, homologous_files=HOMOLOGOUS_FILE):
    global dir_name
    graph = Graph()
    for file_name in gene_order_files:
        with open(file_name, "rt") as source:
            for line in source:
                if line.strip().startswith("Ensembl"):
                    continue
                gene, *rest = line.strip().split()
                graph.add_node(gene)
    for file_name in paralogous_files + homologous_files:
        print("processing", file_name)
        with open(file_name, "rt") as source:
            for line in source:
                if line.strip().startswith("Ensembl"):
                    continue
                gene_1, gene_2 = line.strip().split()
                graph.add_edge(gene_1, gene_2)
    homologous_map = {}
    for number, cc in enumerate(networkx.connected_component_subgraphs(graph)):
        for vertex in cc:
            homologous_map[vertex] = number
    for file_name in gene_order_files:
        dir_name = os.path.dirname(file_name)
        basename = os.path.basename(file_name)
        new_file_name = "".join([basename.replace(".txt", ""), "_grimm-map.txt"])
        with open(os.path.join(dir_name, new_file_name), "wt") as destination:
            with open(file_name, "rt") as source:
                for line in source:
                    if line.strip().startswith("Ensembl"):
                        continue
                    gene, *rest = line.strip().split()
                    print(gene, homologous_map[gene], file=destination)


if __name__ == "__main__":
    create_closure_gene_map(gene_order_files=GENE_ORDER_FILES,
                            paralogous_files=PARALOGOUS_FILES,
                            homologous_files=HOMOLOGOUS_FILE)
