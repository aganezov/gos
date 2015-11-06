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
    """
    pass