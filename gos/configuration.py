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

    algorithm:
        logger: .->logger
        tasks:                                            # single processing entity
            paths: []                                     # unchangeable value is "./tasks",
                                                          # everything else specified will be appended to "./tasks" directory
            ...
        stages:
            - name: stage1      # must be unique among stages
              self_loop: false
              tasks:
                - task1
                - task2
            - name: stage2
              logger: algorithm->logger
              self_loop: true
              tasks:
                - task2
            - name: stage3
              path: path_to_*.py_file                      # if path is specified, the stage is loaded from specified file and
                                                           # its predefined data is used for initialization
        rounds:
            - name: round1
              self_loop: false
              logger: algorithm->logger
              stages:
                - stage1
                - stage2
            - name: round2
              path: path_to_*.py_file

        pipeline:
            logger: algorithm->logger
            self_loop: false
            rounds:
                - round1
                - round2
                - round1
    """
    pass