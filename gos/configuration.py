# -*- coding: utf-8 -*-

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"


class Configuration(dict):
    """
    Structure, not yaml, just similar looking. It is just a description.

    input:
        source:
            - path: file1_path                            # -- relative (to input->dir) path to file with genome data
              format: grimm                               # -- determines which reader is going ot process the source file
                                                          #    if not specified, automatically retrieved from file extension
              io_silent_fail: input->io_silent_fail       # -- whether to fail or not if exception has occurred during data reading
                                                          #    file specific. defaults to input io_silent_fail setting.
                                                          ########################################################################
            - path: file2_path
            - path: file3_path
        dir: /                                            # -- a directory to search for source files in. / by default
                                                          ########################################################################
        io_silent_fail: .->io_silent_fail                 # -- input section wide setting whether to fail or not, when an exception
                                                          #    has occurred during the source file processing. Can be overwritten
                                                          #    by source file specific variable
                                                          ########################################################################
        logger: .->logger                                 # -- a logger specification to be utilized for the input section of the
                                                          #
        genomes:                                          # -- if specified, a check performed to make sure data about all
                                                          #    genomes if present. If not -- retrieved form source files
            - name: genome1_name                          # -- primary genome name.
                                                          #    must be unique among all observed genomes (specified and retrieved)
              aliases: [alias1, alias2, alias3]           # -- other genome names, to be identified by. must be unique per genome
                                                          ########################################################################
            - name: genome2_name
            - name: genome3_name
    """
    pass