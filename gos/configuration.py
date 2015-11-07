# -*- coding: utf-8 -*-

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"


class Configuration(dict):
    """
    Structure, not yaml, just similar looking. It is just a description.

    dir: ./                                               # -- directory, that is used further for creation of relative subdirectories
                                                          #    current working directory by default
    logger:                                               #
        name: GOSLogger                                   #
        level: info                                       #  -- by default only info messages are shown
                                                          #
        format: %(asctime)s - %(name)s - %(levelname)s - %(message)s  #
                                                          #
        destination: sys.stdout                           # -- by default all logging messages are shown to the standard output
                                                          #
    io_silent_fail: false                                 # -- by default if any IO exception happens, program will terminate
                                                          ########################################################################
                                                          ########################################################################
    input:                                                #
        source:                                           #
            - path: file1_path                            # -- relative (to input->dir) path to file with genome data
              format: grimm                               # -- determines which reader is going ot process the source file
                                                          #    if not specified, automatically retrieved from file extension
              io_silent_fail: input->io_silent_fail       # -- whether to fail or not if exception has occurred during data reading
                                                          #    file specific. defaults to input io_silent_fail setting.
                                                          ########################################################################
            - path: file2_path                            #
            - path: file3_path                            #
        dir: .->dir + /input                              # -- a directory to search for source files in. / by default
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
            - name: genome2_name                          #
            - name: genome3_name                          #
                                                          ########################################################################
    algorithm:                                            ########################################################################
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
                                                          ########################################################################
    output:                                               ########################################################################
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
        genomes:                                          # -- output section where information about genomes fragments will be stored
            dir: output->dir + genomes/                   # -- directory where all genomes will ba located
            output_non_glued_fragments: false             # -- if specified, all input information about genomes will be outputted,
                                                          #    if set to false, only those fragments, that we involved in at least one
                                                          #    gluing will be present in the output
            logger: output->logger                        #
            io_silent_fail: output->io_silent_fail        #
    """
    pass