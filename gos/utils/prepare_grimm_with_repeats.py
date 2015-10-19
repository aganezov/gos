# -*- coding: utf-8 -*-
from collections import defaultdict
import os


class Repeat(object):
    def __init__(self, name, start_coordinate, end_coordinate, strand, chromosome):
        self.name = name
        self.start_coordinate = start_coordinate
        self.end_coordinate = end_coordinate
        self.strand = strand
        self.chromosome = chromosome


class Gene(object):
    def __init__(self, name, start_coordinate, end_coordinate, strand, chromosome):
        self.name = name
        self.start_coordinate = start_coordinate
        self.end_coordinate = end_coordinate
        self.strand = strand
        self.chromosome = chromosome

    def __str__(self):
        return ("-" if self.strand == -1 else "") + self.name


def read_repeat_data(file_name, case):
    result = defaultdict(list)
    with open(file_name, "rt") as source:
        for line in source:
            if len(line.strip()) == 0:
                continue
            split_data = line.strip().split()
            if split_data[0].lower().startswith("sw"):
                continue
            if split_data[0].lower().startswith("score"):
                continue

            name = split_data[9]
            start_coordinate, end_coordinate = int(split_data[5]), int(split_data[6])
            strand = -1 if split_data[8] == "C" else 1
            chromosome = chromosome_name_substitution(split_data[4], case=case)
            result[chromosome].append(Repeat(name=name, start_coordinate=start_coordinate, end_coordinate=end_coordinate,
                                             chromosome=chromosome, strand=strand))
    return result


def read_gene_order_data(file_name):
    result = defaultdict(list)
    with open(file_name, "rt") as source:
        for line in source:
            if len(line.strip()) == 0:
                continue
            if line.strip().lower().startswith("ensembl"):
                continue

            split_data = line.strip().split()
            name, chromosome = split_data[0], split_data[1]
            start_coordinate, end_coordinate, strand = int(split_data[2]), int(split_data[3]), int(split_data[4])
            result[chromosome].append(Gene(name=name, chromosome=chromosome, start_coordinate=start_coordinate, end_coordinate=end_coordinate, strand=strand))

    return result


def chromosome_name_substitution(repeat_chromosome_name, case):
    if case == "opossum":
        return repeat_chromosome_name.replace("chr", "")
    elif case == "dog":
        pass
    elif case == "cat":
        pass
    elif case == "chimpanzee":
        pass


def read_gene_to_int_map(*file_names):
    result = {}
    for file_name in file_names:
        with open(file_name, "rt") as source:
            for line in source:
                split_data = line.strip().split()
                gene, map_value = split_data[0], int(split_data[1])
                result[gene] = map_value
    return result


def has_genes(scaffold):
    return any(map(lambda entry: isinstance(entry, Gene), scaffold))


def filter_genome_and_get_fragmentation_history(fragmented_genome):
    true_fragmentation_history = []
    for fragment_1, fragment_2 in zip(fragmented_genome[:-1], fragmented_genome[1:]):
        if not has_genes(fragment_1) or not has_genes(fragment_2):
            continue
        right_most_gene = fragment_1[-2]
        left_most_gene = fragment_2[1]
        true_fragmentation_history.append((right_most_gene, left_most_gene))
    filtered_genome = list(filter(lambda fragment: has_genes(fragment), fragmented_genome))
    return filtered_genome, true_fragmentation_history


if __name__ == "__main__":
    genome_name = "opossum"
    repeat_file_names = ["/Users/aganezov/Dropbox/data/opossum/filtered_repeats/95_400.txt",
                         "/Users/aganezov/Dropbox/data/opossum/filtered_repeats/95_800.txt",
                         "/Users/aganezov/Dropbox/data/opossum/filtered_repeats/95_1200.txt",
                         "/Users/aganezov/Dropbox/data/opossum/filtered_repeats/95_1600.txt",
                         "/Users/aganezov/Dropbox/data/opossum/filtered_repeats/95_2000.txt"]
    gene_order_file_name = "/Users/aganezov/Dropbox/data/opossum/monDom5_gene_order.txt"
    gene_order_map_files = ["/Users/aganezov/Dropbox/data/7_experiment/monDom5_gene_order_grimm-map.txt",
                            "/Users/aganezov/Dropbox/data/7_experiment/rn6.0_gene_order_grimm-map.txt",
                            "/Users/aganezov/Dropbox/data/7_experiment/mm38_gene_order_grimm-map.txt",
                            "/Users/aganezov/Dropbox/data/7_experiment/hg38_gene_order_grimm-map.txt",
                            "/Users/aganezov/Dropbox/data/7_experiment/canFam3.1_gene_order_grimm-map.txt",
                            "/Users/aganezov/Dropbox/data/7_experiment/panTro2.1.4_gene_order_grimm-map.txt",
                            "/Users/aganezov/Dropbox/data/7_experiment/felCat6.2_gene_order_grimm-map.txt"]
    dir_name = "/Users/aganezov/Dropbox/data/7_experiment/opossum_experiment"
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    for repeat_file_name in repeat_file_names:
        repeats = read_repeat_data(file_name=repeat_file_name, case="opossum")
        gene_order = read_gene_order_data(file_name=gene_order_file_name)
        try:
            gene_mapping = read_gene_to_int_map(*gene_order_map_files)
        except IOError as err:
            gene_mapping = None

        combined_genome = {chromosome: chr_gene_order + repeats[chromosome] for chromosome, chr_gene_order in gene_order.items()}
        for chromosome in combined_genome.keys():
            combined_genome[chromosome].sort(key=lambda entry: (entry.start_coordinate + entry.end_coordinate) / 2)

        current_fragment = []
        fragmented_genome = [current_fragment, ]
        for chromosome, order in sorted(combined_genome.items()):
            for entry in order:
                if isinstance(entry, Repeat):
                    current_fragment.append(entry)
                    current_fragment = []
                    fragmented_genome.append(current_fragment)
                    current_fragment.append(entry)
                    continue
                else:
                    current_fragment.append(entry)
        filtered_fragmented_genome, fragmentation_history = filter_genome_and_get_fragmentation_history(fragmented_genome)
        print(len(filtered_fragmented_genome))
        output_grimm_file_name = os.path.join(dir_name, genome_name + "_" + os.path.basename(repeat_file_name).replace(".txt", "") + ".grimm")
        with open(output_grimm_file_name, "wt") as destination:
            print(">", genome_name, file=destination)
            for fragment in filtered_fragmented_genome:
                for entry in fragment:
                    if isinstance(entry, Gene):
                        if gene_mapping is not None:
                            string_value = gene_mapping[entry.name]
                        else:
                            string_value = entry.name
                    else:
                        string_value = entry.name + "__repeat"
                    print("-" if entry.strand == -1 else "", string_value, sep="", end=" ", file=destination)
                print("$", file=destination)
        output_fragmentation_history_file_name = os.path.join(dir_name, genome_name + "_" + os.path.basename(repeat_file_name).replace(".txt", "") + ".fh")
        with open(output_fragmentation_history_file_name, "wt") as destination:
            for extremity1, extremity2 in fragmentation_history:
                value1 = ("-" if extremity1.strand == -1 else "") + str(gene_mapping[extremity1.name])
                value2 = ("-" if extremity2.strand == -1 else "") + str(gene_mapping[extremity2.name])
                print(value1, value2, file=destination)


