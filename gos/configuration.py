# -*- coding: utf-8 -*-

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"


class Configuration(dict):
    """
    Structure, not yaml, just similar looking. It is just a description.

    input:
        source:
            - path: file1_path
              format: grimm
              io_silent_fail: input->io_silent_fail
            - path: file2_path
            - path: file3_path
        io_silent_fail: .->io_silent_fail
        logger: .->logger
        genomes:                                          # if specified, a check performed to make sure data about all
                                                          # genomes if present. If not -- retrieved form source files
            - name: genome1_name
            - name: genome2_name
            - name: genome3_name



    output:
        dir: .->dir + output/                             # -- directory for all output files to be put. Used for further paths construction
        logger: .->logger                                 # -- logger specification tp be utilized in the output section
        io_silent_fail: .->io_silent_fail                 # -- output section wide setting to fail or not when an exception
                                                          #    has occurred during the source file processing. Can be overwritten
                                                          #    by output section specific variable
                                                          #################################################################################
        stats:                                            # -- output section which handles all the statistics output for current
                                                          #    scaffolder execution
            dir: output->dir + stats/                     # -- directory where statistics files will be located
            file: stats.txt                               # -- default file name for the overall statistics file
            logger: output->logger                        #
            io_silent_fail: output->io_silent_fail        #
                                                          #################################################################################
        assembly_points:                                  # -- output section which handles all the information output about assembly
                                                          #    points during scaffolder run
            dir: output->dir + assembly_points/           # -- directory where assembly points file will be located
            file: assembly_points.txt                     # -- default name for the overall statistic
            logger: output->logger                        #
            io_silent_fail: output->io_silent_fail        #
            genome_specific: true                         # -- when specified, besides the overall file with all assembly points for current
                                                          #    scaffolder run, also "per-genome" files are created, that duplicate genome
                                                          #    specific results
                                                          #################################################################################
            genome_specific_file_name_pattern: assembly_points_{genome_name}.txt    # pattern for genome_specific file name creation
                                                          #################################################################################
                                                          #################################################################################
        genomes:                                          # -- output section where information about genomes fragments will be stored
            dir: output->dir + genomes/                   # -- directory where all genomes will ba located
            output_non_glued_fragments: false             # -- if specified, all input information about genomes will be outputted,
                                                          #    if set to false, only those fragments, that we involved in at least one
                                                          #    gluing will be present in the output
            logger: output->logger                        #
            io_silent_fail: output->io_silent_fail        #
    """
    pass