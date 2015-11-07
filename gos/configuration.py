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
        io_silent_fail: .-> io_silent_fail                # -- if any part of an algorithm performs io operation, this flag determines what
                                                          #    to do if an IO exception is thrown
        logger: .->logger                                 # --
        tasks:                                            # -- single processing entity specification
            paths: []                                     # -- unchangeable value is "./tasks". everything else specified will be appended
                                                          #    to "./tasks" directory. All *.py files are observed and all classes,
                                                          #    being subclasses of GOSTask will be processed and available for further usage
                                                          #################################################################################
        stages:                                           # -- section describing next level layer of processing entities "stages"
            - name: stage1                                # -- unique name of a stages, that it can be referenced by later.
              self_loop: false                            # -- flag determining if a stage must be executed again, after its first execution
                                                          #    is finished.
              tasks:                                      # -- ordered list of tasks that stage includes in itself and will execute
                - task1                                   # -- name based reference to previously specified task
                - task2                                   # --
            - name: stage2                                # --
              logger: algorithm->logger                   # -- logger can be specified uniquely for each stage.
              self_loop: true                             # --
              tasks:                                      # --
                - task2                                   # --
            - name: stage3                                # --
              path: path_to_*.py_file                     # -- if "path" value is specified, the stage is loaded from specified .py file and
                                                          #    its structure is retrieved from the class based attributes
                                                          #################################################################################
        rounds:                                           # -- section describing next level layer of processing entities "rounds"
            - name: round1                                # -- unique name of a round, that can be referenced later
              self_loop: false                            # -- flag determining if a round must be executed again, after its first execution
                                                          #    is finished.
              logger: algorithm->logger                   # -- logger can be specified uniquely for each stage.
              stages:                                     # -- ordered list of stages that round includes in itself and will execute
                - stage1                                  # --
                - stage2                                  # --
            - name: round2                                # --
              path: path_to_*.py_file                     # -- if "path" value is specified, the round is loaded from specified .py file and
                                                          #    its structure is retrieved from the class based attributes
                                                          #################################################################################
        pipeline:                                         # -- top level procession entity
            logger: algorithm->logger                     # --
            self_loop: false                              # --
            rounds:                                       # -- ordered list of rounds that pipeline includes in itself and will execute
                - round1                                  # --
                - round2                                  # --
                - round1                                  # --
    """
    pass