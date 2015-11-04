#! /usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from copy import deepcopy
from bg import Multicolor, KBreak, BreakpointGraph, GRIMMReader, NewickReader, BGGenome
import itertools
from bg.vertices import TaggedInfinityVertex, TaggedBlockVertex
import networkx as nx
import os

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"

################################################################################################################
#
# START OF supporting functions that implement some functionality, that BreakpointGraph class lacks in the bg package
#
################################################################################################################

def get_vertex_surrounding_multicolor(graph, vertex):
    """
    Loops over all edges that are incident to supplied vertex and accumulates all colors,
     that are present in those edges
    """
    result = Multicolor()
    for edge in graph.get_edges_by_vertex(vertex):
        result += edge.multicolor
    return result


def get_irregular_edge_by_vertex(graph, vertex):
    """
    Loops over all edges that are incident to supplied vertex and return a first irregular edge
        in "no repeat" scenario such irregular edge can be only one for any given supplied vertex
    """
    for edge in graph.get_edges_by_vertex(vertex):
        if edge.is_irregular_edge:
            return edge
    return None  # not return in current implementation, added for code consistency


def get_irregular_vertex(bgedge):
    """
    This method is called only in irregular edges in current implementation, thus at least one edge will be irregular
    """
    return bgedge.vertex1 if bgedge.vertex1.is_irregular_vertex else bgedge.vertex2


def supports_a_pair_of_irregular_edges(graph, edge):
    v1 = edge.vertex1
    v2 = edge.vertex2
    return get_irregular_edge_by_vertex(graph, v1) is not None and get_irregular_edge_by_vertex(graph, v2) is not None


def get_full_irregular_multicolor(graph, vertex):
    result = Multicolor()
    for edge in graph.get_edges_by_vertex(vertex):
        if edge.is_irregular_edge:
            result += edge.multicolor
    return result


################################################################################################################
#
# END OF supporting functions that implement some functionality, that BreakpointGraph class lacks in the bg package
#
################################################################################################################


################################################################################################################
#
# START OF main scaffolding algorithm functions
#
################################################################################################################

def get_irregular_subnets(cc, target_multicolor, exclude):
    h_support = defaultdict(set)
    t_support = defaultdict(set)

    to_remove_edges = []
    to_remove_vertices = []

    for bgedge, key in cc.edges(keys=True):
        if bgedge.is_irregular_edge:
            if bgedge.is_repeat_edge:
                if not target_multicolor <= bgedge.multicolor:
                    to_remove_edges.append((bgedge, key))
                    continue
                if any(map(lambda color: bgedge.multicolor.multicolors[color] > 1, target_multicolor.colors)):
                    to_remove_edges.append((bgedge, key))
                    continue
                repeat = [value for tag, value in get_irregular_vertex(bgedge).tags if tag == "repeat"][0]
                repeat_name, repeat_dir = repeat[:-1], repeat[-1]
                if repeat_dir == "h":
                    h_support[bgedge.vertex1 if bgedge.vertex1.is_regular_vertex else bgedge.vertex2].add(repeat_name)
                elif repeat_dir == "t":
                    t_support[bgedge.vertex1 if bgedge.vertex1.is_regular_vertex else bgedge.vertex2].add(repeat_name)
            elif any(map(lambda color: color in bgedge.multicolor.colors, exclude)):
                to_remove_vertices.append(bgedge.vertex1 if bgedge.vertex1.is_regular_vertex else bgedge.vertex2)
                continue

    for bgedge, key in to_remove_edges:
        cc.delete_bgedge(bgedge, key)
    for vertex in to_remove_vertices:
        if vertex in h_support:
            del h_support[vertex]
        if vertex in t_support:
            del t_support[vertex]
        edges = list(cc.get_edges_by_vertex(vertex, keys=True))
        for bgedge, key in edges:
            cc.delete_bgedge(bgedge, key)

    to_remove_edges = []
    possible_assemblies = defaultdict(list)
    repeats = set()
    for bgedge, key in cc.edges(keys=True):
        if not bgedge.is_irregular_edge:
            v1, v2 = bgedge.vertex1, bgedge.vertex2
            flag = True
            if v1 in h_support and v2 in t_support:
                intersection = h_support[v1].intersection(t_support[v2])
                if len(intersection) > 0:
                    flag = False
                    for repeat_name in intersection:
                        possible_assemblies[(v1, v2)].append(repeat_name)
                        repeats.add(repeat_name)
            if v1 in t_support and v2 in h_support:
                intersection = t_support[v1].intersection(h_support[v2])
                if len(intersection) > 0:
                    flag = False
                    for repeat_name in intersection:
                        repeats.add(repeat_name)
                        possible_assemblies[(v2, v1)].append(repeat_name)
            if flag:
                to_remove_edges.append((bgedge, key))

    for bgedge, key in to_remove_edges:
        cc.delete_bgedge(bgedge, key)

    subnets = []
    for cc in cc.connected_components_subgraphs(copy=False):
        if len(list(cc.edges())) > 0:
            subnets.append(cc)
    return subnets, possible_assemblies, h_support, t_support, repeats


def get_assembly_score(graph, v1, v2, target_multicolor, tree, multicolors_scores, surroundings, full_irregular_multicolors):
    if surroundings is None:
        surroundings = {}
    if multicolors_scores is None:
        multicolors_scores = {}
    if full_irregular_multicolors is None:
        full_irregular_multicolors = {}

    full_multicolor = Multicolor(*max(tree.consistent_multicolors, key=lambda multicolor: len(list(multicolor.multicolors.elements()))).colors)
    guidance = tree.consistent_multicolors

    if v1 not in surroundings:
        surroundings[v1] = Multicolor(*get_vertex_surrounding_multicolor(graph, v1).colors)
    surrounding1 = surroundings[v1]
    if v1 not in full_irregular_multicolors:
        full_irregular_multicolors[v1] = Multicolor(*get_full_irregular_multicolor(graph, v1).colors)
    im1 = full_irregular_multicolors[v1]
    if v2 not in surroundings:
        surroundings[v2] = Multicolor(*get_vertex_surrounding_multicolor(graph, v2).colors)
    surrounding2 = surroundings[v2]
    if v2 not in full_irregular_multicolors:
        full_irregular_multicolors[v2] = Multicolor(*get_full_irregular_multicolor(graph, v2).colors)
    im2 = full_irregular_multicolors[v1]

    c_1_multicolor = full_multicolor - surrounding1
    c_2_multicolor = full_multicolor - surrounding2

    c = c_1_multicolor.intersect(c_2_multicolor)

    c_a = c_1_multicolor - c
    c_b = c_2_multicolor - c
    sedge = graph.get_edge_by_two_vertices(v1, v2)
    smulticolor = Multicolor(*sedge.multicolor.colors) if sedge is not None else Multicolor()
    if target_multicolor <= smulticolor:
        smulticolor -= target_multicolor

    if (im1 + c_a).hashable_representation not in multicolors_scores:
        multicolors_scores[(im1 + c_a).hashable_representation] = len(Multicolor.split_colors(im1 + c_a, guidance=guidance,
                                                                                              account_for_color_multiplicity_in_guidance=False))
    if (im2 + c_b).hashable_representation not in multicolors_scores:
        multicolors_scores[(im2 + c_b).hashable_representation] = len(Multicolor.split_colors(im2 + c_b, guidance=guidance,
                                                                                              account_for_color_multiplicity_in_guidance=False))
    if (smulticolor + c).hashable_representation not in multicolors_scores:
        multicolors_scores[(smulticolor + c).hashable_representation] = len(
            Multicolor.split_colors(smulticolor + c, guidance=guidance,
                                    account_for_color_multiplicity_in_guidance=False))
    ie1_score = multicolors_scores[(im1 + c_a).hashable_representation]
    ie2_score = multicolors_scores[(im2 + c_b).hashable_representation]
    se_score = multicolors_scores[(smulticolor + c).hashable_representation]
    before = ie1_score + ie2_score + se_score

    if (im1 - target_multicolor + c_a).hashable_representation not in multicolors_scores:
        multicolors_scores[(im1 - target_multicolor + c_a).hashable_representation] = len(
            Multicolor.split_colors(im1 - target_multicolor + c_a, guidance=guidance,
                                    account_for_color_multiplicity_in_guidance=False))
    if (im2 - target_multicolor + c_b).hashable_representation not in multicolors_scores:
        multicolors_scores[(im2 - target_multicolor + c_b).hashable_representation] = len(
            Multicolor.split_colors(im2 - target_multicolor + c_b, guidance=guidance,
                                    account_for_color_multiplicity_in_guidance=False))
    if (smulticolor + target_multicolor + c).hashable_representation not in multicolors_scores:
        multicolors_scores[(smulticolor + target_multicolor + c).hashable_representation] = len(
            Multicolor.split_colors(smulticolor + target_multicolor + c, guidance=guidance,
                                    account_for_color_multiplicity_in_guidance=False))
    new_ie1_score = multicolors_scores[(im1 - target_multicolor + c_a).hashable_representation]
    new_ie2_score = multicolors_scores[(im2 - target_multicolor + c_b).hashable_representation]
    new_se_score = multicolors_scores[(smulticolor + target_multicolor + c).hashable_representation]

    after = new_ie1_score + new_ie2_score + new_se_score
    return before, after

def identify_assembly_points(graph, bgtree, target_multicolor, exclude=None, verbose=False, verbose_destination=None):
    """
    The main granular assembling function, that IDENTIFIES assembly points, but does not perform the assembly on its own
    It DOES NOT change the supplied breakpoint graph in any way!!!
    """
    if verbose:
        print(">>Identifying assemblies for target multicolor:",
              [e.name for e in target_multicolor.multicolors.elements()], file=verbose_destination)
    guidance = bgtree.consistent_multicolors[:]
    offset = len(Multicolor.split_colors(target_multicolor, guidance=guidance,
                                         account_for_color_multiplicity_in_guidance=False)) - 1
    assemblies = []  # the overall result
    if exclude is None:
        exclude = []  # a container with single colors of genomes, that are to be considered fully assembled
    multicolor_scores = {}
    surroundings = {}
    full_irregular_multicolors = {}
    for i, cc in enumerate(graph.connected_components_subgraphs(copy=True)):
        subnets, possible_assemblies, h_support, t_support, repeats = get_irregular_subnets(cc, target_multicolor, exclude)
        for subnet in subnets:
            vertices = [vertex for vertex in subnet.nodes() if not vertex.is_irregular_vertex]
            repeats_h = {repeat for vertex in vertices for repeat in h_support[vertex]}
            repeats_t = {repeat for vertex in vertices for repeat in t_support[vertex]}
            repeats = repeats_h.intersection(repeats_t)
            for repeat in repeats:
                g = nx.Graph()
                for edge in filter(lambda edge: not edge.is_irregular_edge, subnet.edges()):
                    v1, v2 = sorted((edge.vertex1, edge.vertex2), key=lambda vertex: vertex.name)
                    if v1 in h_support and repeat in h_support[v1] and v2 in t_support and repeat in t_support[v2]:
                        before, after = get_assembly_score(graph, v1, v2, target_multicolor, bgtree,
                                                           multicolor_scores, surroundings, full_irregular_multicolors)
                        if before - after - offset > 1:
                            g.add_edge((v1, "h"), (v2, "t"), weight=before - after - offset)
                    if v1 in t_support and repeat in t_support[v1] and v2 in h_support and repeat in h_support[v2]:
                        before, after = get_assembly_score(graph, v1, v2, target_multicolor, bgtree,
                                                           multicolor_scores, surroundings, full_irregular_multicolors)
                        if before - after - offset > 1:
                            g.add_edge((v1, "t"), (v2, "h"), weight=before - after - offset)
                edges = g.edges(data=True)
                if len(edges) == 0:
                    continue
                new_edges = []
                for edge in edges:
                    first, second = edge[0], edge[1]
                    v1, v2 = sorted((first, second), key=lambda item: item[0].name)
                    new_edges.append((v1, v2, edge[2]))
                edges = sorted(new_edges, reverse=True, key=lambda e: (e[2]["weight"], e[0][0].name, e[0][1], e[1][0].name, e[0][1]))
                visited = set()
                for v1, v2, data in edges:
                    weight = data["weight"]
                    if v1 not in visited and v2 not in visited:
                        visited.add(v1)
                        visited.add(v2)
                        v1, dir1 = v1
                        v2, dir2 = v2
                        assert (dir1 == "h" and dir2 == "t") or (dir1 == "t" and dir2 == "h")
                        if dir1 == "h":
                            assemblies.append((v2, v1, weight, repeat))
                        else:
                            assemblies.append((v1, v2, weight, repeat))
    return assemblies


def assemble_points(graph, assemblies, multicolor):
    for assembly in assemblies:
        v1, v2, weight, repeat_name = assembly
        iv1 = TaggedInfinityVertex(v1.name)
        iv1.add_tag("repeat", repeat_name + "t")
        iv2 = TaggedInfinityVertex(v2.name)
        iv2.add_tag("repeat", repeat_name + "h")
        kbreak = KBreak(start_edges=[(v1, iv1), (v2, iv2)],
                        result_edges=[(v1, v2), (iv1, iv2)],
                        multicolor=multicolor)
        graph.apply_kbreak(kbreak=kbreak, merge=True)


def assemble_scaffolds(graph, bgtree, target_organisms, exclude=None, verbose=False, verbose_destination=None):
    overall_assembling_result = []

    # all genomes stacked up together
    overall_target_multicolor = Multicolor(*target_organisms)

    # all of them combined might not be a tree consistent set, so we separate it into smallest number
    #   of tree consistent chunks
    tree_consistent_target_multicolors = Multicolor.split_colors(overall_target_multicolor,
                                                                 guidance=bgtree.consistent_multicolors,
                                                                 account_for_color_multiplicity_in_guidance=False)
    if verbose:
        print("Supplied set of targeted for scaffolding genomes has been split into",
              len(tree_consistent_target_multicolors), "T-consistent sets:", file=verbose_destination)
        for multicolor in tree_consistent_target_multicolors:
            print("\t", [color.name for color in multicolor.multicolors.elements()], file=verbose_destination)
        print("Expanding target multicolors to include all T-consistent subcolors")

    # now we need to expand that list into a larger list to include every possible tree consistent sub-color,
    #   of whatever is already in the list
    #
    # we will change it as we go, so better iterate over a copy
    for target_multicolor in tree_consistent_target_multicolors[:]:
        for tree_c_multicolor in deepcopy(bgtree.consistent_multicolors):
            if tree_c_multicolor <= target_multicolor\
                    and tree_c_multicolor not in tree_consistent_target_multicolors\
                    and len(tree_c_multicolor.colors) > 0:
                tree_consistent_target_multicolors.append(tree_c_multicolor)

    tree_consistent_target_multicolors = sorted(tree_consistent_target_multicolors,
                                                key=lambda mc: len(mc.hashable_representation),
                                                reverse=True)

    all_target_multicolors = tree_consistent_target_multicolors[:]
    for i in range(2, len(tree_consistent_target_multicolors) + 1):
        for comb in itertools.combinations(tree_consistent_target_multicolors[:], i):
            comb = list(comb)
            for mc1, mc2 in itertools.combinations(comb, 2):
                if len(mc1.intersect(mc2).colors) > 0:
                    break
            else:
                new_mc = Multicolor()
                for mc in comb:
                    new_mc += mc
                all_target_multicolors.append(new_mc)
    hashed_vertex_tree_consistent_multicolors = {mc.hashable_representation for mc in all_target_multicolors}
    all_target_multicolors = [Multicolor(*hashed_multicolor) for hashed_multicolor in
                                       hashed_vertex_tree_consistent_multicolors]
    all_target_multicolors = sorted(all_target_multicolors,
                                                key=lambda mc: len(mc.hashable_representation),
                                                reverse=True)
    if verbose:
        print("Determined full list of targeted for scaffolding multicolors of length",
              len(tree_consistent_target_multicolors), file=verbose_destination)
        for multicolor in all_target_multicolors:
            print("\t", [color.name for color in multicolor.multicolors.elements()], file=verbose_destination)

    for multicolor in all_target_multicolors:
        assembly_points = identify_assembly_points(graph, bgtree, target_multicolor=multicolor, exclude=exclude,
                                                   verbose_destination=verbose_destination)
        for v1, v2, weight, repeat_name in assembly_points:
            overall_assembling_result.append((v1, v2, weight, repeat_name, multicolor))
        assemble_points(graph, assemblies=assembly_points, multicolor=multicolor)
    return overall_assembling_result

################################################################################################################
#
# END OF main scaffolding algorithm functions
#
################################################################################################################

################################################################################################################
#
# START OF experiment set up (data)
#
################################################################################################################

GRIMM_FILES = ["./all.grimm"]
NEWICK_STRING_TREE = "(((human, chimp), gorilla), orangutan);"
TARGET_ORGANISM_NAMES = ["chimp"]
COMPLETE_ORGANISM_NAMES = ["human", "gorilla", "orangutan"]

################################################################################################################
#
# END OF experiment set up (data)
#
################################################################################################################

if __name__ == "__main__":
    print("Reading data into breakpoint graph...")
    graph = BreakpointGraph()
    for file in GRIMM_FILES:
        with open(file, "rt") as source:
            graph.update(GRIMMReader.get_breakpoint_graph(source), merge_edges=True)

    print("Getting a tree...")
    bgtree = NewickReader.from_string(NEWICK_STRING_TREE)

    print("Preparing organisms for assembling...")
    target_organisms = [BGGenome(organism) for organism in TARGET_ORGANISM_NAMES]
    exclude = [BGGenome(organism) for organism in COMPLETE_ORGANISM_NAMES]

    print("Staring the assembly process...")
    result = assemble_scaffolds(graph=graph, bgtree=bgtree, target_organisms=target_organisms, exclude=exclude,
                                verbose=True)
    print("Finished assembling!")
    print("Were identified",
          sum([len(multicolor.colors) for v1, v2, weight, repeat_name, multicolor in result]),
          "assembly points")
    with open("sor.txt", "wt") as destination:
        result = sorted(result, key=lambda entry: (entry[0].name, entry[1].name, entry[3]))
        for v1, v2, weight, repeat_name, multicolor in result:
            for color in multicolor.colors:
                print(v1.name, v2.name, color.name, "+" + repeat_name, weight, file=destination )
