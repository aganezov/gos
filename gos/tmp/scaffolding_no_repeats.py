#! /usr/bin/env python
# -*- coding: utf-8 -*-
from copy import deepcopy
from bg import Multicolor, KBreak, BreakpointGraph, GRIMMReader, NewickReader, BGGenome
import itertools
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

def get_support_edge_scores(graph, subnet, target_multicolor, tree, verbose=False, verbose_destination=None):
    """
    For supplied connected components (this connected components is assumed to be pre-filtered before hand)
     for every regular edge in it (which after pre-filtration would correspond to "supporting" edge only)
     computes an summands ("before" and "after") for its "assembly score" (which is defined as "before" - "after")
     where "before" is a score for a pair of irregular edges under observation and their support
        (every support edge corresponds to a pair of irregular edges), as if assembly DID NOT happened
     where "after" is a score for a pair of irregular edges under observation and their support
        (every support edge corresponds to a pair of irregular edges), as if assembly DID happened
    """
    result = []
    # we iterate over all regular edges in pre-filtered connected component,
    # as all of them correspond to possible assembly points
    if verbose:
        print(">Getting support edge scores", file=verbose_destination)
    for edge in filter(lambda e: not e.is_irregular_edge, subnet.edges()):
        ex_data = {}
        if verbose:
            print("Possible assembly point", edge.vertex1.name, edge.vertex2.name,
                  [color.name for color in edge.multicolor.multicolors.elements()], file=verbose_destination)

        # basic references to most important parts of the observed possible assembly point
        v1, v2 = edge.vertex1, edge.vertex2
        sedge, iedge1, iedge2 = edge, None, None

        # since each vertex has at most 1 irregular edge incident to it, we can safely retrieve
        #   the first one for each vertex
        iedge1 = get_irregular_edge_by_vertex(subnet, v1)
        iedge2 = get_irregular_edge_by_vertex(subnet, v2)

        if verbose:
            print("irregular edge 1:", iedge1.vertex1.name, iedge1.vertex2.name,
                  [color.name for color in iedge1.multicolor.multicolors.elements()], file=verbose_destination)
            print("irregular edge 2:", iedge2.vertex1.name, iedge2.vertex2.name,
                  [color.name for color in iedge2.multicolor.multicolors.elements()], file=verbose_destination)

        # we need a full multicolor to determine which colors are missing (indels) on both vertices,
        #   that determine an assembly point
        full_multicolor = max(tree.consistent_multicolors, key=lambda multicolor: len(list(multicolor.multicolors.elements())))
        full_multicolor = Multicolor(*full_multicolor.colors)

        # we accumulated multicolors for both vertices,
        #   that are present in all edges combined, that are incident to them
        # we need to retrieve that information from the original whole graph, and not from the filtered one
        surrounding1 = Multicolor(*get_vertex_surrounding_multicolor(graph, v1).colors)
        surrounding2 = Multicolor(*get_vertex_surrounding_multicolor(graph, v2).colors)

        # we compute complementary multicolors for each vertex
        #   (multicolors, that are not present in edges, that are incident to respective vertices)
        c_1_multicolor = full_multicolor - surrounding1
        c_2_multicolor = full_multicolor - surrounding2

        # their intersection correspond to multicolors, that are not present at both vertices
        c = c_1_multicolor.intersect(c_2_multicolor)

        # and these colors correspond to colors, that are lacking uniquely at each vertex
        c_a = c_1_multicolor - c
        c_b = c_2_multicolor - c

        # a list of tree consistent multicolors, that are used to split any given multicolor into a smallest set of
        #   T-consistent multicolors
        guidance = tree.consistent_multicolors

        if verbose:
            print("\tfull multicolor:", [color.name for color in full_multicolor.multicolors.elements()],
                  file=verbose_destination)
            print("\ts1 multicolor:", [color.name for color in surrounding1.multicolors.elements()],
                  file=verbose_destination)
            print("\ts2 multicolor:", [color.name for color in surrounding2.multicolors.elements()],
                  file=verbose_destination)
            print("\tc_1 multicolor:", [color.name for color in c_1_multicolor.multicolors.elements()],
                  file=verbose_destination)
            print("\tc_2 multicolor:", [color.name for color in c_2_multicolor.multicolors.elements()],
                  file=verbose_destination)
            print("\tc multicolor:", [color.name for color in c.multicolors.elements()],
                  file=verbose_destination)
            print("\tc_a multicolor:", [color.name for color in c_a.multicolors.elements()],
                  file=verbose_destination)
            print("\tc_b multicolor:", [color.name for color in c_b.multicolors.elements()],
                  file=verbose_destination)

        # we compute summands for the "before" score for respective three edges
        # we add lacking colors to the edges multicolors during this computation

        ###################################################
        # we don't account for multiplicity in guidance, as in guidance we have each colors present exactly once,
        # as it is when no information about whole genome duplication is available,
        # but since there might be duplications in the multicolors on the edges, we would like to interpret
        # those multicolors as multicolors, where each present colors has multiplicity 1
        ###################################################
        ie1_score = len(Multicolor.split_colors(Multicolor(*iedge1.multicolor.colors) + c_a, guidance=guidance,
                                                account_for_color_multiplicity_in_guidance=False))
        ie2_score = len(Multicolor.split_colors(Multicolor(*iedge2.multicolor.colors) + c_b, guidance=guidance,
                                                account_for_color_multiplicity_in_guidance=False))
        s_multicolor = (Multicolor(*sedge.multicolor.colors))
        ex_data["s_support"] = sorted(sorted([color.name for color in target_multicolor.intersect(s_multicolor).colors]))
        if target_multicolor <= s_multicolor:
            s_multicolor -= target_multicolor
        se_score = len(Multicolor.split_colors(s_multicolor + c, guidance=guidance,
                                               account_for_color_multiplicity_in_guidance=False))
        before = ie1_score + ie2_score + se_score

        if verbose:
            print("score before: iedge1 score =", ie1_score,
                  "iedge2 score =", ie2_score,
                  "support edge score =", se_score,
                  "\"before\" score =", before,
                  file=verbose_destination)

        # we compute summands for the "after" score for respective three edges, as if the assembly was performed
        # we add lacking colors to the edges multicolors during this computation

        ###################################################
        # we don't account for multiplicity in guidance, as in guidance we have each colors present exactly once,
        # as it is when no information about whole genome duplication is available,
        # but since there might be duplications in the multicolors on the edges, we would like to interpret
        # those multicolors as multicolors, where each present colors has multiplicity 1
        ###################################################
        new_ie1_score = len(Multicolor.split_colors(Multicolor(*iedge1.multicolor.colors) - target_multicolor + c_a, guidance=guidance,
                                                    account_for_color_multiplicity_in_guidance=False))
        new_ie2_score = len(Multicolor.split_colors(Multicolor(*iedge2.multicolor.colors) - target_multicolor + c_b, guidance=guidance,
                                                    account_for_color_multiplicity_in_guidance=False))
        new_se_score = len(Multicolor.split_colors(s_multicolor + target_multicolor + c, guidance=guidance,
                                                   account_for_color_multiplicity_in_guidance=False))

        after = new_ie1_score + new_ie2_score + new_se_score

        if verbose:
            print("score after: iedge1 score =", new_ie1_score,
                  "iedge2 score =", new_ie2_score,
                  "support edge score =", new_se_score,
                  "\"after\" score =", after)

        result.append(((v1, v2), before, after, ex_data))

    # we return result as a list of tuples, where each tuple contains information about a pair of vertices
    #   (possible assembly point), and "before" and "after" score for this possible assembly point
    return result


def get_irregular_subnets(cc, target_multicolor, exclude, verbose=False, verbose_destination=None):
    """
    For a supplied connected component (which is assumed to be a deepcopy from an original breakpoint graph)
    we filter out all edges, that are of no interest for the scaffolding purposes with current target multicolor:
        1. target multicolor must be fully present in the irregular edge
        2. all colors from the target multicolor must be present exactly once in irregular edge multicolor
        3. no colors from the "exclude" set must be present in the irregular edge multicolor
        4. regular edge must "support" two irregular edges, that have survived the filtration specified above
    """
    to_remove = []

    if verbose:
        print(">Getting irregular subnets", file=verbose_destination)
        print("Graph contains", len(list(cc.edges())), "edges", file=verbose_destination)
        print("Removing uninteresting irregular edges", file=verbose_destination)

    ####################################################################################################
    # we work with a supplied connected components,
    #   assuming that its a deepcopy of the connected components in the original graph
    # so we can do with it whatever we want, without affecting data in the original graph
    ####################################################################################################
    for bgedge, key in cc.edges(keys=True):
        ####################################################################################################
        # infinity edges must fully contain target multicolor
        ####################################################################################################
        if bgedge.is_irregular_edge and not target_multicolor <= bgedge.multicolor:
            if verbose:
                print("  removing", bgedge.vertex1.name, "--", bgedge.vertex2.name,
                      [color.name for color in bgedge.multicolor.multicolors.elements()], ": no target multicolor",
                      file=verbose_destination)
            to_remove.append((bgedge, key))
            continue
        ####################################################################################################
        # infinity edges must not contain colors from the excluded group
        ####################################################################################################
        if bgedge.is_irregular_edge and any(map(lambda color: color in bgedge.multicolor.colors, exclude)):
            if verbose:
                print("  removing", bgedge.vertex1.name, "--", bgedge.vertex2.name,
                      [color.name for color in bgedge.multicolor.multicolors.elements()],
                      ": contains exclude multicolor", file=verbose_destination)
            to_remove.append((bgedge, key))
            continue
        ####################################################################################################
        # in infinity edge multicolor all colors from targetted multicolor must have multiplicity one
        ####################################################################################################
        if bgedge.is_irregular_edge and any(map(lambda color: bgedge.multicolor.multicolors[color] > 1, target_multicolor.colors)):
            if verbose:
                print("  removing", bgedge.vertex1.name, "--", bgedge.vertex2.name,
                      [color.name for color in bgedge.multicolor.multicolors.elements()],
                      ": multicplicity of some target multicolor os greater than 1", file=verbose_destination)
            to_remove.append((bgedge, key))
            continue
            ####################################################################################################

    ##########################################################################################################
    # once we've gathered all uninteresting / ambiguous (from target multicolor scaffolding stand point) irregular edges
    #   we remove them
    ##########################################################################################################
    for bgedge, key in to_remove:
        cc.delete_bgedge(bgedge, key)
    if verbose:
        print("Graph contains", len(list(cc.edges())), "edges", file=verbose_destination)

    to_remove = []
    ################################################################################
    # after we have left only those infinity edges are of interesting for the scaffolding purposses
    # we filter regular edges to leave only those, that are supporting these infinity edges
    ################################################################################
    if verbose:
        print("Removing uninteresting regular edges", file=verbose_destination)
    for bgedge, key in cc.edges(keys=True):
        ################################################################################
        # we only need edges that are either infinity edges, that were left during the presious step
        # or support edges (have infinity edges at both vertices, that they are incident to)
        ################################################################################
        if not bgedge.is_irregular_edge and not supports_a_pair_of_irregular_edges(cc, bgedge):
            if verbose:
                print("  removing", bgedge.vertex1.name, "--", bgedge.vertex2.name,
                      [color.name for color in bgedge.multicolor.multicolors.elements()],
                      ": does not support any irregular edge", file=verbose_destination)
            to_remove.append((bgedge, key))

    ##########################################################################################################
    # once we've gathered all regular edges, that do not support pairs of interesting (from scaffolding stand point)
    #   irregular edges
    ##########################################################################################################
    for bgedge, key in to_remove:
        cc.delete_bgedge(bgedge, key)
    if verbose:
        print("Graph contains", len(list(cc.edges())), "edges", file=verbose_destination)

    ##########################################################################################################
    # once we've deleted all the uninteresting for scaffolding purposes infinity and regular edges,
    #   our connected component
    # is being torn apart into multiple connected components, each of which we can process independently
    # and which contain only edges of interest for us
    ##########################################################################################################
    result = []
    for cc in cc.connected_components_subgraphs(copy=False):
        if len(list(cc.edges())) > 0:
            result.append(cc)
    return result


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

    threshold = 1 if offset == 0 else 2
    assemblies = []  # the overall result
    if exclude is None:
        exclude = []  # a container with single colors of genomes, that are to be considered fully assembled

    p_t_consistent_multicolors_in_target = Multicolor.split_colors(target_multicolor, guidance=guidance,
                                                                   account_for_color_multiplicity_in_guidance=False)
    t_consistent_multicolors_in_target = []
    for tcmc in p_t_consistent_multicolors_in_target:
        t_consistent_multicolors_in_target.append(sorted(color.name for color in tcmc.colors))
    # we work with each connected component separately, as connected components usually preserve fragmentation points
    ################################################################################################
    #
    # its important that we iterate over connected components making each particular one a deepcopy of an
    #   underlying breakpoint graph connected component
    #
    ################################################################################################
    for i, cc in enumerate(graph.connected_components_subgraphs(copy=True)):

        # we filter current connected component of uninteresting / ambiguous edges and retrieve a list of
        #   connected components that are left in the original connected components after filtration
        irregular_subnets = get_irregular_subnets(cc, target_multicolor, exclude)

        if len(irregular_subnets) > 0 and verbose:
            print(">>Processing", str(i) + "th", "connected component", file=verbose_destination)
            print("\tcontains", len(irregular_subnets), "subnet groups", file=verbose_destination)

        # each subnet can be processed separately
        for subnet in irregular_subnets:

            supporting_edge_scores = get_support_edge_scores(graph, subnet, target_multicolor, bgtree)

            # we create a new dummy graph for the purpose of computing maximum weight matching for support edges in it
            new_graph = nx.Graph()
            if verbose:
                print("\tcontains", len(supporting_edge_scores), "possible assembly points", file=verbose_destination)

            # we'll keep track of possible assembly points for future reference
            support_edge_dict = {}
            for (v1, v2), before, after, ex_data in supporting_edge_scores:
                ex_data["tcmc"] = t_consistent_multicolors_in_target
                ##########################################################################################
                #
                # INSERT YOUR CODE ASSEMBLY SCORE THRESHOLD FILTRATION HERE IF NEED BE
                #
                ##########################################################################################
                if before - after - offset < threshold:
                    continue
                ##########################################################################################
                #
                # by default networkx assumes all edges, that have weight >= 0 are good
                #
                ##########################################################################################
                new_graph.add_edge(v1, v2, weight=before - after - offset)
                support_edge_dict[(v1, v2)] = (before, after + offset, ex_data)
                support_edge_dict[(v2, v1)] = (before, after + offset, ex_data)

            maximal_matching = nx.max_weight_matching(new_graph)

            if verbose:
                print("\t", len(maximal_matching) // 2, "assembly points are identified", file=verbose_destination)

            # as networkx provides a maximum matching in a form of adjacency list, every identified edge
            #   (pair of vertices) is present their twice (i.e. matching[v1]=v2 and matching[v2]=v1)
            #   we need to make sure we only add every edge only once
            visited = set()
            for v1, v2 in maximal_matching.items():
                if v1 in visited or v2 in visited:
                    continue
                visited.add(v1)
                visited.add(v2)
                assemblies.append((v1, v2, support_edge_dict[(v1, v2)]))

    # we return the result as a list of assembly points that were identified for the targeted multicolor
    # as a list of tuples (v1, v2, ("before", "after"))
    # where v1 and v2 correspond to assembly point and "before" and "after" are used to compute the assembly score
    return assemblies


def assemble_points(graph, assemblies, multicolor, verbose=False, verbose_destination=None):
    """
    This function actually does assembling being provided
        a graph, to play with
        a list of assembly points
        and a multicolor, which to assemble
    """
    if verbose:
        print(">>Assembling for multicolor", [e.name for e in multicolor.multicolors.elements()],
              file=verbose_destination)
    for assembly in assemblies:
        v1, v2, (before, after, ex_data) = assembly
        iv1 = get_irregular_vertex(get_irregular_edge_by_vertex(graph, vertex=v1))
        iv2 = get_irregular_vertex(get_irregular_edge_by_vertex(graph, vertex=v2))
        kbreak = KBreak(start_edges=[(v1, iv1), (v2, iv2)],
                        result_edges=[(v1, v2), (iv1, iv2)],
                        multicolor=multicolor)
        if verbose:
            print("(", v1.name, ",", iv1.name, ")x(", v2.name, ",", iv2.name, ")", " score=", before - after, sep="",
                  file=verbose_destination)
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
            if tree_c_multicolor <= target_multicolor \
                    and tree_c_multicolor not in tree_consistent_target_multicolors \
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
              len(all_target_multicolors), file=verbose_destination)
        for multicolor in all_target_multicolors:
            print("\t", [color.name for color in multicolor.multicolors.elements()], file=verbose_destination)
    for i, multicolor in enumerate(all_target_multicolors):
        print("working with multicolor", i)
        assembly_points = identify_assembly_points(graph, bgtree, target_multicolor=multicolor, exclude=exclude,
                                                   verbose_destination=verbose_destination)
        for v1, v2, (before, after, ex_data) in assembly_points:
            overall_assembling_result.append((v1, v2, (before, after, ex_data), multicolor))
        assemble_points(graph, assemblies=assembly_points, multicolor=multicolor,
                        verbose_destination=verbose_destination)
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

DATA_SOURCE_ROOT_DIR = "/volumes/data/projects/2015"
DATA_SOURCE_REL_DIR = "plants/data"

DATA_TEST_CASE = "grimm"

FULL_SOURCE_DIR = os.path.join(DATA_SOURCE_ROOT_DIR, DATA_SOURCE_REL_DIR, DATA_TEST_CASE)

SOURCE_GRIMM_FILES = [os.path.join(FULL_SOURCE_DIR, file) for file in os.listdir(FULL_SOURCE_DIR) if file.endswith(".grimm")]

GRIMM_FILES = SOURCE_GRIMM_FILES
F_NEWICK_STRING_TREE = "((((((fugu,Stickleback),Medaka),Tetraodon),zebra_fish),Coelacanth),Anguilla_japonica);"
NEWICK_STRING_TREE = "(vvi,(ptr,(egr,(cpa,(tpa,(cru,(ath,aly)))))));"
F_TARGET_ORGANISM_NAMES = ["Anguilla_japonica", "Coelacanth", "fugu", "Medaka"]
TARGET_ORGANISM_NAMES = ["aly", "tpa"]
COMPLETE_ORGANISM_NAMES = ["vvi", "ath"]
F_COMPLETE_ORGANISM_NAMES = ["Stickleback", "Tetraodon"]

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
    print("Were identified", sum([len(multicolor.colors) for _, _, (_, _, ex_data), multicolor in result]), "assembly points")

    with open("assemblies.txt", "wt") as destination:
        for v1, v2, (before, after, ex_data), multicolor in result:
            for color in multicolor.colors:
                print(color.name, before - after, v1.name, v2.name, ex_data["s_support"], ex_data["tcmc"])

